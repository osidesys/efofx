#!/bin/bash

# Generate security keys for EFOFX Estimate Service
# This script uses OpenSSL which should be available on macOS

set -e  # Exit on any error

echo "🔐 Generating EFOFX security keys using OpenSSL..."
echo ""

# Check if OpenSSL is available
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL is not installed. Please install it first:"
    echo "   brew install openssl"
    exit 1
fi

# Create scripts directory if it doesn't exist
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Generate HMAC Key ID
HMAC_KEY_ID="efofx-key-$(uuidgen | cut -d'-' -f1)"
echo "✅ HMAC_KEY_ID: $HMAC_KEY_ID"

# Generate HMAC Secret (Base64 encoded)
HMAC_SECRET_B64=$(openssl rand -base64 32)
echo "✅ HMAC_SECRET_B64: $HMAC_SECRET_B64"

echo ""
echo "🔑 Generating RSA key pair..."

# Generate private key (RSA 2048-bit)
openssl genrsa -out private_key.pem 2048 2>/dev/null
echo "✅ Private key generated: private_key.pem"

# Extract public key from private key
openssl rsa -in private_key.pem -pubout -out public_key.pem 2>/dev/null
echo "✅ Public key extracted: public_key.pem"

# Display the keys
echo ""
echo "📋 JWT_PRIVATE_KEY (save this securely):"
echo "=========================================="
cat private_key.pem
echo "=========================================="

echo ""
echo "📋 JWT_PUBLIC_KEY_PEM (put this in your .env):"
echo "=========================================="
cat public_key.pem
echo "=========================================="

# Create .env template
echo ""
echo "📝 Creating .env template..."
cat > .env.template << EOF
# Security Keys
HMAC_KEY_ID=$HMAC_KEY_ID
HMAC_SECRET_B64=$HMAC_SECRET_B64

# JWT Configuration
JWT_PUBLIC_KEY_PEM=$(cat public_key.pem | tr '\n' '\\n')

# MCP Configuration
MCP_BASE_URL=https://your-do-functions-host
MCP_JWT_PRIVATE_KEY=$(cat private_key.pem | tr '\n' '\\n')

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Application Configuration
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8080
DEBUG=false
LOG_LEVEL=info

# Optional Configuration
AUDIT_DB_URI=
REDIS_URL=
EOF

echo "✅ .env.template created with your keys"

echo ""
echo "🎯 Next steps:"
echo "1. Copy .env.template to .env: cp .env.template .env"
echo "2. Edit .env and fill in the remaining values"
echo "3. Keep private_key.pem secure and never commit it to version control"
echo "4. The public_key.pem is safe to share and commit"

echo ""
echo "🔒 Security notes:"
echo "- private_key.pem contains sensitive information - keep it secure!"
echo "- public_key.pem can be shared safely"
echo "- HMAC_SECRET_B64 should be kept secret"
echo "- Consider rotating these keys regularly in production"
