# **estimator-mcp-functions**
> Serverless MCP endpoints (DigitalOcean Functions) that expose Reference Class Forecasting (RCF) data to the monolithic FastAPI orchestrator. These endpoints are **not** called by the LLM directly; only the monolith calls them using signed requests.

## **Table of Contents**
- [Purpose](#purpose)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Endpoints](#endpoints)
- [Security](#security)
- [Tech Stack & Versions](#tech-stack--versions)
- [Project Layout](#project-layout)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [Testing & Quality Gates](#testing--quality-gates)
- [Observability](#observability)
- [Performance Targets](#performance-targets)
- [Operational Playbook](#operational-playbook)
- [FAQ](#faq)
- [License](#license)

---

## **Purpose**

- Serve a minimal **Model Context Protocol (MCP)** interface over HTTPS for reference classes.
- Return **distributional baselines** (P50/P80/P95), cost breakdowns, and metadata for RCF.
- Enforce **tenant isolation** and **cryptographic request verification**.
- Provide **small, cacheable payloads** tailored for LLM‑assisted estimation.

## **Architecture**
- **DigitalOcean Functions** (Node.js runtime nodejs:18) with **project.yml** configuration. 
- **MongoDB (Managed)** in same region + VPC.
- **HTTP JSON** API; stateless, idempotent handlers.
- **Access**: only the monolithic FastAPI service is authorized (HMAC + short‑lived JWT).

```
FastAPI (monolith) ───(HMAC+JWT)──▶ DO Functions (MCP, Node.js) ───▶ MongoDB
```

> Functions receive (event, context) and return a response object { body, statusCode?, headers? }. With web: true (default), query and JSON body fields are parsed onto top-level keys of event; HTTP details live under event.http. 

---

## **Data Model**
### **reference_classes**

```
{
  "id": "pool-installation-midrange-socal@v3",
  "tenant_id": "acme-co",
  "name": "Pool Installation – Midrange (SoCal)",
  "category": "construction",
  "subcategory": "pool",
  "region": "SoCal",
  "scope": "medium",
  "scale": "single_family_residential",
  "distribution_version": 3,
  "cost_distribution": { "P50": 78000, "P80": 93000, "P95": 115000 },
  "time_distribution": { "P50": 6, "P80": 8, "P95": 12 },
  "cost_breakdown": { "labor": 0.55, "materials": 0.32, "permits": 0.05, "overhead": 0.08 },
  "citations": ["cohort/pools_socal_2022_2024"],
  "schema_version": 1,
  "created_at": "2025-08-01T12:00:00Z",
  "updated_at": "2025-08-20T11:59:00Z"
}
```

### **observations (rolled into distributions)**
```
{
  "tenant_id": "acme-co",
  "reference_class_key": { "category": "construction", "subcategory": "pool", "region": "SoCal", "scope": "medium" },
  "outcome": { "cost": 86500, "time_weeks": 7 },
  "project_metadata": { "start": "2024-04-12", "finish": "2024-06-28" },
  "weight": 1.0,
  "schema_version": 1,
  "created_at": "2024-06-30T17:00:00Z"
}
```

### **modifiers**
```
{
  "tenant_id": "acme-co",
  "region": "SoCal",
  "season": "summer",
  "labor_multiplier": 1.06,
  "materials_multiplier": 1.02,
  "volatility_index": 0.12,
  "effective_from": "2025-06-01",
  "effective_to": "2025-09-30",
  "schema_version": 1
}
```

### **audit_logs**
```
{
  "when": "2025-08-24T17:20:31Z",
  "who": { "tenant_id": "acme-co", "sub": "user-123", "email": "estimator@acme.co" },
  "what": "reference_classes.query",
  "params": { "category": "construction", "region": "SoCal", "scope": "medium" },
  "rc_id": "pool-installation-midrange-socal@v3",
  "status": 200
}
```

---

## **Endpoints**

> **URL shape**: In Functions namespaces, public URLs follow the built-in pattern including namespace, package, and function. When deployed as an App Platform “Serverless Functions” component, final URLs look like:
> <app_url>/<component_route>/<package>/<function>. To serve /.well-known/mcp/manifest.json, add an edge/router rule at App Platform (or a proxy) to rewrite to your function URL. 


### **GET /.well-known/mcp/manifest.json**
- **Purpose:** Advertise available tools and schemas.
- **Cache:** 5–10 minutes.

### **POST /reference_classes/query**
**Input**

```
{
  "attributes": {
    "category": "construction",
    "subcategory": "pool",
    "region": "SoCal",
    "scope": "medium",
    "scale": "single_family_residential"
  },
  "options": { "allow_partial": false }
}
```

**Response (200)**

```
{
  "id": "pool-installation-midrange-socal@v3",
  "name": "Pool Installation – Midrange (SoCal)",
  "distribution_version": 3,
  "cost_distribution": { "P50": 78000, "P80": 93000, "P95": 115000 },
  "time_distribution": { "P50": 6, "P80": 8, "P95": 12 },
  "cost_breakdown": { "labor": 0.55, "materials": 0.32, "permits": 0.05, "overhead": 0.08 },
  "citations": ["cohort/pools_socal_2022_2024"]
}
```

**Errors:** 400 invalid_input, 401/403 unauthorized, 404 not_found.

### **GET /reference_classes/:id**
- Returns the same shape by id.

### **(Optional)** 
### **POST /adjustments/apply**
- Applies stored modifiers to a baseline estimate.

---

## **Security**
### **HMAC request signing (required)**
Headers:
- x-efofx-key-id, x-efofx-timestamp, x-efofx-nonce, x-efofx-signature
- signature = base64( HMAC_SHA256(secret, method|path|body|timestamp|nonce) )
    Reject skew > 120s, replayed nonces, or invalid signatures.

**Verifier (Node.js)**
```
// lib/auth.js
import crypto from 'node:crypto';

export function verifyHmac({ event, secretBase64 }) {
  const hdr = (name) => event.http?.headers?.[name] || event[name];
  const keyId = hdr('x-efofx-key-id');
  const ts = hdr('x-efofx-timestamp');
  const nonce = hdr('x-efofx-nonce');
  const sig = hdr('x-efofx-signature');

  if (!keyId || !ts || !nonce || !sig) return { ok: false, reason: 'missing_headers' };
  const now = Math.floor(Date.now()/1000);
  if (Math.abs(now - Number(ts)) > 120) return { ok: false, reason: 'timestamp_skew' };

  const body = JSON.stringify(event.body ?? event); // if you pass raw body, adjust accordingly
  const method = event.http?.method || 'POST';
  const path = event.http?.path || '';

  const msg = [method.toUpperCase(), path, body, ts, nonce].join('|');
  const key = Buffer.from(secretBase64, 'base64');
  const calc = crypto.createHmac('sha256', key).update(msg).digest('base64');

  const ok = crypto.timingSafeEqual(Buffer.from(calc), Buffer.from(sig));
  return ok ? { ok: true, keyId } : { ok: false, reason: 'bad_signature' };
}
```

> DO functions expose headers and parsed body fields in event when web: true; see **Parameters and Responses**. 

### **Short‑lived JWT (recommended)**
- Monolith includes a **1–5 min** JWT with claims: iss, aud="efofx-mcp", tenant_id, scope, jti.
- Verify signature; enforce tenant scoping in queries.

### **Tenant scoping & network**
- Every query includes tenant_id and filters by it.
- Mongo in **VPC**, Functions in same region; DB not publicly accessible.

---

## **Tech Stack & Versions**
|**Area**|**Library**|**Version**|
|---|---|---|
|Node.js Runtime|DigitalOcean Functions nodejs:18|nodejs:18 (set in project.yml)|
|HTTP runtime|DO Functions|response { body, statusCode, headers }|
|MongoDB Driver|mongodb|6.x|
|Schema Validation|zod|3.x|
|JWT|jsonwebtoken|9.x|
|Logging|pino|9.x|
|Cache (in-proc)|lru-cache|10.x|
|Test|vitest or jest|2.x / 29–30.x|
|Lint/Format|eslint / prettier|9.x / 3.x|

> Pin versions in package.json. The runtime is set via project.yml (runtime: 'nodejs:18'). 

---

## **Project Layout**
DigitalOcean Functions projects require project.yml at the root and a packages/ directory containing one or more packages, each with functions. Shared code can go in lib/. 

```
estimator-mcp-functions/
├─ project.yml
├─ packages/
│  └─ estimator/
│     ├─ manifest/              # GET /.well-known/mcp/manifest.json (via route/proxy)
│     │  ├─ index.js
│     │  └─ package.json
│     ├─ reference_classes-query/
│     │  ├─ index.js
│     │  └─ package.json
│     ├─ reference_classes-get/
│     │  ├─ index.js
│     │  └─ package.json
│     └─ adjustments-apply/
│        ├─ index.js
│        └─ package.json
├─ lib/
│  ├─ db.js        # Mongo client (module-scope, pooled)
│  ├─ auth.js      # HMAC/JWT verification
│  ├─ schemas.js   # zod validators
│  └─ log.js       # pino logger
└─ .env.example
```

### **project.yml**

###  **(example)**

```
packages:
  - name: estimator
    environment:
      DB_NAME: "${DB_NAME}"
      MONGO_URI: "${MONGO_URI}"
      HMAC_KEY_ID: "${HMAC_KEY_ID}"
      HMAC_SECRET_B64: "${HMAC_SECRET_B64}"
      JWT_PUBLIC_KEY_PEM: "${JWT_PUBLIC_KEY_PEM}"
    functions:
      - name: manifest
        runtime: "nodejs:18"
        web: true
        limits: { timeout: 2000, memory: 256 }
      - name: reference_classes-query
        runtime: "nodejs:18"
        web: true
        limits: { timeout: 2500, memory: 256 }
      - name: reference_classes-get
        runtime: "nodejs:18"
        web: true
        limits: { timeout: 2000, memory: 256 }
      - name: adjustments-apply
        runtime: "nodejs:18"
        web: true
        limits: { timeout: 2000, memory: 256 }
```

- Use **templating** to inject secrets from .env or App Platform env vars. 
- If you need a **cron** to rebuild distributions, add a triggers: block. 
    
### **Handlers**
**Manifest**
```
// packages/estimator/manifest/index.js
export async function main() {
  return {
    headers: { 'Cache-Control': 'public, max-age=600' },
    body: {
      mcpServer: 'estimator-mcp',
      version: '1.0.0',
      tools: [
        { name: 'reference_classes.query', description: 'Find the best reference class' },
        { name: 'reference_classes.get', description: 'Get RC distributions by id' }
      ]
    }
  };
}
```

**Mongo client (module-scope pooling)**
```
// lib/db.js
import { MongoClient } from 'mongodb';

let client;
export async function db() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 1500,
      connectTimeoutMS: 1500,
      socketTimeoutMS: 5000
    });
    await client.connect();
  }
  return client.db(process.env.DB_NAME || 'efofx');
}
```

**Query reference class**
```
// packages/estimator/reference_classes-query/index.js
import { db } from '../../../lib/db.js';
import { verifyHmac } from '../../../lib/auth.js';

export async function main(event) {
  const auth = verifyHmac({ event, secretBase64: process.env.HMAC_SECRET_B64 });
  if (!auth.ok) return { statusCode: 401, body: { error: 'unauthorized', reason: auth.reason } };

  const attrs = event.attributes || {};
  const tenantId = event.tenant_id || event.tenantId;
  if (!tenantId) return { statusCode: 400, body: { error: 'invalid_input', field: 'tenant_id' } };

  const match = Object.fromEntries(
    ['tenant_id','category','subcategory','region','scope','scale'].map(k => [k, (k==='tenant_id'?tenantId:attrs[k])]).filter(([,v]) => v != null)
  );

  const coll = (await db()).collection('reference_classes');
  const doc = await coll.findOne(match, {
    projection: { _id: 0, id: 1, name: 1, distribution_version: 1, cost_distribution: 1, time_distribution: 1, cost_breakdown: 1, citations: 1 }
  });

  return doc ? { body: doc } : { statusCode: 404, body: { error: 'not_found' } };
}
```

---

## **Local Development**
1. **Scaffold / init**
```
doctl serverless init --language js estimator-mcp-functions
# or structure manually as above
```
2. **Configure env**
- Put secrets in .env next to project.yml (read during deploy), or configure on App Platform. 
3. **Deploy**
```
doctl serverless deploy .
# add --remote-build if using native deps/bundlers
```
> You can also run doctl serverless init, deploy, detect package.json and build automatically; logs are accessible via doctl commands. 

4. **Find URLs / tail logs**
```
doctl serverless functions get estimator/manifest --url
doctl serverless activations logs --follow
```

5. **Invoke (example)**
```
curl -H "content-type: application/json" \
     -H "x-efofx-key-id: key-1" \
     -H "x-efofx-timestamp: $(date +%s)" \
     -H "x-efofx-nonce: $(uuidgen)" \
     -H "x-efofx-signature: <calc>" \
     -d '{"attributes":{"category":"construction","subcategory":"pool","region":"SoCal"},"tenant_id":"acme-co"}' \
     https://<function-url>/estimator/reference_classes-query
```

---

## **Configuration**
.env.example
```
MONGO_URI=mongodb+srv://...
DB_NAME=efofx_dev
HMAC_KEY_ID=key-1
HMAC_SECRET_B64=base64-encoded-secret
JWT_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----...
LOG_LEVEL=info
```

> project.yml supports environment templating from .env or App Platform variables. 

---

## **Testing & Quality Gates**
```
# Lint/format
npm run lint && npm run format:check

# Unit tests
npm test
```

- Contract tests for each function (happy-path + auth failures + replay/skew).
- Schema tests (zod) for input & output shapes.
- If using TypeScript, add tsc --noEmit as a gate.

---

## **Observability**
- **JSON logs** (pino or console) including: trace_id, tenant_id, tool, rc_id, status.    
- Use doctl serverless activations logs --follow to stream logs. 
- Emit latency and error counts (forward to your aggregator if using App Platform).

---

## **Performance Targets**
- Handler p95 ≤ **300–400 ms** (warm).
- Cold starts acceptable; monitor p99.
- Response size ≤ **5–20 KB** typical.

**Pooling & timeouts**
- Create the Mongo client **once per warm container** (module scope).
 - Suggested: maxPoolSize: 10, serverSelectionTimeoutMS: 1500, connectTimeoutMS: 1500, socketTimeoutMS: 5000.
 
**Caching (optional)**
- Per-instance LRU cache (30–120s) by tenant_id + attributes.
 
 ---

## **Operational Playbook**
- **Rotate HMAC secrets** quarterly (support dual keys during rotation).
- **Backfill/roll-ups**: run outside this repo (scheduled job or CI).
- **Safe deploy**: canary by deploying to a staging namespace, then prod.
- **Incident**: if Mongo unreachable, return 503 with trace_id, alert Ops.

---

## **FAQ**

**How do I map /.well-known/mcp/manifest.json exactly?**
Functions URLs include package/function. For a “pretty” path, front with App Platform routing or a tiny proxy that rewrites to your function URL. 

**Where do request fields live in Node?**
With web: true, parsed query/body fields are top-level in event; HTTP details are in event.http. Use event.http.headers for HMAC headers. 

**Which Node runtime should I pick?**
Set runtime: 'nodejs:18' in project.yml (per Functions runtime docs). 

---

## **License**
Proprietary. All rights reserved.
