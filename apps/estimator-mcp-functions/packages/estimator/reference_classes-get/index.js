import { db } from '../../../lib/db.js';
import { verifyHmac, extractTenantId } from '../../../lib/auth.js';
import { logRequest, logResponse, logError, createRequestLogger } from '../../../lib/log.js';

export async function main(event) {
  const traceId = event.trace_id || `get-${Date.now()}`;
  const log = createRequestLogger(traceId, 'unknown');
  
  try {
    // Verify HMAC authentication
    const auth = verifyHmac({ event, secretBase64: process.env.HMAC_SECRET_B64 });
    if (!auth.ok) {
      log.warn({ tool: 'reference_classes.get', reason: auth.reason });
      return { 
        statusCode: 401, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'unauthorized', reason: auth.reason } 
      };
    }

    // Extract and validate tenant ID
    const tenantId = extractTenantId(event);
    if (!tenantId) {
      log.warn({ tool: 'reference_classes.get', reason: 'missing_tenant_id' });
      return { 
        statusCode: 400, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'invalid_input', field: 'tenant_id' } 
      };
    }

    // Extract reference class ID from path parameters or body
    const rcId = event.id || event.body?.id || event.http?.path?.split('/').pop();
    if (!rcId) {
      log.warn({ tool: 'reference_classes.get', reason: 'missing_rc_id' });
      return { 
        statusCode: 400, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'invalid_input', field: 'id' } 
      };
    }

    // Update logger with tenant ID
    const tenantLog = createRequestLogger(traceId, tenantId);
    logRequest(event, tenantId, 'reference_classes.get');

    // Query database by ID and tenant
    const collection = (await db()).collection('reference_classes');
    const doc = await collection.findOne(
      { id: rcId, tenant_id: tenantId },
      {
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
      }
    );

    if (!doc) {
      tenantLog.info({ 
        tool: 'reference_classes.get', 
        message: 'Reference class not found',
        rc_id: rcId 
      });
      logResponse(traceId, tenantId, 'reference_classes.get', 404);
      return { 
        statusCode: 404, 
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'not_found', trace_id: traceId } 
      };
    }

    tenantLog.info({ 
      tool: 'reference_classes.get', 
      message: 'Reference class retrieved',
      rc_id: doc.id 
    });

    logResponse(traceId, tenantId, 'reference_classes.get', 200, doc.id);
    return { 
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: doc 
    };

  } catch (error) {
    logError(traceId, 'unknown', 'reference_classes.get', error);
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
