import { logger, createRequestLogger } from '../../../lib/log.js';

export async function main(event) {
  const traceId = event.trace_id || `manifest-${Date.now()}`;
  const log = createRequestLogger(traceId, 'system');
  
  try {
    log.info({ tool: 'manifest', message: 'Serving MCP manifest' });
    
    return {
      statusCode: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=600'
      },
      body: {
        mcpServer: 'estimator-mcp',
        version: '1.0.0',
        tools: [
          { 
            name: 'reference_classes.query', 
            description: 'Find the best reference class based on attributes',
            inputSchema: {
              type: 'object',
              properties: {
                attributes: {
                  type: 'object',
                  properties: {
                    category: { type: 'string' },
                    subcategory: { type: 'string' },
                    region: { type: 'string' },
                    scope: { type: 'string' },
                    scale: { type: 'string' }
                  }
                },
                options: {
                  type: 'object',
                  properties: {
                    allow_partial: { type: 'boolean' }
                  }
                },
                tenant_id: { type: 'string' }
              },
              required: ['tenant_id']
            }
          },
          { 
            name: 'reference_classes.get', 
            description: 'Get reference class distributions by ID',
            inputSchema: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                tenant_id: { type: 'string' }
              },
              required: ['id', 'tenant_id']
            }
          },
          { 
            name: 'adjustments.apply', 
            description: 'Apply stored modifiers to a baseline estimate',
            inputSchema: {
              type: 'object',
              properties: {
                reference_class_id: { type: 'string' },
                modifiers: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      type: { 
                        type: 'string',
                        enum: ['labor_multiplier', 'materials_multiplier', 'volatility_index']
                      },
                      value: { type: 'number' }
                    },
                    required: ['type', 'value']
                  }
                },
                tenant_id: { type: 'string' }
              },
              required: ['reference_class_id', 'modifiers', 'tenant_id']
            }
          }
        ]
      }
    };
  } catch (error) {
    log.error({ tool: 'manifest', error: error.message });
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
