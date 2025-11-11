"""Security utilities for JWT verification and RBAC."""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# JWT token scheme
security = HTTPBearer()


class JWTVerifier:
    """JWT verification and user extraction utilities."""
    
    def __init__(self):
        self.public_key = settings.jwt_public_key
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "sub", "tenant_id"]
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from JWT payload."""
        required_fields = ["sub", "tenant_id", "email"]
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Missing required claims: {missing_fields}"
            )
        
        return {
            "user_id": payload["sub"],
            "tenant_id": payload["tenant_id"],
            "email": payload["email"],
            "permissions": payload.get("permissions", []),
            "exp": payload["exp"]
        }


# Global JWT verifier instance
jwt_verifier = JWTVerifier()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = jwt_verifier.verify_token(token)
    return jwt_verifier.extract_user_info(payload)


async def require_permission(permission: str):
    """Dependency to require specific permission."""
    async def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get("permissions", [])
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return user
    
    return permission_checker


async def require_tenant_access(tenant_id: str):
    """Dependency to require access to specific tenant."""
    async def tenant_checker(user: Dict[str, Any] = Depends(get_current_user)):
        if user["tenant_id"] != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        return user
    
    return tenant_checker


def create_mcp_jwt(tenant_id: str, scope: str = "rc.read") -> str:
    """Create short-lived JWT for MCP calls."""
    now = datetime.utcnow()
    payload = {
        "aud": "efofx-mcp",
        "tenant_id": tenant_id,
        "scope": scope,
        "iat": now,
        "exp": now + timedelta(minutes=5),  # 5 minute expiry
        "iss": "efofx-estimate"
    }
    
    return jwt.encode(
        payload,
        settings.mcp_jwt_private_key,
        algorithm="RS256"
    )
