# Deployment Guide

This guide covers deploying the estimator-mcp-functions to DigitalOcean Functions.

## Prerequisites

1. **DigitalOcean Account**: You need a DigitalOcean account with API access
2. **doctl CLI**: Install the DigitalOcean CLI tool
3. **MongoDB Database**: A MongoDB instance (managed or self-hosted)
4. **Environment Variables**: Configure all required environment variables

## Setup

### 1. Install doctl

```bash
# macOS
brew install doctl

# Linux
snap install doctl

# Or download from: https://github.com/digitalocean/doctl/releases
```

### 2. Authenticate with DigitalOcean

```bash
doctl auth init
# Enter your DigitalOcean API token when prompted
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your actual values
```

## Local Development

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Tests

```bash
npm test
npm run lint
npm run format:check
```

### 3. Test Functions Locally

```bash
# Test manifest function
doctl serverless functions invoke estimator/manifest

# Test with custom event
doctl serverless functions invoke estimator/reference_classes-query \
  --param event='{"tenant_id":"test","attributes":{"category":"construction"}}'
```

## Deployment

### 1. Deploy to Functions Namespace

```bash
# Deploy all functions
doctl serverless deploy .

# Deploy with remote build (if using native dependencies)
doctl serverless deploy . --remote-build
```

### 2. Deploy to App Platform

If you want to deploy as part of an App Platform app:

1. Create an App Platform app
2. Add a "Serverless Functions" component
3. Point to this repository
4. Set environment variables in the App Platform dashboard

### 3. Verify Deployment

```bash
# List deployed functions
doctl serverless functions list

# Get function URLs
doctl serverless functions get estimator/manifest --url
doctl serverless functions get estimator/reference_classes-query --url

# Check function logs
doctl serverless activations logs --follow
```

## Testing Deployed Functions

### 1. Test Manifest Endpoint

```bash
curl -H "Content-Type: application/json" \
  https://<function-url>/estimator/manifest
```

### 2. Test Reference Classes Query (with HMAC)

```bash
# Generate HMAC signature (you'll need to implement this)
TIMESTAMP=$(date +%s)
NONCE=$(uuidgen)
BODY='{"attributes":{"category":"construction"},"tenant_id":"acme-co"}'
SIGNATURE=$(echo -n "POST|/estimator/reference_classes-query|$BODY|$TIMESTAMP|$NONCE" | \
  openssl dgst -sha256 -hmac "$(echo 'your-secret' | base64 -d)" -binary | base64)

curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-efofx-key-id: key-1" \
  -H "x-efofx-timestamp: $TIMESTAMP" \
  -H "x-efofx-nonce: $NONCE" \
  -H "x-efofx-signature: $SIGNATURE" \
  -d "$BODY" \
  https://<function-url>/estimator/reference_classes-query
```

## Monitoring & Troubleshooting

### 1. View Logs

```bash
# Stream logs in real-time
doctl serverless activations logs --follow

# View logs for specific function
doctl serverless activations logs --function estimator/reference_classes-query

# View recent activations
doctl serverless activations list
```

### 2. Common Issues

- **Cold Start Delays**: First request may be slow, subsequent requests are faster
- **Memory Limits**: Functions are limited to 256MB by default
- **Timeout Issues**: Functions timeout after 2-2.5 seconds
- **Database Connection**: Ensure MongoDB is accessible from Functions

### 3. Performance Optimization

- **Connection Pooling**: MongoDB client is pooled per function instance
- **Caching**: Consider adding LRU cache for frequently accessed data
- **Async Operations**: Use async/await for database operations

## Security Considerations

1. **HMAC Keys**: Rotate HMAC secrets quarterly
2. **JWT Keys**: Use strong RSA keys for JWT verification
3. **Network Security**: MongoDB should be in VPC, not publicly accessible
4. **Rate Limiting**: Consider implementing rate limiting for production

## Rollback

If you need to rollback to a previous version:

```bash
# List deployments
doctl serverless deployments list

# Rollback to specific deployment
doctl serverless deployments rollback <deployment-id>
```

## Support

For issues with DigitalOcean Functions:
- [DigitalOcean Functions Documentation](https://docs.digitalocean.com/products/functions/)
- [DigitalOcean Support](https://cloud.digitalocean.com/support)
- [Functions Community](https://www.digitalocean.com/community/tags/functions)
