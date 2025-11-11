"""HMAC signing utilities for MCP authentication."""

import base64
import hashlib
import hmac
import time
from typing import Dict, Optional
from urllib.parse import urlparse

from app.core.config import settings


class HMACSigner:
    """HMAC signing for MCP authentication headers."""
    
    def __init__(self):
        self.key_id = settings.mcp_hmac_key_id
        self.secret = base64.b64decode(settings.mcp_hmac_secret)
    
    def sign_request(
        self,
        method: str,
        url: str,
        body: Optional[bytes] = None,
        timestamp: Optional[int] = None
    ) -> Dict[str, str]:
        """Sign HTTP request with HMAC authentication."""
        if timestamp is None:
            timestamp = int(time.time())
        
        # Parse URL components
        parsed_url = urlparse(url)
        path = parsed_url.path
        if parsed_url.query:
            path += "?" + parsed_url.query
        
        # Create canonical request string
        canonical_request = f"{method.upper()}\n{path}\n{timestamp}"
        if body:
            body_hash = hashlib.sha256(body).hexdigest()
            canonical_request += f"\n{body_hash}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret,
            canonical_request.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Return authentication headers
        return {
            "X-EFOFX-Key-ID": self.key_id,
            "X-EFOFX-Timestamp": str(timestamp),
            "X-EFOFX-Signature": signature,
        }
    
    def verify_signature(
        self,
        method: str,
        url: str,
        body: Optional[bytes],
        timestamp: int,
        signature: str
    ) -> bool:
        """Verify HMAC signature (for testing purposes)."""
        expected_headers = self.sign_request(method, url, body, timestamp)
        return expected_headers["X-EFOFX-Signature"] == signature


# Global HMAC signer instance
hmac_signer = HMACSigner()
