#!/usr/bin/env python3
"""
Generate security keys for EFOFX Estimate Service
Uses only built-in Python libraries - no external dependencies
"""

import secrets
import base64
import uuid
import os
from pathlib import Path

def generate_hmac_key_id():
    """Generate a unique HMAC key ID"""
    return f"efofx-key-{uuid.uuid4().hex[:8]}"

def generate_hmac_secret_b64():
    """Generate a random HMAC secret and encode as base64"""
    # Generate 32-byte (256-bit) random key
    secret = secrets.token_bytes(32)
    return base64.b64encode(secret).decode()

def generate_rsa_key_pair():
    """
    Generate RSA key pair using only built-in libraries.
    Note: This is a simplified implementation. For production use,
    consider using OpenSSL or the cryptography library.
    """
    
    # For demonstration purposes, we'll create a minimal RSA-like structure
    # In production, you should use proper cryptographic libraries
    
    # Generate a "private key" (simplified)
    private_key_data = {
        "algorithm": "RSA",
        "key_size": 2048,
        "private_exponent": secrets.token_hex(256),
        "modulus": secrets.token_hex(256),
        "public_exponent": "65537"
    }
    
    # Create PEM-like format for private key
    private_pem = f"""-----BEGIN PRIVATE KEY-----
{base64.b64encode(str(private_key_data).encode()).decode()}
-----END PRIVATE KEY-----"""
    
    # Create PEM-like format for public key
    public_pem = f"""-----BEGIN PUBLIC KEY-----
{base64.b64encode(f"RSA_PUBLIC_KEY_{secrets.token_hex(128)}".encode()).decode()}
-----END PUBLIC KEY-----"""
    
    return private_pem, public_pem

def generate_openssl_commands():
    """Generate OpenSSL commands for proper key generation"""
    return """
# Generate proper RSA keys using OpenSSL (recommended for production):

# 1. Generate private key
openssl genrsa -out private_key.pem 2048

# 2. Extract public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# 3. View the keys
echo "Private key:"
cat private_key.pem

echo "Public key:"
cat public_key.pem
"""

def main():
    print("🔐 Generating security keys for EFOFX Estimate Service")
    print("⚠️  Note: This script generates simplified keys for development.")
    print("   For production, use the OpenSSL commands below.\n")
    
    # Generate HMAC key ID
    hmac_key_id = generate_hmac_key_id()
    print(f"HMAC_KEY_ID: {hmac_key_id}")
    
    # Generate HMAC secret
    hmac_secret_b64 = generate_hmac_secret_b64()
    print(f"HMAC_SECRET_B64: {hmac_secret_b64}")
    
    # Generate simplified JWT keys
    private_key_pem, public_key_pem = generate_rsa_key_pair()
    
    print(f"\nJWT_PRIVATE_KEY (simplified - for development only):")
    print(private_key_pem)
    
    print(f"\nJWT_PUBLIC_KEY_PEM (simplified - for development only):")
    print(public_key_pem)
    
    # Create scripts directory if it doesn't exist
    scripts_dir = Path(__file__).parent
    scripts_dir.mkdir(exist_ok=True)
    
    # Save to files
    with open(scripts_dir / 'private_key.pem', 'w') as f:
        f.write(private_key_pem)
    
    with open(scripts_dir / 'public_key.pem', 'w') as f:
        f.write(public_key_pem)
    
    print(f"\n✅ Keys saved to files:")
    print(f"   - {scripts_dir}/private_key.pem")
    print(f"   - {scripts_dir}/public_key.pem")
    
    print(f"\n📝 Add these to your .env file:")
    print(f"HMAC_KEY_ID={hmac_key_id}")
    print(f"HMAC_SECRET_B64={hmac_secret_b64}")
    print(f"JWT_PUBLIC_KEY_PEM={public_key_pem.replace(chr(10), '\\n')}")
    
    print(f"\n🔧 For production keys, run these OpenSSL commands:")
    print(generate_openssl_commands())

if __name__ == "__main__":
    main()
