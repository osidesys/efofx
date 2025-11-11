# Deployment Guide for EFOFX Estimate Service

This guide will help you deploy the FastAPI service to DigitalOcean App Platform and resolve environment variable issues.

## **Environment Variable Mismatch Issue**

The error you're seeing indicates a mismatch between:
1. **`project.yml`** (MCP Functions) - expects `LOG_LEVEL:-info`
2. **App Platform App Spec** - missing some environment variables

## **Solution: Update Your App Platform Configuration**

### **Option 1: Use the App Spec File (Recommended)**

1. **Update the app spec file** (`.do/app.yaml`) with your actual values:
   ```yaml
   # Replace these placeholder values with your actual values
   - key: JWT_PUBLIC_KEY_PEM
     scope: RUN_AND_BUILD_TIME
     value: "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
   
   - key: MCP_BASE_URL
     scope: RUN_AND_BUILD_TIME
     value: "https://your-actual-mcp-host.com"
   
   - key: HMAC_KEY_ID
     scope: RUN_AND_BUILD_TIME
     value: "efofx-key-xxxxxxxx"
   
   - key: HMAC_SECRET_B64
     scope: RUN_AND_BUILD_TIME
     value: "YourBase64EncodedSecretHere..."
   ```

2. **Deploy using the app spec**:
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

### **Option 2: Set Environment Variables in App Platform Console**

1. **Go to your App Platform dashboard**
2. **Select your app**
3. **Go to Settings → Environment Variables**
4. **Add these required variables**:

   | Key | Value | Scope |
   |-----|-------|-------|
   | `LOG_LEVEL` | `info` | Run Time |
   | `JWT_ISSUER` | `efofx-estimate` | Run Time |
   | `JWT_PUBLIC_KEY_PEM` | Your public key | Run Time |
   | `MCP_BASE_URL` | Your MCP server URL | Run Time |
   | `HMAC_KEY_ID` | Your HMAC key ID | Run Time |
   | `HMAC_SECRET_B64` | Your HMAC secret | Run Time |
   | `MCP_JWT_PRIVATE_KEY` | Your private key | Run Time |
   | `OPENAI_API_KEY` | Your OpenAI API key | Run Time |

## **Required Environment Variables**

### **Security & Authentication**
```bash
JWT_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----

JWT_ISSUER=efofx-estimate

HMAC_KEY_ID=efofx-key-xxxxxxxx
HMAC_SECRET_B64=YourBase64EncodedSecretHere...

MCP_JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----
```

### **External Services**
```bash
MCP_BASE_URL=https://your-mcp-server.com
OPENAI_API_KEY=sk-your-openai-api-key
```

### **Application Configuration**
```bash
LOG_LEVEL=info
APP_ENV=production
DEBUG=false
```

## **Deployment Steps**

### **1. Prepare Your Environment Variables**

Create a `.env.production` file with your production values:
```bash
# Copy from your local .env file
cp .env .env.production

# Edit with production values
nano .env.production
```

### **2. Deploy to App Platform**

#### **Using App Spec (Recommended)**
```bash
# Update the app spec with your values
nano .do/app.yaml

# Deploy
doctl apps create --spec .do/app.yaml
```

#### **Using Console**
1. Push your code to GitHub
2. Create a new app in App Platform
3. Connect your GitHub repository
4. Set environment variables in the console
5. Deploy

### **3. Verify Deployment**

Check your app is running:
```bash
# Get your app URL
doctl apps list

# Test the health endpoint
curl https://your-app-url/health
```

## **Troubleshooting**

### **Environment Variable Errors**

If you still get environment variable errors:

1. **Check your app spec** has all required variables
2. **Verify in App Platform console** that variables are set
3. **Check variable names** match exactly (case-sensitive)
4. **Ensure required variables** don't have empty values

### **Common Issues**

- **Missing LOG_LEVEL**: Set to `info` in your app
- **Missing JWT_ISSUER**: Set to `efofx-estimate`
- **Empty values**: Make sure all required variables have values
- **Case sensitivity**: Variable names must match exactly

### **Debugging**

1. **Check app logs** in App Platform console
2. **Verify environment variables** are loaded correctly
3. **Test locally** with the same environment variables
4. **Check FastAPI startup** for configuration errors

## **Security Best Practices**

1. **Use App Platform secrets** for sensitive values
2. **Never commit** private keys to version control
3. **Rotate keys** regularly
4. **Use least privilege** for service accounts
5. **Monitor access** and audit logs

## **Next Steps**

After successful deployment:

1. **Test your endpoints** to ensure they work
2. **Set up monitoring** and alerting
3. **Configure custom domain** if needed
4. **Set up CI/CD** for automated deployments
5. **Monitor performance** and logs

Your FastAPI service should now deploy successfully without environment variable errors!
