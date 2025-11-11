# EFOFX Estimate Service

> Monolithic **FastAPI** service that powers chat‑driven estimates. It normalizes project attributes, calls the MCP server (serverless Functions) to fetch **reference class facts**, applies local policies/modifiers, invokes the LLM, validates structured output, and records audit/metrics/logs.

## **Table of Contents**
- [Purpose](#purpose-1)
- [Architecture](#architecture-1)
- [Public API](#public-api)
- [Internal Schemas](#internal-schemas)
- [Data Model](#data-model-1)
- [Tech Stack & Versions](#tech-stack--versions-1)
- [Project Layout](#project-layout-1)
- [Local Development](#local-development-1)
- [Configuration](#configuration-1)
- [Security Model](#security-model)
- [Observability](#observability-1)
- [Testing & Quality Gates](#testing--quality-gates-1)
- [LLM Guardrails](#llm-guardrails)
- [Performance Targets](#performance-targets-1)
- [Operational Playbook](#operational-playbook-1)
- [License](#license-1)
    
---

## **Purpose**
- Provide a **/chat** endpoint that converts conversational input into **reference‑class‑grounded** estimates.
- Encapsulate **RCF orchestration**: attribute normalization → MCP fetch → facts block → LLM call → schema‑validated output.
- Serve as the **only caller** of the MCP Functions, enforcing **HMAC + JWT** and tenant scoping.
- Centralize **audit, metrics, and logs**.

## **Architecture**
- **FastAPI** (Python 3.13.5) with **httpx** for outbound MCP calls
- **OpenAI** SDK for LLM completions
- Optional **Redis** cache for session and hot reference class lookups
- **Prometheus** metrics + **structured logs** (Loki)

```
User ▶ FastAPI /chat ▶ Orchestrator ▶ MCP(client) ▶ DO Functions(MCP) ▶ Mongo
                   └──────▶ OpenAI (LLM) ────────┘
```

## **Public API**
### **POST /chat**
**Request**

```json
{
  "message": "We want a midrange pool in SoCal, medium scope.",
  "session_id": "sess-abc"
}
```

**Response**

```json
{
  "summary": "For a midrange SoCal pool install, expect ...",
  "estimate": {
    "totals": { "P50": 79200, "P80": 94800, "P95": 117000 },
    "breakdown": [
      { "bucket": "labor", "amountP50": 43560 },
      { "bucket": "materials", "amountP50": 25344 },
      { "bucket": "permits", "amountP50": 3960 },
      { "bucket": "overhead", "amountP50": 6336 }
    ],
    "time_weeks": { "P50": 6, "P80": 8, "P95": 12 }
  },
  "reference": {
    "reference_class_id": "pool-installation-midrange-socal@v3",
    "distribution_version": 3
  },
  "trace_id": "trc-7b2f"
}
```
- **Auth**: Bearer JWT from your app (tenant/user claims).
- **Latency goal**: p95 ≤ 1.5 s end‑to‑end (warm path).

## **Internal Schemas (pydantic)**

```python
# rcf/schemas.py
class CostDist(BaseModel):
    P50: conint(ge=0)
    P80: conint(ge=0)
    P95: conint(ge=0)

class TimeDist(BaseModel):
    P50: PositiveInt
    P80: PositiveInt
    P95: PositiveInt

class FactsBlock(BaseModel):
    reference_class_id: str
    distribution_version: PositiveInt
    cost_distribution: CostDist
    time_distribution: TimeDist
    cost_breakdown: Dict[str, confloat(ge=0, le=1)]
    modifiers_applied: List[Dict[str, Any]] = []
    policy: Dict[str, Any] = {}

class EstimateBucket(BaseModel):
    bucket: str
    amountP50: conint(ge=0)

class EstimateJSON(BaseModel):
    totals: CostDist
    breakdown: List[EstimateBucket]
    time_weeks: TimeDist

class EstimateResponse(BaseModel):
    summary: str
    estimate: EstimateJSON
    reference: Dict[str, Any]
    trace_id: str
```

## **Data Model**
> This service can be "stateless" (no DB) or persist **audit** and **estimates**.

### **Session (optional cache)**

```json
{
  "session_id": "sess-abc",
  "tenant_id": "acme-co",
  "attrs": { "category": "construction", "subcategory": "pool", "region": "SoCal", "scope": "medium" },
  "last_rc_id": "pool-installation-midrange-socal@v3",
  "created_at": "2025-08-24T17:10:00Z"
}
```

### **Audit**

```json
{
  "when": "2025-08-24T17:20:31Z",
  "tenant_id": "acme-co",
  "sub": "user-123",
  "email": "estimator@acme.co",
  "action": "estimate.create",
  "rc_id": "pool-installation-midrange-socal@v3",
  "distribution_version": 3,
  "estimate_id": "est-9f1a",
  "latency_ms": 842,
  "status": "success"
}
```

### **Estimates (optional)**

```json
{
  "estimate_id": "est-9f1a",
  "tenant_id": "acme-co",
  "reference_class_id": "pool-installation-midrange-socal@v3",
  "facts_block": { "...": "as passed to LLM" },
  "estimate_json": { "...": "validated result" },
  "summary_text": "For a midrange SoCal pool install, expect ...",
  "schema_version": 1,
  "created_at": "2025-08-24T17:20:31Z"
}
```

## **Tech Stack & Versions**

|**Area**|**Library**|**Version**|
|---|---|---|
|Python Runtime|Python|3.13.5|
|Web|fastapi|0.116.1|
|ASGI Server|uvicorn|0.35.x|
|HTTP Client|httpx|0.28.1|
|Validation|pydantic|2.8.2|
|Auth (JWT)|pyjwt|2.11.1|
|OpenAI|openai|1.101.0|
|Caching (opt)|redis|5.0.8|
|Metrics|prometheus-client|0.22.1|
|Logging|structlog|24.1.0|
|Testing|pytest|8.3.2|
|Lint|ruff|0.6.5|
|Types|mypy|1.11.2|

## **Project Layout**

```
efofx-estimate/
  ├─ app/
  │   ├─ main.py                 # FastAPI app
  │   ├─ api/
  │   │   └─ chat.py             # /chat endpoint
  │   ├─ core/
  │   │   ├─ config.py           # settings (pydantic)
  │   │   ├─ security.py         # JWT verify, RBAC
  │   │   └─ signing.py          # HMAC headers for MCP
  │   ├─ rcf/
  │   │   ├─ orchestrator.py     # normalize attrs, facts, call LLM
  │   │   ├─ normalize.py        # attribute extractors
  │   │   └─ schemas.py          # facts_block + estimate schemas
  │   ├─ clients/
  │   │   ├─ mcp.py              # HTTP client for DO Functions
  │   │   └─ openai_client.py    # LLM invocation wrapper
  │   ├─ observability/
  │   │   ├─ metrics.py          # Prometheus
  │   │   └─ logging.py          # structured logs
  │   └─ storage/
  │       ├─ audit.py            # audit persistence (Mongo/Postgres)
  │       └─ estimates.py        # optional estimate store
  ├─ tests/
  ├─ pyproject.toml
  ├─ README.md
  └─ env.example
```

## **Local Development**

### 1. **Install Dependencies**

```bash
# Install Python 3.13.5+ if not already installed
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -e .
```

### 2. **Environment Setup**

```bash
# Copy environment template
cp env.example .env

# Edit .env with your actual values
# Required:
# - JWT_PUBLIC_KEY_PEM
# - MCP_BASE_URL
# - HMAC_KEY_ID
# - HMAC_SECRET_B64
# - MCP_JWT_PRIVATE_KEY
# - OPENAI_API_KEY
```

### 3. **Run the Service**

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8080

# Or using the main function
python -m app.main
```

### 4. **Try the API**

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test chat endpoint (requires valid JWT)
curl -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"message":"We want a midrange pool in SoCal, medium scope."}' \
     http://localhost:8080/api/v1/chat
```

### 5. **View API Documentation**

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Metrics**: http://localhost:8080/metrics

## **Configuration**

### Environment Variables

```bash
# Application Environment
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8080
DEBUG=false

# JWT Configuration
JWT_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----...

# MCP Configuration
MCP_BASE_URL=https://your-do-functions-host
HMAC_KEY_ID=key-1
HMAC_SECRET_B64=base64-encoded-secret
MCP_JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----...

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Prometheus Configuration
PROMETHEUS_PORT=9000

# Logging Configuration
LOG_LEVEL=info

# Database Configuration (Optional)
AUDIT_DB_URI=mongodb+srv://...    # or postgresql://...
REDIS_URL=redis://localhost:6379/0

# Performance Tuning
MCP_TIMEOUT=5.0
LLM_TIMEOUT=30.0
MAX_RETRIES=3
CACHE_TTL=120
```

## **Security Model**
- **Inbound**: Verify user JWT; extract tenant_id, sub, email.
- **Outbound to MCP**: Sign with HMAC headers + short‑lived JWT (aud="efofx-mcp", tenant_id, scope="rc.read", exp ≤ 5 min).
- **Tenant isolation**: Orchestrator always includes tenant_id and enforces it at response handling time.
- **PII**: Logs contain hashed or minimal user identifiers; avoid storing message text unless needed.
  
## **Observability**
- **Prometheus**:
    - http_requests_total{route,method,status,tenant_id}
    - mcp_call_latency_ms{tool,tenant_id}
    - llm_latency_ms{model}
    - estimate_created_total{tenant_id,rc_id}
    
- **Logs (JSON)**: trace_id, tenant_id, rc_id, distribution_version, latency_ms, status.
- **Audit**: Every successful estimate produces a normalized record.

## **Testing & Quality Gates**

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_schemas.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Type checking with mypy
mypy .

# Format code with black
black .

# Run all quality checks
ruff check . && mypy . && pytest
```

- Unit: normalization, MCP client signing, LLM response validation.
- Contract: stub MCP responses; strict schema checks.
- Load: happy‑path /chat at target RPS; assert p95 budget.
    
## **LLM Guardrails**
- **Ground truth only**: Numbers must come from facts_block; never hallucinate distributions.
- **Structured output**: Must validate against EstimateResponse. Reprompt with correction if invalid.
- **Explainability**: Always include reference_class_id and distribution_version in the response.
- **Uncertainty**: If gaps exist, widen ranges and surface assumptions.
- **No direct DB**: The LLM does not call MCP or databases; only the orchestrator does.

## **Performance Targets**
- **MCP call** p95 ≤ 300–400 ms (warm).
- **LLM call** tuned via prompt size; keep facts block compact (≤ 5–10 KB).
- **End‑to‑end** p95 ≤ 1.5 s typical.
  
## **Operational Playbook**
- **Key rotation**: Rotate HMAC/JWT keys; support dual keys during rotation.
- **Backoff**: Exponential with jitter on MCP calls; total deadline ≤ 1.5–2.0 s.
- **Caching**: 30–120 s TTL on identical attribute+tenant lookups.
- **Degradation**: If MCP 404s, fallback to nearest‑neighbor or return actionable "needs clarification."
- **Incidents**: Return user‑safe message; include trace_id for support.

## **Development Workflow**

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement changes**
   - Follow the existing code structure
   - Add appropriate tests
   - Update documentation

3. **Run quality checks**
   ```bash
   ruff check .
   mypy .
   pytest
   ```

4. **Create pull request**
   - Include description of changes
   - Link any related issues
   - Request code review

### Debugging

- **Logs**: Check structured logs for trace_id
- **Metrics**: Monitor Prometheus metrics at `/metrics`
- **API**: Use FastAPI's built-in debugging tools
- **Database**: Check audit and estimate storage logs

## **Deployment**

### Docker (Recommended)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: efofx-estimate
spec:
  replicas: 3
  selector:
    matchLabels:
      app: efofx-estimate
  template:
    metadata:
      labels:
        app: efofx-estimate
    spec:
      containers:
      - name: efofx-estimate
        image: efofx-estimate:latest
        ports:
        - containerPort: 8080
        env:
        - name: APP_ENV
          value: "production"
        - name: JWT_PUBLIC_KEY_PEM
          valueFrom:
            secretKeyRef:
              name: efofx-secrets
              key: jwt-public-key-pem
```

## **License**
Proprietary. All rights reserved.
