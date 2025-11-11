import { describe, it, expect, beforeEach } from 'vitest';
import { verifyHmac, extractTenantId } from './auth.js';

describe('Auth Module', () => {
  let mockEvent;
  let mockSecret;

  beforeEach(() => {
    mockSecret = Buffer.from('test-secret-key').toString('base64');
    mockEvent = {
      http: {
        method: 'POST',
        path: '/test',
        headers: {
          'x-efofx-key-id': 'test-key',
          'x-efofx-timestamp': Math.floor(Date.now() / 1000).toString(),
          'x-efofx-nonce': 'test-nonce-123',
          'x-efofx-signature': 'dummy-signature'
        }
      },
      body: { test: 'data' }
    };
  });

  describe('extractTenantId', () => {
    it('should extract tenant_id from event body', () => {
      const event = { body: { tenant_id: 'acme-co' } };
      expect(extractTenantId(event)).toBe('acme-co');
    });

    it('should extract tenant_id from top level', () => {
      const event = { tenant_id: 'acme-co' };
      expect(extractTenantId(event)).toBe('acme-co');
    });

    it('should return undefined when tenant_id is missing', () => {
      const event = { body: { other: 'data' } };
      expect(extractTenantId(event)).toBeUndefined();
    });
  });

  describe('verifyHmac', () => {
    it('should return missing_headers when required headers are missing', () => {
      const event = { http: { headers: {} } };
      const result = verifyHmac({ event, secretBase64: mockSecret });
      expect(result.ok).toBe(false);
      expect(result.reason).toBe('missing_headers');
    });

    it('should return timestamp_skew when timestamp is too old', () => {
      const oldTimestamp = Math.floor((Date.now() / 1000) - 300).toString();
      mockEvent.http.headers['x-efofx-timestamp'] = oldTimestamp;
      
      const result = verifyHmac({ event: mockEvent, secretBase64: mockSecret });
      expect(result.ok).toBe(false);
      expect(result.reason).toBe('timestamp_skew');
    });
  });
});
