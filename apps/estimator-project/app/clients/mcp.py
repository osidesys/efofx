"""MCP client for communicating with DigitalOcean Functions."""

import asyncio
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import httpx
import structlog
from app.core.config import settings
from app.core.security import create_mcp_jwt
from app.core.signing import hmac_signer
from app.observability.metrics import mcp_metrics

logger = structlog.get_logger(__name__)


class MCPClient:
    """HTTP client for MCP server communication."""
    
    def __init__(self):
        self.base_url = settings.mcp_base_url.rstrip('/')
        self.timeout = httpx.Timeout(settings.mcp_timeout)
        self.max_retries = settings.max_retries
    
    async def get_reference_class_facts(
        self, 
        rc_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Fetch reference class facts from MCP server."""
        start_time = time.time()
        
        try:
            # Create MCP JWT
            mcp_jwt = create_mcp_jwt(tenant_id, scope="rc.read")
            
            # Prepare request
            url = urljoin(self.base_url, f"/reference_classes/{rc_id}")
            headers = {
                "Authorization": f"Bearer {mcp_jwt}",
                "Content-Type": "application/json",
                "X-Tenant-ID": tenant_id,
            }
            
            # Add HMAC signature
            hmac_headers = hmac_signer.sign_request("GET", url)
            headers.update(hmac_headers)
            
            logger.info(
                "Fetching reference class facts",
                rc_id=rc_id,
                tenant_id=tenant_id,
                url=url
            )
            
            # Make request with retries
            response_data = await self._make_request_with_retries(
                "GET", url, headers=headers
            )
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            mcp_metrics.record_mcp_call_success(
                tool="reference_classes_get",
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            logger.info(
                "Successfully fetched reference class facts",
                rc_id=rc_id,
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            return response_data
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            mcp_metrics.record_mcp_call_failure(
                tool="reference_classes_get",
                tenant_id=tenant_id,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to fetch reference class facts",
                rc_id=rc_id,
                tenant_id=tenant_id,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
    
    async def query_reference_classes(
        self, 
        query: Dict[str, Any], 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Query reference classes based on criteria."""
        start_time = time.time()
        
        try:
            # Create MCP JWT
            mcp_jwt = create_mcp_jwt(tenant_id, scope="rc.read")
            
            # Prepare request
            url = urljoin(self.base_url, "/reference_classes/query")
            headers = {
                "Authorization": f"Bearer {mcp_jwt}",
                "Content-Type": "application/json",
                "X-Tenant-ID": tenant_id,
            }
            
            # Add HMAC signature
            body = query
            hmac_headers = hmac_signer.sign_request("POST", url, body=str(body).encode())
            headers.update(hmac_headers)
            
            logger.info(
                "Querying reference classes",
                query=query,
                tenant_id=tenant_id,
                url=url
            )
            
            # Make request with retries
            response_data = await self._make_request_with_retries(
                "POST", url, json=body, headers=headers
            )
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            mcp_metrics.record_mcp_call_success(
                tool="reference_classes_query",
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            logger.info(
                "Successfully queried reference classes",
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            return response_data
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            mcp_metrics.record_mcp_call_failure(
                tool="reference_classes_query",
                tenant_id=tenant_id,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to query reference classes",
                query=query,
                tenant_id=tenant_id,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
    
    async def apply_adjustments(
        self, 
        rc_id: str, 
        adjustments: Dict[str, Any], 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Apply adjustments to reference class facts."""
        start_time = time.time()
        
        try:
            # Create MCP JWT
            mcp_jwt = create_mcp_jwt(tenant_id, scope="rc.write")
            
            # Prepare request
            url = urljoin(self.base_url, f"/reference_classes/{rc_id}/adjustments")
            headers = {
                "Authorization": f"Bearer {mcp_jwt}",
                "Content-Type": "application/json",
                "X-Tenant-ID": tenant_id,
            }
            
            # Add HMAC signature
            body = adjustments
            hmac_headers = hmac_signer.sign_request("POST", url, body=str(body).encode())
            headers.update(hmac_headers)
            
            logger.info(
                "Applying adjustments to reference class",
                rc_id=rc_id,
                adjustments=adjustments,
                tenant_id=tenant_id,
                url=url
            )
            
            # Make request with retries
            response_data = await self._make_request_with_retries(
                "POST", url, json=body, headers=headers
            )
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            mcp_metrics.record_mcp_call_success(
                tool="adjustments_apply",
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            logger.info(
                "Successfully applied adjustments",
                rc_id=rc_id,
                tenant_id=tenant_id,
                latency_ms=latency_ms
            )
            
            return response_data
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            mcp_metrics.record_mcp_call_failure(
                tool="adjustments_apply",
                tenant_id=tenant_id,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to apply adjustments",
                rc_id=rc_id,
                adjustments=adjustments,
                tenant_id=tenant_id,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
    
    async def _make_request_with_retries(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retries."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, **kwargs)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=json, **kwargs)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ValueError(f"Reference class not found: {e.response.text}")
                elif e.response.status_code >= 500:
                    last_exception = e
                    if attempt < self.max_retries:
                        await self._wait_before_retry(attempt)
                        continue
                    else:
                        raise
                else:
                    raise
                    
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self.max_retries:
                    await self._wait_before_retry(attempt)
                    continue
                else:
                    raise
                    
            except Exception as e:
                raise
        
        # If we get here, all retries failed
        raise last_exception or Exception("All retry attempts failed")
    
    async def _wait_before_retry(self, attempt: int) -> None:
        """Wait before retry with exponential backoff and jitter."""
        base_delay = 0.1  # 100ms base delay
        max_delay = 2.0   # 2 second max delay
        
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter (±20%)
        jitter = delay * 0.2 * (2 * asyncio.get_event_loop().time() % 1 - 1)
        delay += jitter
        
        logger.info(f"Retrying in {delay:.2f}s (attempt {attempt + 1})")
        await asyncio.sleep(delay)
