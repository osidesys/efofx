"""Reference Class Facts (RCF) schemas and data models."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, conint, confloat, PositiveInt


class CostDist(BaseModel):
    """Cost distribution with percentiles."""
    P50: conint(ge=0) = Field(..., description="50th percentile cost")
    P80: conint(ge=0) = Field(..., description="80th percentile cost")
    P95: conint(ge=0) = Field(..., description="95th percentile cost")


class TimeDist(BaseModel):
    """Time distribution with percentiles."""
    P50: PositiveInt = Field(..., description="50th percentile time in weeks")
    P80: PositiveInt = Field(..., description="80th percentile time in weeks")
    P95: PositiveInt = Field(..., description="95th percentile time in weeks")


class FactsBlock(BaseModel):
    """Reference class facts block passed to LLM."""
    reference_class_id: str = Field(..., description="Reference class identifier")
    distribution_version: PositiveInt = Field(..., description="Distribution version")
    cost_distribution: CostDist = Field(..., description="Cost distribution")
    time_distribution: TimeDist = Field(..., description="Time distribution")
    cost_breakdown: Dict[str, confloat(ge=0, le=1)] = Field(
        ..., 
        description="Cost breakdown by category (0.0 to 1.0)"
    )
    modifiers_applied: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of modifiers applied to base estimates"
    )
    policy: Dict[str, Any] = Field(
        default_factory=dict,
        description="Policy information and rules"
    )


class EstimateBucket(BaseModel):
    """Individual cost bucket in estimate breakdown."""
    bucket: str = Field(..., description="Cost category name")
    amountP50: conint(ge=0) = Field(..., description="50th percentile amount for this bucket")


class EstimateJSON(BaseModel):
    """Structured estimate output."""
    totals: CostDist = Field(..., description="Total cost distribution")
    breakdown: List[EstimateBucket] = Field(..., description="Cost breakdown by category")
    time_weeks: TimeDist = Field(..., description="Time estimate distribution")


class EstimateResponse(BaseModel):
    """Complete estimate response."""
    summary: str = Field(..., description="Human-readable estimate summary")
    estimate: EstimateJSON = Field(..., description="Structured estimate data")
    reference: Dict[str, Any] = Field(..., description="Reference class information")
    trace_id: str = Field(..., description="Trace identifier for debugging")


class ChatRequest(BaseModel):
    """Chat endpoint request model."""
    message: str = Field(..., description="User's chat message")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class ChatResponse(BaseModel):
    """Chat endpoint response model."""
    summary: str = Field(..., description="Human-readable estimate summary")
    estimate: EstimateJSON = Field(..., description="Structured estimate data")
    reference: Dict[str, Any] = Field(..., description="Reference class information")
    trace_id: str = Field(..., description="Trace identifier for debugging")


class Session(BaseModel):
    """User session data (optional caching)."""
    session_id: str = Field(..., description="Unique session identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    attrs: Dict[str, Any] = Field(..., description="Extracted project attributes")
    last_rc_id: Optional[str] = Field(None, description="Last reference class used")
    created_at: str = Field(..., description="Session creation timestamp")


class Audit(BaseModel):
    """Audit record for every estimate."""
    when: str = Field(..., description="Audit timestamp")
    tenant_id: str = Field(..., description="Tenant identifier")
    sub: str = Field(..., description="User identifier")
    email: str = Field(..., description="User email")
    action: str = Field(..., description="Action performed")
    rc_id: str = Field(..., description="Reference class identifier")
    distribution_version: int = Field(..., description="Distribution version used")
    estimate_id: str = Field(..., description="Estimate identifier")
    latency_ms: int = Field(..., description="Request latency in milliseconds")
    status: str = Field(..., description="Request status")


class Estimate(BaseModel):
    """Stored estimate record (optional)."""
    estimate_id: str = Field(..., description="Unique estimate identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    reference_class_id: str = Field(..., description="Reference class identifier")
    facts_block: Dict[str, Any] = Field(..., description="Facts block passed to LLM")
    estimate_json: EstimateJSON = Field(..., description="Validated estimate output")
    summary_text: str = Field(..., description="Generated summary text")
    schema_version: int = Field(default=1, description="Schema version")
    created_at: str = Field(..., description="Creation timestamp")


class ProjectAttributes(BaseModel):
    """Normalized project attributes extracted from chat message."""
    category: str = Field(..., description="Project category (e.g., construction)")
    subcategory: str = Field(..., description="Project subcategory (e.g., pool)")
    region: str = Field(..., description="Geographic region (e.g., SoCal)")
    scope: str = Field(..., description="Project scope (e.g., medium)")
    complexity: Optional[str] = Field(None, description="Project complexity level")
    timeline: Optional[str] = Field(None, description="Timeline constraints")
    budget: Optional[str] = Field(None, description="Budget constraints")
