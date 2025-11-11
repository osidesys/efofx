import { z } from 'zod';

// Reference class query input schema
export const referenceClassQuerySchema = z.object({
  attributes: z.object({
    category: z.string().optional(),
    subcategory: z.string().optional(),
    region: z.string().optional(),
    scope: z.string().optional(),
    scale: z.string().optional()
  }).optional(),
  options: z.object({
    allow_partial: z.boolean().optional()
  }).optional(),
  tenant_id: z.string()
});

// Reference class response schema
export const referenceClassResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  distribution_version: z.number(),
  cost_distribution: z.object({
    P50: z.number(),
    P80: z.number(),
    P95: z.number()
  }),
  time_distribution: z.object({
    P50: z.number(),
    P80: z.number(),
    P95: z.number()
  }),
  cost_breakdown: z.object({
    labor: z.number(),
    materials: z.number(),
    permits: z.number(),
    overhead: z.number()
  }),
  citations: z.array(z.string())
});

// Adjustments apply input schema
export const adjustmentsApplySchema = z.object({
  reference_class_id: z.string(),
  modifiers: z.array(z.object({
    type: z.enum(['labor_multiplier', 'materials_multiplier', 'volatility_index']),
    value: z.number()
  })),
  tenant_id: z.string()
});

// Error response schema
export const errorResponseSchema = z.object({
  error: z.string(),
  reason: z.string().optional(),
  field: z.string().optional(),
  trace_id: z.string().optional()
});

// Validation helper
export function validateInput(schema, data) {
  try {
    return { ok: true, data: schema.parse(data) };
  } catch (error) {
    return { ok: false, errors: error.errors };
  }
}
