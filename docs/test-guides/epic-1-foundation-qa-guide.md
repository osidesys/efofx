# Epic 1: Foundation & Infrastructure - Manual QA Test Guide

**Version:** 1.0
**Date:** 2025-11-10
**Epic:** Foundation & Infrastructure Setup
**Tester Profile:** No prior codebase knowledge required

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Test Cases](#test-cases)
4. [Expected Results](#expected-results)
5. [Known Limitations](#known-limitations)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

Before starting, ensure you have access to:

- ✅ **GitHub Account** - For repository access and auto-deploy testing
- ✅ **MongoDB Atlas Account** - Free tier (M0) is sufficient
  - Sign up at: https://www.mongodb.com/cloud/atlas
- ✅ **Sentry Account** - Free tier (5,000 errors/month) is sufficient
  - Sign up at: https://sentry.io/signup/
- ✅ **DigitalOcean Account** - For deployment testing (optional for basic testing)
  - Sign up at: https://www.digitalocean.com/

### Required Tools

Install the following tools on your machine:

- ✅ **Node.js 20+** - JavaScript runtime
  - Download: https://nodejs.org/
  - Verify: `node --version` (should be 20.0.0 or higher)

- ✅ **Python 3.11+** - Programming language
  - Download: https://www.python.org/downloads/
  - Verify: `python3 --version` (should be 3.11.0 or higher)

- ✅ **npm** - Node package manager (comes with Node.js)
  - Verify: `npm --version`

- ✅ **git** - Version control
  - Download: https://git-scm.com/
  - Verify: `git --version`

- ✅ **curl** - Command line tool for testing HTTP endpoints
  - Usually pre-installed on macOS/Linux
  - Windows: Download from https://curl.se/
  - Verify: `curl --version`

### Test Data Requirements

**None** - Epic 1 is infrastructure setup. No test data is required.

---

## Environment Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/[your-org]/efofx-workspace.git

# Navigate to the project directory
cd efofx-workspace

# Verify you're in the correct directory
pwd
# Expected output: /path/to/efofx-workspace
```

### Step 2: Setup Widget (Frontend)

```bash
# Navigate to widget directory
cd apps/efofx-widget

# Install dependencies
npm install

# Expected output:
# - "added X packages" message
# - No error messages
# - Takes ~10-30 seconds

# Build the widget
npm run build

# Expected output:
# - "dist/embed.js" file created
# - Build time ~1-2 seconds
# - No errors

# Verify build output
ls -lh dist/

# Expected output:
# - embed.js file (~578KB)
# - vite.svg file
```

### Step 3: Setup Backend (API)

```bash
# Navigate to backend directory
cd ../../apps/efofx-estimate

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Your terminal prompt should now show (.venv)

# Install dependencies
pip install -r requirements.txt

# Expected output:
# - "Successfully installed..." messages
# - Takes ~1-2 minutes
# - No error messages
```

### Step 4: Configure Environment Variables

```bash
# Still in apps/efofx-estimate directory

# Copy example environment file
cp .env.example .env

# Edit .env file (use your preferred text editor)
nano .env  # or: code .env, vim .env, etc.

# REQUIRED: Update these values:
# MONGO_URI=mongodb+srv://[username]:[password]@[cluster].mongodb.net/efofx_production
# OPENAI_API_KEY=sk-[your-openai-api-key]
# SECRET_KEY=[generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
# JWT_SECRET_KEY=[generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
# ENCRYPTION_KEY=[generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"]

# OPTIONAL (for Sentry testing):
# SENTRY_DSN=https://[your-sentry-dsn]@sentry.io/[project-id]

# Save and close the file
```

**MongoDB Atlas Setup:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free M0 cluster
3. Click "Connect" → "Connect your application"
4. Copy the connection string and paste it into MONGO_URI in .env
5. Replace `<password>` with your database password
6. Change database name from `test` to `efofx_production`

**Sentry Setup (Optional):**
1. Go to https://sentry.io/
2. Create a new project (select "FastAPI" as platform)
3. Copy the DSN from the setup page
4. Paste into SENTRY_DSN in .env

---

## Test Cases

### TC1.1: Widget Builds Successfully

**Objective:** Verify the widget project builds and produces a single embed.js bundle

**Steps:**
```bash
cd apps/efofx-widget
npm run build
ls -lh dist/
```

**Expected Results:**
- ✅ Build completes without errors
- ✅ `dist/embed.js` file exists
- ✅ File size is < 600KB (actual: ~578KB)
- ✅ Build time is < 5 seconds

**Pass Criteria:** All checkboxes above are ✅

---

### TC1.2: Backend Starts Successfully

**Objective:** Verify the FastAPI backend starts without errors

**Steps:**
```bash
cd apps/efofx-estimate
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting efOfX Estimation Service...
INFO:     MongoDB connection established
INFO:     Sentry SDK initialized successfully (or: Sentry DSN not configured)
INFO:     Application startup complete.
```

**Expected Results:**
- ✅ Server starts on port 8000
- ✅ No error messages in console
- ✅ MongoDB connection message appears
- ✅ Application startup complete message appears

**Pass Criteria:** All checkboxes above are ✅

**Keep the server running for the next tests.**

---

### TC1.3: Health Endpoint Returns 200 OK

**Objective:** Verify the /health endpoint is accessible and returns correct status

**Steps:**
```bash
# In a NEW terminal window (keep server running in first terminal)
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "efOfX Estimation Service",
  "database": "connected",
  "version": "1.0.0"
}
```

**Expected Results:**
- ✅ HTTP 200 status code
- ✅ Response time < 100ms
- ✅ `status` field is "healthy"
- ✅ `database` field is "connected"

**Pass Criteria:** All checkboxes above are ✅

---

### TC1.4: MongoDB Connection Status in Health Response

**Objective:** Verify health endpoint includes database status check

**Steps:**
```bash
curl http://localhost:8000/health | jq '.database'
```

**Expected Output:**
```
"connected"
```

**Expected Results:**
- ✅ Database field is "connected"
- ✅ If MongoDB is unavailable, field changes to "disconnected" and status becomes "degraded"

**Pass Criteria:** Database status correctly reflects MongoDB connection state

---

### TC1.5: Sentry Captures Test Error

**Objective:** Verify Sentry error tracking is configured and captures errors

**Prerequisites:** SENTRY_DSN must be configured in .env

**Steps:**
```bash
# Trigger test error endpoint
curl http://localhost:8000/test-error
```

**Expected Output:**
```json
{
  "detail": "This is a test error to verify Sentry integration"
}
```

**Verification Steps:**
1. Check server logs - should see:
   ```
   ERROR: Test error endpoint triggered - intentional error for Sentry testing
   ```

2. Go to Sentry dashboard (https://sentry.io/)
3. Navigate to your project
4. Check "Issues" tab

**Expected Results:**
- ✅ Error appears in Sentry dashboard within 30 seconds
- ✅ Error shows full stack trace
- ✅ Environment tag matches .env configuration
- ✅ Release version is "1.0.0"

**Pass Criteria:** Error captured in Sentry with full details

**Note:** If SENTRY_DSN is not configured, this test will be skipped. Server will log: "Sentry DSN not configured, error tracking disabled"

---

### TC1.6: DigitalOcean Deployment Configuration Exists

**Objective:** Verify .do/app.yaml configuration file is created and valid

**Steps:**
```bash
cd apps/efofx-estimate
cat .do/app.yaml
```

**Expected Results:**
- ✅ File exists at `.do/app.yaml`
- ✅ Contains Gunicorn run command
- ✅ Health check endpoint configured as `/health`
- ✅ CPU alert configured at 80%
- ✅ Memory alert configured at 90%
- ✅ GitHub auto-deploy enabled (`deploy_on_push: true`)
- ✅ Instance size is `basic-xs`

**Pass Criteria:** File exists with all required configuration

**Note:** Actual deployment testing requires DigitalOcean account and is beyond scope of this guide.

---

### TC1.7: Widget Embeds in Test HTML Page

**Objective:** Verify widget can be embedded in a test HTML page

**Steps:**
```bash
cd apps/efofx-widget

# Open test-embed.html in browser
# macOS:
open test-embed.html

# Linux:
xdg-open test-embed.html

# Windows:
start test-embed.html
```

**Expected Results:**
- ✅ Page loads without console errors
- ✅ Widget container is visible
- ✅ Widget initialization message in console: "efOfX Widget initialized successfully!"
- ✅ No CSS conflicts with page styles (widget is isolated via Shadow DOM)
- ✅ React dev tools show widget component tree

**Visual Verification:**
- Page shows header "efOfX Widget Test Page"
- Widget loads in the designated container
- Widget styles don't affect page header styles

**Pass Criteria:** Widget loads and renders without errors

---

## Expected Results

### Summary

When all test cases pass, you should have:

| Component | Expected State |
|-----------|---------------|
| **Widget Build** | Single `embed.js` file (~578KB) |
| **Backend Server** | Running on port 8000, no errors |
| **Health Endpoint** | Returns 200 OK, response time < 100ms |
| **MongoDB** | Connected, status visible in /health |
| **Sentry** | Capturing errors (if configured) |
| **DO Config** | Complete app.yaml with alerts |
| **Widget Embed** | Loads in test HTML page |

### Performance Benchmarks

- Widget bundle size: < 600KB ✅ (actual: 578KB)
- Backend health check: < 100ms ✅
- MongoDB connection: Established on startup ✅
- Sentry error capture: < 30 seconds ✅

---

## Known Limitations

At this stage (Epic 1 complete), the following are expected limitations:

### API Endpoints
- ❌ **No business logic endpoints** - Only `/health`, `/test-error`, and `/` exist
- ❌ **No estimation API** - Will be implemented in Epic 2
- ❌ **No tenant management** - Will be implemented in Epic 3
- ❌ **No authentication** - Will be implemented in Epic 3

### Database
- ❌ **No collections created** - Database exists but is empty
- ❌ **No indexes defined** - Will be created when collections are added
- ❌ **No seed data** - Synthetic data generation is Epic 2

### Widget
- ❌ **Placeholder content only** - Widget renders but has no chat functionality
- ❌ **No API integration** - Will connect to backend in Epic 4
- ❌ **No branding system** - Will be implemented in Epic 5

### Deployment
- ❌ **Not deployed to DigitalOcean** - Manual deployment required
- ❌ **No production environment** - Configuration exists, actual deployment is manual
- ❌ **Auto-deploy not tested** - Requires GitHub repo connection to DO

These limitations are **expected and acceptable** for Epic 1. They will be addressed in subsequent epics.

---

## Troubleshooting

### Issue: Widget build fails with "tailwindcss" error

**Symptoms:**
```
[postcss] It looks like you're trying to use `tailwindcss` directly
```

**Solution:**
```bash
npm install @tailwindcss/postcss
# Verify postcss.config.js uses '@tailwindcss/postcss'
```

---

### Issue: Backend fails to start - "ImportError: No module named"

**Symptoms:**
```
ImportError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Your prompt should show (.venv)

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: MongoDB connection fails

**Symptoms:**
```
ERROR: Failed to connect to MongoDB
```

**Solution:**
1. Verify MONGO_URI in .env is correct
2. Check MongoDB Atlas:
   - Cluster is running (not paused)
   - IP whitelist includes your IP (or use 0.0.0.0/0 for testing)
   - Database user credentials are correct
3. Test connection:
   ```bash
   # Use mongosh or MongoDB Compass to verify connection string
   ```

---

### Issue: Health endpoint returns "database": "disconnected"

**Symptoms:**
```json
{"status": "degraded", "database": "disconnected"}
```

**Solution:**
1. Check server logs for MongoDB connection error
2. Verify MONGO_URI in .env
3. Restart server after fixing .env:
   ```bash
   # Press CTRL+C to stop
   uvicorn app.main:app --reload
   ```

---

### Issue: Sentry errors not appearing

**Symptoms:**
- /test-error returns 500 but nothing in Sentry dashboard

**Solution:**
1. Verify SENTRY_DSN is correctly configured in .env
2. Check server logs for "Sentry SDK initialized successfully"
3. Verify Sentry project is active
4. Wait 30-60 seconds - Sentry may batch events
5. Check Sentry project settings for rate limiting

---

### Issue: Port 8000 already in use

**Symptoms:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 [PID]

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

---

## Approval Checklist

Before marking Epic 1 as complete, verify:

- [ ] **TC1.1** - Widget builds successfully (embed.js < 600KB)
- [ ] **TC1.2** - Backend starts without errors
- [ ] **TC1.3** - Health endpoint returns 200 OK
- [ ] **TC1.4** - MongoDB connection status is "connected"
- [ ] **TC1.5** - Sentry captures test errors (if configured)
- [ ] **TC1.6** - DigitalOcean app.yaml exists with correct config
- [ ] **TC1.7** - Widget embeds in test HTML page

**Epic 1 is approved when all checkboxes above are ✅**

---

## Next Steps

After Epic 1 approval:

1. **Epic 2**: Reference Class Engine & Synthetic Data
   - Implement MongoDB schemas
   - Create RCF matching algorithm
   - Generate synthetic construction data
   - Implement baseline estimation calculation

2. **Epic 3**: Multi-Tenant Infrastructure & Security
   - Tenant registration and management
   - JWT authentication
   - BYOK encryption for API keys
   - Tenant isolation middleware

3. **Epic 4**: LLM Integration & Conversational Scoping
   - OpenAI client with BYOK support
   - Git-based prompt management
   - Estimate narratives generation
   - Conversational chat engine

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Next Review:** After Epic 1 QA completion
