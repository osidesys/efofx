import { db } from '../../../lib/db.js';
import { verifyHmac, extractTenantId } from '../../../lib/auth.js';
import { validateInput, referenceClassQuerySchema } from '../../../lib/schemas.js';
import { logRequest, logResponse, logError, createRequestLogger } from '../../../lib/log.js';

export async function main(event) {
  const traceId = event.trace_id || `query-${Date.now()}`;
  const log = createRequestLogger(traceId, 'unknown');
  
  try {
    // Verify HMAC authentication
    const auth = verifyHmac({ event, secretBase64: process.env.HMAC_SECRET_B64 });
    if (!auth.ok) {
      log.warn({ tool: 'reference_classes.query', reason: auth.reason });
      return { 
        statusCode: 401, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'unauthorized', reason: auth.reason } 
      };
    }

    // Extract and validate tenant ID
    const tenantId = extractTenantId(event);
    if (!tenantId) {
      log.warn({ tool: 'reference_classes.query', reason: 'missing_tenant_id' });
      return { 
        statusCode: 400, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'invalid_input', field: 'tenant_id' } 
      };
    }

    // Update logger with tenant ID
    const tenantLog = createRequestLogger(traceId, tenantId);
    logRequest(event, tenantId, 'reference_classes.query');

    // Validate input schema
    const validation = validateInput(referenceClassQuerySchema, {
      attributes: event.attributes || event.body?.attributes,
      options: event.options || event.body?.options,
      tenant_id: tenantId
    });

    if (!validation.ok) {
      tenantLog.warn({ 
        tool: 'reference_classes.query', 
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

    const { attributes = {}, options = {} } = validation.data;

    // Build MongoDB query
    const match = Object.fromEntries(
      ['tenant_id', 'category', 'subcategory', 'region', 'scope', 'scale']
        .map(k => [k, k === 'tenant_id' ? tenantId : attributes[k]])
        .filter(([, v]) => v != null)
    );

    // Query database
    const collection = (await db()).collection('reference_classes');
    const doc = await collection.findOne(match, {
      projection: { 
        _id: 0, 
        id: 1, 
        name: 1, 
        distribution_version: 1, 
        cost_distribution: 1, 
        time_distribution: 1, 
        cost_breakdown: 1, 
        citations: 1 
      }
    });

    if (!doc) {
      tenantLog.info({ 
        tool: 'reference_classes.query', 
        message: 'No reference class found',
        match 
      });
      logResponse(traceId, tenantId, 'reference_classes.query', 404);
      return { 
        statusCode: 404, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'not_found', trace_id: traceId } 
      };
    }

    tenantLog.info({ 
      tool: 'reference_classes.query', 
      message: 'Reference class found',
      rc_id: doc.id 
    });

    logResponse(traceId, tenantId, 'reference_classes.query', 200, doc.id);
    return { 
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: doc 
    };

  } catch (error) {
    logError(traceId, 'unknown', 'reference_classes.query', error);
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
