import pino from 'pino';

const logLevel = process.env.LOG_LEVEL || 'info';

export const logger = pino({
  level: logLevel,
  formatters: {
    level: (label) => ({ level: label }),
    log: (object) => object
  },
  timestamp: pino.stdTimeFunctions.isoTime
});

export function createRequestLogger(traceId, tenantId) {
  return logger.child({
    trace_id: traceId,
    tenant_id: tenantId
  });
}

export function logRequest(req, tenantId, tool) {
  logger.info({
    trace_id: req.trace_id || 'unknown',
    tenant_id: tenantId,
    tool,
    method: req.http?.method,
    path: req.http?.path,
    user_agent: req.http?.headers?.['user-agent']
  });
}

export function logResponse(traceId, tenantId, tool, status, rcId = null) {
  logger.info({
    trace_id: traceId,
    tenant_id: tenantId,
    tool,
    status,
    rc_id: rcId
  });
}

export function logError(traceId, tenantId, tool, error, context = {}) {
  logger.error({
    trace_id: traceId,
    tenant_id: tenantId,
    tool,
    error: error.message,
    stack: error.stack,
    ...context
  });
}
