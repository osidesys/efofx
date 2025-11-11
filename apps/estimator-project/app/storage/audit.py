"""Audit storage for estimate operations."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import structlog

from app.core.config import settings
from app.rcf.schemas import Audit

logger = structlog.get_logger(__name__)


class AuditStorage:
    """Storage for audit records."""
    
    def __init__(self):
        self.is_configured = bool(settings.audit_db_uri)
        if not self.is_configured:
            logger.warning("Audit storage not configured - audit records will not be persisted")
    
    async def store_audit(
        self,
        trace_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        rc_id: str,
        facts_block: Dict[str, Any],
        response: Dict[str, Any],
        latency_ms: int
    ) -> None:
        """Store audit record for successful estimate."""
        if not self.is_configured:
            return
        
        try:
            audit_record = Audit(
                when=datetime.utcnow().isoformat(),
                tenant_id=tenant_id,
                sub=user_id,
                email=user_email,
                action="estimate.create",
                rc_id=rc_id,
                distribution_version=facts_block.get("distribution_version", 1),
                estimate_id=response.get("trace_id", trace_id),
                latency_ms=latency_ms,
                status="success"
            )
            
            await self._persist_audit(audit_record)
            
            logger.info(
                "Audit record stored",
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                rc_id=rc_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to store audit record",
                trace_id=trace_id,
                tenant_id=tenant_id,
                error=str(e),
                exc_info=True
            )
    
    async def store_audit_failure(
        self,
        trace_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        rc_id: str,
        error_message: str,
        latency_ms: int
    ) -> None:
        """Store audit record for failed estimate."""
        if not self.is_configured:
            return
        
        try:
            audit_record = Audit(
                when=datetime.utcnow().isoformat(),
                tenant_id=tenant_id,
                sub=user_id,
                email=user_email,
                action="estimate.create",
                rc_id=rc_id,
                distribution_version=1,  # Default for failures
                estimate_id=trace_id,
                latency_ms=latency_ms,
                status="failure"
            )
            
            await self._persist_audit(audit_record)
            
            logger.info(
                "Failure audit record stored",
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                rc_id=rc_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to store failure audit record",
                trace_id=trace_id,
                tenant_id=tenant_id,
                error=str(e),
                exc_info=True
            )
    
    async def get_audit_records(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Audit]:
        """Retrieve audit records for a tenant."""
        if not self.is_configured:
            return []
        
        try:
            # This would be implemented based on the actual database backend
            # For now, return empty list
            logger.info(
                "Retrieving audit records",
                tenant_id=tenant_id,
                user_id=user_id,
                limit=limit
            )
            
            return []
            
        except Exception as e:
            logger.error(
                "Failed to retrieve audit records",
                tenant_id=tenant_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            return []
    
    async def _persist_audit(self, audit_record: Audit) -> None:
        """Persist audit record to storage backend."""
        # This would be implemented based on the actual database backend
        # For now, just log the record
        
        if settings.audit_db_uri.startswith("mongodb"):
            await self._persist_to_mongodb(audit_record)
        elif settings.audit_db_uri.startswith("postgresql"):
            await self._persist_to_postgresql(audit_record)
        else:
            logger.warning(f"Unsupported database type: {settings.audit_db_uri}")
    
    async def _persist_to_mongodb(self, audit_record: Audit) -> None:
        """Persist audit record to MongoDB."""
        # This would be implemented with actual MongoDB client
        logger.info(
            "Would persist to MongoDB",
            audit_record=audit_record.dict()
        )
    
    async def _persist_to_postgresql(self, audit_record: Audit) -> None:
        """Persist audit record to PostgreSQL."""
        # This would be implemented with actual PostgreSQL client
        logger.info(
            "Would persist to PostgreSQL",
            audit_record=audit_record.dict()
        )
    
    async def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """Clean up old audit records."""
        if not self.is_configured:
            return 0
        
        try:
            logger.info(
                "Cleaning up old audit records",
                days_to_keep=days_to_keep
            )
            
            # This would be implemented based on the actual database backend
            # For now, return 0
            return 0
            
        except Exception as e:
            logger.error(
                "Failed to cleanup old audit records",
                days_to_keep=days_to_keep,
                error=str(e),
                exc_info=True
            )
            return 0
