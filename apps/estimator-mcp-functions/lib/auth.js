import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';

export function verifyHmac({ event, secretBase64 }) {
  const hdr = (name) => event.http?.headers?.[name] || event[name];
  const keyId = hdr('x-efofx-key-id');
  const ts = hdr('x-efofx-timestamp');
  const nonce = hdr('x-efofx-nonce');
  const sig = hdr('x-efofx-signature');

  if (!keyId || !ts || !nonce || !sig) {
    return { ok: false, reason: 'missing_headers' };
  }

  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - Number(ts)) > 120) {
    return { ok: false, reason: 'timestamp_skew' };
  }

  const body = JSON.stringify(event.body ?? event);
  const method = event.http?.method || 'POST';
  const path = event.http?.path || '';

  const msg = [method.toUpperCase(), path, body, ts, nonce].join('|');
  const key = Buffer.from(secretBase64, 'base64');
  const calc = crypto.createHmac('sha256', key).update(msg).digest('base64');

  const ok = crypto.timingSafeEqual(Buffer.from(calc), Buffer.from(sig));
  return ok ? { ok: true, keyId } : { ok: false, reason: 'bad_signature' };
}

export function verifyJwt(token, publicKeyPem) {
  try {
    const decoded = jwt.verify(token, publicKeyPem, {
      algorithms: ['RS256'],
      audience: 'efofx-mcp',
      issuer: process.env.JWT_ISSUER || 'efofx-monolith'
    });
    return { ok: true, claims: decoded };
  } catch (error) {
    return { ok: false, reason: error.message };
  }
}

export function extractTenantId(event) {
  // Try to get tenant_id from various sources
  return event.tenant_id || event.tenantId || event.body?.tenant_id || event.body?.tenantId;
}
