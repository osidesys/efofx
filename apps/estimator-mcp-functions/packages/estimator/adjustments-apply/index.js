import { db } from '../../../lib/db.js';
import { verifyHmac, extractTenantId } from '../../../lib/auth.js';
import { validateInput, adjustmentsApplySchema } from '../../../lib/schemas.js';
import { logRequest, logResponse, logError, createRequestLogger } from '../../../lib/log.js';

export async function main(event) {
  const traceId = event.trace_id || `adjust-${Date.now()}`;
  const log = createRequestLogger(traceId, 'unknown');
  
  try {
    // Verify HMAC authentication
    const auth = verifyHmac({ event, secretBase64: process.env.HMAC_SECRET_B64 });
    if (!auth.ok) {
      log.warn({ tool: 'adjustments.apply', reason: auth.reason });
      return { 
        statusCode: 401, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'unauthorized', reason: auth.reason } 
      };
    }

    // Extract and validate tenant ID
    const tenantId = extractTenantId(event);
    if (!tenantId) {
      log.warn({ tool: 'adjustments.apply', reason: 'missing_tenant_id' });
      return { 
        statusCode: 400, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'invalid_input', field: 'tenant_id' } 
      };
    }

    // Update logger with tenant ID
    const tenantLog = createRequestLogger(traceId, tenantId);
    logRequest(event, tenantId, 'adjustments.apply');

    // Validate input schema
    const validation = validateInput(adjustmentsApplySchema, {
      reference_class_id: event.reference_class_id || event.body?.reference_class_id,
      modifiers: event.modifiers || event.body?.modifiers,
      tenant_id: tenantId
    });

    if (!validation.ok) {
      tenantLog.warn({ 
        tool: 'adjustments.apply', 
        reason: 'validation_failed',
        errors: validation.errors 
      });
      return { 
        statusCode: 400, 
        headers: { 'Content-Type': 'application/json' },
        body: { 
          error: 'invalid_input', 
          details: validation.errors,
          trace_id: traceId
        } 
      };
    }

    const { reference_class_id, modifiers } = validation.data;

    // Get the reference class
    const collection = (await db()).collection('reference_classes');
    const rc = await collection.findOne(
      { id: reference_class_id, tenant_id: tenantId },
      { projection: { _id: 0, cost_distribution: 1, time_distribution: 1 } }
    );

    if (!rc) {
      tenantLog.warn({ 
        tool: 'adjustments.apply', 
        reason: 'reference_class_not_found',
        rc_id: reference_class_id 
      });
      return { 
        statusCode: 404, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'reference_class_not_found', trace_id: traceId } 
      };
    }

    // Get applicable modifiers for the tenant and region
    const modifiersCollection = (await db()).collection('modifiers');
    const applicableModifiers = await modifiersCollection.find({
      tenant_id: tenantId,
      effective_from: { $lte: new Date() },
      effective_to: { $gte: new Date() }
    }).toArray();

    // Apply modifiers to baseline estimates
    let adjustedCost = { ...rc.cost_distribution };
    let adjustedTime = { ...rc.time_distribution };

    for (const modifier of applicableModifiers) {
      if (modifier.labor_multiplier) {
        // Apply labor multiplier to cost (assuming labor is 55% of total)
        const laborCost = adjustedCost.P50 * 0.55;
        const adjustment = laborCost * (modifier.labor_multiplier - 1);
        adjustedCost.P50 = Math.round(adjustedCost.P50 + adjustment);
        adjustedCost.P80 = Math.round(adjustedCost.P80 + adjustment);
        adjustedCost.P95 = Math.round(adjustedCost.P95 + adjustment);
      }

      if (modifier.materials_multiplier) {
        // Apply materials multiplier to cost (assuming materials is 32% of total)
        const materialsCost = adjustedCost.P50 * 0.32;
        const adjustment = materialsCost * (modifier.materials_multiplier - 1);
        adjustedCost.P50 = Math.round(adjustedCost.P50 + adjustment);
        adjustedCost.P80 = Math.round(adjustedCost.P80 + adjustment);
        adjustedCost.P95 = Math.round(adjustedCost.P95 + adjustment);
      }

      if (modifier.volatility_index) {
        // Apply volatility adjustment to time estimates
        const volatilityMultiplier = 1 + modifier.volatility_index;
        adjustedTime.P50 = Math.round(adjustedTime.P50 * volatilityMultiplier);
        adjustedTime.P80 = Math.round(adjustedTime.P80 * volatilityMultiplier);
        adjustedTime.P95 = Math.round(adjustedTime.P95 * volatilityMultiplier);
      }
    }

    tenantLog.info({ 
      tool: 'adjustments.apply', 
      message: 'Adjustments applied successfully',
      rc_id: reference_class_id,
      modifiers_applied: applicableModifiers.length
    });

    logResponse(traceId, tenantId, 'adjustments.apply', 200, reference_class_id);
    return { 
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: {
        reference_class_id,
        original_cost: rc.cost_distribution,
        original_time: rc.time_distribution,
        adjusted_cost: adjustedCost,
        adjusted_time: adjustedTime,
        modifiers_applied: applicableModifiers.length
      }
    };

  } catch (error) {
    logError(traceId, 'unknown', 'adjustments.apply', error);
    return { 
      statusCode: 500, 
      headers: { 'Content-Type': 'application/json' },
      body: { 
        error: 'internal_server_error', 
        trace_id: traceId 
      } 
    };
  }
}
