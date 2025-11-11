"""Chat endpoint for estimate generation."""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

import structlog
from app.core.security import get_current_user
from app.rcf.schemas import ChatRequest, ChatResponse
from app.rcf.orchestrator import RCFOrchestrator
from app.clients.mcp import MCPClient
from app.clients.openai_client import OpenAIClient
from app.storage.audit import AuditStorage
from app.storage.estimates import EstimateStorage
from app.observability.metrics import http_metrics

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def create_estimate(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ChatResponse:
    """
    Create an estimate from a chat message.
    
    This endpoint:
    1. Normalizes the chat message to extract project attributes
    2. Fetches reference class facts from the MCP server
    3. Applies policy modifiers
    4. Generates the estimate using OpenAI
    5. Returns a structured estimate response
    """
    start_time = time.time()
    
    try:
        # Extract user information
        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        user_email = current_user["email"]
        
        logger.info(
            "Processing chat request",
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=request.session_id,
            message_length=len(request.message)
        )
        
        # Initialize clients and storage
        mcp_client = MCPClient()
        openai_client = OpenAIClient()
        
        # Initialize storage (optional)
        audit_storage = AuditStorage() if hasattr(AuditStorage, 'is_configured') else None
        estimate_storage = EstimateStorage() if hasattr(EstimateStorage, 'is_configured') else None
        
        # Create orchestrator
        orchestrator = RCFOrchestrator(
            mcp_client=mcp_client,
            openai_client=openai_client,
            audit_storage=audit_storage,
            estimate_storage=estimate_storage
        )
        
        # Generate estimate
        response = await orchestrator.create_estimate(
            message=request.message,
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            session_id=request.session_id
        )
        
        # Record success metrics
        latency_ms = int((time.time() - start_time) * 1000)
        http_metrics.record_request_success(
            route="/chat",
            method="POST",
            tenant_id=tenant_id,
            latency_ms=latency_ms
        )
        
        logger.info(
            "Chat request completed successfully",
            trace_id=response.trace_id,
            tenant_id=tenant_id,
            user_id=user_id,
            latency_ms=latency_ms
        )
        
        return response
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Record failure metrics
        http_metrics.record_request_failure(
            route="/chat",
            method="POST",
            tenant_id=current_user.get("tenant_id", "unknown"),
            status_code=500,
            latency_ms=latency_ms
        )
        
        logger.error(
            "Chat request failed",
            tenant_id=current_user.get("tenant_id"),
            user_id=current_user.get("user_id"),
            error=str(e),
            latency_ms=latency_ms,
            exc_info=True
        )
        
        # Return appropriate error response
        if "MCP" in str(e) or "reference class" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reference class found for the specified project type. Please provide more details about your project."
            )
        elif "OpenAI" in str(e) or "LLM" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Estimate generation service is temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while generating the estimate. Please try again."
            )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the chat service."""
    return {"status": "healthy", "service": "chat"}


@router.get("/estimate/{estimate_id}")
async def get_estimate(
    estimate_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a previously generated estimate.
    
    This endpoint allows users to retrieve estimates they've generated.
    """
    try:
        # Initialize storage
        estimate_storage = EstimateStorage()
        
        # Get estimate
        estimate = await estimate_storage.get_estimate(estimate_id)
        
        if not estimate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estimate not found"
            )
        
        # Check tenant access
        if estimate["tenant_id"] != current_user["tenant_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this estimate"
            )
        
        return estimate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve estimate",
            estimate_id=estimate_id,
            user_id=current_user.get("user_id"),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve estimate"
        )
