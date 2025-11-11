"""Reference Class Facts (RCF) orchestrator for the estimation workflow."""

import asyncio
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
from app.rcf.schemas import (
    ProjectAttributes, FactsBlock, EstimateResponse, 
    EstimateJSON, CostDist, TimeDist, EstimateBucket
)
from app.rcf.normalize import attribute_normalizer
from app.clients.mcp import MCPClient
from app.clients.openai_client import OpenAIClient
from app.storage.audit import AuditStorage
from app.storage.estimates import EstimateStorage
from app.observability.metrics import estimate_metrics

logger = structlog.get_logger(__name__)


class RCFOrchestrator:
    """Orchestrates the complete RCF estimation workflow."""
    
    def __init__(
        self,
        mcp_client: MCPClient,
        openai_client: OpenAIClient,
        audit_storage: Optional[AuditStorage] = None,
        estimate_storage: Optional[EstimateStorage] = None
    ):
        self.mcp_client = mcp_client
        self.openai_client = openai_client
        self.audit_storage = audit_storage
        self.estimate_storage = estimate_storage
    
    async def create_estimate(
        self,
        message: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        session_id: Optional[str] = None
    ) -> EstimateResponse:
        """Create a complete estimate from chat message."""
        start_time = time.time()
        trace_id = f"trc-{uuid.uuid4().hex[:8]}"
        
        try:
            logger.info(
                "Starting estimate creation",
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id
            )
            
            # Step 1: Normalize and extract attributes
            attrs = attribute_normalizer.extract_attributes(message)
            logger.info(
                "Extracted project attributes",
                trace_id=trace_id,
                attributes=attrs.dict()
            )
            
            # Step 2: Get reference class ID
            rc_id = attribute_normalizer.get_reference_class_id(attrs)
            logger.info(
                "Generated reference class ID",
                trace_id=trace_id,
                rc_id=rc_id
            )
            
            # Step 3: Fetch reference class facts from MCP
            facts_block = await self._fetch_reference_class_facts(rc_id, tenant_id)
            logger.info(
                "Retrieved reference class facts",
                trace_id=trace_id,
                rc_id=rc_id,
                distribution_version=facts_block.distribution_version
            )
            
            # Step 4: Apply policy modifiers
            policy_result = attribute_normalizer.apply_policy_modifiers(attrs)
            facts_block.modifiers_applied = policy_result["modifiers"]
            facts_block.policy = {
                "total_factor": policy_result["total_factor"],
                "attributes": attrs.dict()
            }
            
            # Step 5: Call LLM for estimate generation
            estimate_result = await self._generate_estimate_with_llm(facts_block, message)
            logger.info(
                "Generated estimate with LLM",
                trace_id=trace_id,
                rc_id=rc_id
            )
            
            # Step 6: Create response
            response = EstimateResponse(
                summary=estimate_result["summary"],
                estimate=estimate_result["estimate"],
                reference={
                    "reference_class_id": rc_id,
                    "distribution_version": facts_block.distribution_version,
                    "attributes": attrs.dict(),
                    "modifiers": policy_result["modifiers"]
                },
                trace_id=trace_id
            )
            
            # Step 7: Store audit and estimate (if configured)
            await self._store_results(
                trace_id, tenant_id, user_id, user_email, rc_id,
                facts_block, response, start_time
            )
            
            # Step 8: Record metrics
            latency_ms = int((time.time() - start_time) * 1000)
            estimate_metrics.record_estimate_created(
                tenant_id=tenant_id,
                rc_id=rc_id,
                latency_ms=latency_ms
            )
            
            logger.info(
                "Estimate creation completed successfully",
                trace_id=trace_id,
                latency_ms=latency_ms
            )
            
            return response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "Estimate creation failed",
                trace_id=trace_id,
                tenant_id=tenant_id,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            
            # Record failure metrics
            estimate_metrics.record_estimate_failed(
                tenant_id=tenant_id,
                error_type=type(e).__name__
            )
            
            # Store audit record for failure
            if self.audit_storage:
                await self._store_audit_failure(
                    trace_id, tenant_id, user_id, user_email,
                    rc_id, str(e), latency_ms
                )
            
            raise
    
    async def _fetch_reference_class_facts(
        self, 
        rc_id: str, 
        tenant_id: str
    ) -> FactsBlock:
        """Fetch reference class facts from MCP server."""
        try:
            facts = await self.mcp_client.get_reference_class_facts(rc_id, tenant_id)
            return FactsBlock(**facts)
        except Exception as e:
            logger.error(
                "Failed to fetch reference class facts",
                rc_id=rc_id,
                tenant_id=tenant_id,
                error=str(e)
            )
            raise
    
    async def _generate_estimate_with_llm(
        self, 
        facts_block: FactsBlock, 
        original_message: str
    ) -> Dict[str, Any]:
        """Generate estimate using OpenAI LLM."""
        try:
            # Create prompt for LLM
            prompt = self._create_llm_prompt(facts_block, original_message)
            
            # Call OpenAI
            response = await self.openai_client.generate_estimate(prompt)
            
            # Parse and validate response
            estimate_data = self._parse_llm_response(response)
            
            # Validate against schema
            validated_estimate = EstimateJSON(**estimate_data)
            
            return {
                "summary": response.get("summary", ""),
                "estimate": validated_estimate
            }
            
        except Exception as e:
            logger.error(
                "Failed to generate estimate with LLM",
                error=str(e),
                facts_block_id=facts_block.reference_class_id
            )
            raise
    
    def _create_llm_prompt(self, facts_block: FactsBlock, original_message: str) -> str:
        """Create prompt for LLM based on facts block."""
        prompt = f"""
You are an expert estimator. Generate a detailed estimate based on the following reference class facts and user request.

USER REQUEST:
{original_message}

REFERENCE CLASS FACTS:
- ID: {facts_block.reference_class_id}
- Version: {facts_block.distribution_version}
- Cost Distribution: P50: ${facts_block.cost_distribution.P50:,}, P80: ${facts_block.cost_distribution.P80:,}, P95: ${facts_block.cost_distribution.P95:,}
- Time Distribution: P50: {facts_block.time_distribution.P50} weeks, P80: {facts_block.time_distribution.P80} weeks, P95: {facts_block.time_distribution.P95} weeks
- Cost Breakdown: {', '.join([f'{k}: {v*100:.1f}%' for k, v in facts_block.cost_breakdown.items()])}

POLICY MODIFIERS:
{self._format_modifiers(facts_block.modifiers_applied)}

INSTRUCTIONS:
1. Use ONLY the facts provided above - do not hallucinate numbers
2. Apply any policy modifiers to adjust the base estimates
3. Provide a clear, professional summary
4. Return structured data in the exact format specified

OUTPUT FORMAT:
{{
    "summary": "Professional estimate summary...",
    "estimate": {{
        "totals": {{
            "P50": <adjusted_p50_cost>,
            "P80": <adjusted_p80_cost>,
            "P95": <adjusted_p95_cost>
        }},
        "breakdown": [
            {{
                "bucket": "<category_name>",
                "amountP50": <p50_amount_for_category>
            }}
        ],
        "time_weeks": {{
            "P50": <adjusted_p50_weeks>,
            "P80": <adjusted_p80_weeks>,
            "P95": <adjusted_p95_weeks>
        }}
    }}
}}
"""
        return prompt
    
    def _format_modifiers(self, modifiers: list) -> str:
        """Format policy modifiers for LLM prompt."""
        if not modifiers:
            return "None applied"
        
        formatted = []
        for mod in modifiers:
            formatted.append(f"- {mod['type']}: {mod['factor']}x ({mod['reason']})")
        
        return "\n".join(formatted)
    
    def _parse_llm_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Extract estimate data from response
            if "estimate" in response:
                return response["estimate"]
            elif "choices" in response and response["choices"]:
                # Handle OpenAI API response format
                content = response["choices"][0]["message"]["content"]
                # This is a simplified parser - in production you'd want more robust JSON extraction
                import json
                return json.loads(content)
            else:
                raise ValueError("Unexpected LLM response format")
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError(f"Invalid LLM response format: {e}")
    
    async def _store_results(
        self,
        trace_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        rc_id: str,
        facts_block: FactsBlock,
        response: EstimateResponse,
        start_time: float
    ) -> None:
        """Store audit record and estimate (if configured)."""
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Store audit record
        if self.audit_storage:
            await self.audit_storage.store_audit(
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                rc_id=rc_id,
                facts_block=facts_block.dict(),
                response=response.dict(),
                latency_ms=latency_ms
            )
        
        # Store estimate (optional)
        if self.estimate_storage:
            await self.estimate_storage.store_estimate(
                trace_id=trace_id,
                tenant_id=tenant_id,
                rc_id=rc_id,
                facts_block=facts_block.dict(),
                response=response.dict(),
                latency_ms=latency_ms
            )
    
    async def _store_audit_failure(
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
        if self.audit_storage:
            await self.audit_storage.store_audit_failure(
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                rc_id=rc_id,
                error_message=error_message,
                latency_ms=latency_ms
            )
