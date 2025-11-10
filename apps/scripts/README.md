# Key Generation Scripts

This directory contains scripts to generate the security keys needed for the EFOFX Estimate Service.

## **Available Scripts**

### **1. `generate_keys.sh` (Recommended)**
- **What it does**: Generates proper cryptographic keys using OpenSSL
- **Requirements**: OpenSSL (usually pre-installed on macOS)
- **Output**: Creates `private_key.pem`, `public_key.pem`, and `.env.template`
- **Best for**: Production use and proper security

### **2. `keygen.py`**
- **What it does**: Generates simplified keys using only Python built-in libraries
- **Requirements**: Python 3.6+ (no external packages)
- **Output**: Creates simplified keys for development/testing
- **Best for**: Development/testing when OpenSSL isn't available

## **Quick Start (Recommended)**

### **Option A: Using the Shell Script (OpenSSL)**

```bash
# Navigate to the scripts directory
cd estimator-project/scripts

# Run the key generation script
./generate_keys.sh

# Copy the generated template to your project root
cp .env.template ../.env

# Edit the .env file with your actual values
nano ../.env
```

### **Option B: Using Python Script**

```bash
# Navigate to the scripts directory
cd estimator-project/scripts

# Run the Python script
python3 keygen.py

# Copy the generated template to your project root
cp .env.template ../.env

# Edit the .env file with your actual values
nano ../.env
```

## **What Gets Generated**

### **1. HMAC_KEY_ID**
- A unique identifier for your HMAC key
- Format: `efofx-key-xxxxxxxx`
- Example: `efofx-key-a1b2c3d4`

### **2. HMAC_SECRET_B64**
- A base64-encoded secret key for HMAC signing
- 256-bit (32-byte) random key
- Used for authenticating requests to the MCP server

### **3. JWT_PUBLIC_KEY_PEM**
- Public key in PEM format for JWT verification
- Safe to share and commit to version control
- Used by the FastAPI app to verify incoming JWT tokens

### **4. JWT_PRIVATE_KEY (not in .env)**
- Private key for signing JWT tokens
- **NEVER commit this to version control**
- Keep it secure and use it only for generating tokens

## **Environment Variables**

After running the script, you'll need to add these to your `.env` file:

```bash
# Security Keys
HMAC_KEY_ID=efofx-key-a1b2c3d4
HMAC_SECRET_B64=YourBase64EncodedSecretHere...

# JWT Configuration
JWT_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----

# MCP Configuration
MCP_BASE_URL=https://your-do-functions-host
MCP_JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
```

## **Security Best Practices**

1. **Keep private keys secure**: Never commit `private_key.pem` to version control
2. **Rotate keys regularly**: Consider rotating HMAC secrets and JWT keys periodically
3. **Use strong key sizes**: RSA 2048-bit minimum, HMAC 256-bit minimum
4. **Store securely**: Use environment variables or secure secret management systems
5. **Backup keys**: Keep secure backups of your private keys

## **Troubleshooting**

### **OpenSSL not found**
```bash
# Install OpenSSL on macOS
brew install openssl

# Or use the Python script instead
python3 keygen.py
```

### **Permission denied**
```bash
# Make the script executable
chmod +x generate_keys.sh
```

### **Python script errors**
```bash
# Check Python version (needs 3.6+)
python3 --version

# Run with verbose output
python3 -v keygen.py
```

## **Manual Key Generation**

If you prefer to generate keys manually:

### **HMAC Secret**
```bash
# Generate 32-byte random key and encode as base64
openssl rand -base64 32
```

### **RSA Key Pair**
```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Extract public key
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

## **Next Steps**

After generating your keys:

1. **Copy `.env.template` to `.env`** in your project root
2. **Fill in the remaining values** (MCP_BASE_URL, OPENAI_API_KEY, etc.)
3. **Test your configuration** by running the FastAPI app
4. **Keep your private keys secure** and never share them

Your FastAPI application should now start without environment variable errors!
