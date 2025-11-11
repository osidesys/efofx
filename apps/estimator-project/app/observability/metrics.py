"""Prometheus metrics for the EFOFX Estimate Service."""

from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Optional


class HTTPMetrics:
    """HTTP request metrics."""
    
    def __init__(self):
        self.requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["route", "method", "status", "tenant_id"]
        )
        
        self.request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["route", "method", "tenant_id"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.requests_in_progress = Gauge(
            "http_requests_in_progress",
            "Number of HTTP requests currently in progress",
            ["route", "method", "tenant_id"]
        )
    
    def record_request_success(
        self, 
        route: str, 
        method: str, 
        tenant_id: str, 
        latency_ms: int
    ) -> None:
        """Record successful HTTP request."""
        self.requests_total.labels(
            route=route,
            method=method,
            status="200",
            tenant_id=tenant_id
        ).inc()
        
        self.request_duration.labels(
            route=route,
            method=method,
            tenant_id=tenant_id
        ).observe(latency_ms / 1000.0)
    
    def record_request_failure(
        self, 
        route: str, 
        method: str, 
        tenant_id: str, 
        status_code: int, 
        latency_ms: int
    ) -> None:
        """Record failed HTTP request."""
        self.requests_total.labels(
            route=route,
            method=method,
            status=str(status_code),
            tenant_id=tenant_id
        ).inc()
        
        self.request_duration.labels(
            route=route,
            method=method,
            tenant_id=tenant_id
        ).observe(latency_ms / 1000.0)


class MCPMetrics:
    """MCP call metrics."""
    
    def __init__(self):
        self.call_latency_ms = Histogram(
            "mcp_call_latency_ms",
            "MCP call latency in milliseconds",
            ["tool", "tenant_id"],
            buckets=[50, 100, 200, 300, 400, 500, 750, 1000]
        )
        
        self.calls_total = Counter(
            "mcp_calls_total",
            "Total MCP calls",
            ["tool", "tenant_id", "status"]
        )
        
        self.calls_in_progress = Gauge(
            "mcp_calls_in_progress",
            "Number of MCP calls currently in progress",
            ["tool", "tenant_id"]
        )
    
    def record_mcp_call_success(
        self, 
        tool: str, 
        tenant_id: str, 
        latency_ms: int
    ) -> None:
        """Record successful MCP call."""
        self.call_latency_ms.labels(
            tool=tool,
            tenant_id=tenant_id
        ).observe(latency_ms)
        
        self.calls_total.labels(
            tool=tool,
            tenant_id=tenant_id,
            status="success"
        ).inc()
    
    def record_mcp_call_failure(
        self, 
        tool: str, 
        tenant_id: str, 
        error_type: str, 
        latency_ms: int
    ) -> None:
        """Record failed MCP call."""
        self.call_latency_ms.labels(
            tool=tool,
            tenant_id=tenant_id
        ).observe(latency_ms)
        
        self.calls_total.labels(
            tool=tool,
            tenant_id=tenant_id,
            status="failure"
        ).inc()


class LLMMetrics:
    """LLM call metrics."""
    
    def __init__(self):
        self.call_latency_ms = Histogram(
            "llm_latency_ms",
            "LLM call latency in milliseconds",
            ["model"],
            buckets=[100, 250, 500, 1000, 2000, 5000, 10000, 30000]
        )
        
        self.calls_total = Counter(
            "llm_calls_total",
            "Total LLM calls",
            ["model", "status"]
        )
        
        self.tokens_total = Counter(
            "llm_tokens_total",
            "Total tokens processed",
            ["model", "type"]
        )
        
        self.calls_in_progress = Gauge(
            "llm_calls_in_progress",
            "Number of LLM calls currently in progress",
            ["model"]
        )
    
    def record_llm_call_success(
        self, 
        model: str, 
        latency_ms: int, 
        tokens_used: int
    ) -> None:
        """Record successful LLM call."""
        self.call_latency_ms.labels(model=model).observe(latency_ms)
        
        self.calls_total.labels(
            model=model,
            status="success"
        ).inc()
        
        self.tokens_total.labels(
            model=model,
            type="total"
        ).inc(tokens_used)
    
    def record_llm_call_failure(
        self, 
        model: str, 
        error_type: str, 
        latency_ms: int
    ) -> None:
        """Record failed LLM call."""
        self.call_latency_ms.labels(model=model).observe(latency_ms)
        
        self.calls_total.labels(
            model=model,
            status="failure"
        ).inc()


class EstimateMetrics:
    """Estimate generation metrics."""
    
    def __init__(self):
        self.estimates_created_total = Counter(
            "estimate_created_total",
            "Total estimates created",
            ["tenant_id", "rc_id"]
        )
        
        self.estimates_failed_total = Counter(
            "estimate_failed_total",
            "Total estimate failures",
            ["tenant_id", "error_type"]
        )
        
        self.estimate_creation_duration = Histogram(
            "estimate_creation_duration_seconds",
            "Estimate creation duration in seconds",
            ["tenant_id", "rc_id"],
            buckets=[0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
        )
        
        self.estimates_in_progress = Gauge(
            "estimates_in_progress",
            "Number of estimates currently being created",
            ["tenant_id"]
        )
    
    def record_estimate_created(
        self, 
        tenant_id: str, 
        rc_id: str, 
        latency_ms: int
    ) -> None:
        """Record successful estimate creation."""
        self.estimates_created_total.labels(
            tenant_id=tenant_id,
            rc_id=rc_id
        ).inc()
        
        self.estimate_creation_duration.labels(
            tenant_id=tenant_id,
            rc_id=rc_id
        ).observe(latency_ms / 1000.0)
    
    def record_estimate_failed(
        self, 
        tenant_id: str, 
        error_type: str
    ) -> None:
        """Record estimate creation failure."""
        self.estimates_failed_total.labels(
            tenant_id=tenant_id,
            error_type=error_type
        ).inc()


class CacheMetrics:
    """Cache performance metrics."""
    
    def __init__(self):
        self.cache_hits_total = Counter(
            "cache_hits_total",
            "Total cache hits",
            ["cache_type", "tenant_id"]
        )
        
        self.cache_misses_total = Counter(
            "cache_misses_total",
            "Total cache misses",
            ["cache_type", "tenant_id"]
        )
        
        self.cache_size = Gauge(
            "cache_size",
            "Current cache size",
            ["cache_type", "tenant_id"]
        )
    
    def record_cache_hit(self, cache_type: str, tenant_id: str) -> None:
        """Record cache hit."""
        self.cache_hits_total.labels(
            cache_type=cache_type,
            tenant_id=tenant_id
        ).inc()
    
    def record_cache_miss(self, cache_type: str, tenant_id: str) -> None:
        """Record cache miss."""
        self.cache_misses_total.labels(
            cache_type=cache_type,
            tenant_id=tenant_id
        ).inc()
    
    def set_cache_size(self, cache_type: str, tenant_id: str, size: int) -> None:
        """Set current cache size."""
        self.cache_size.labels(
            cache_type=cache_type,
            tenant_id=tenant_id
        ).set(size)


# Global metric instances
http_metrics = HTTPMetrics()
mcp_metrics = MCPMetrics()
llm_metrics = LLMMetrics()
estimate_metrics = EstimateMetrics()
cache_metrics = CacheMetrics()


def setup_metrics() -> None:
    """Setup and register all metrics."""
    # This function is called during application startup
    # All metrics are automatically registered when the classes are instantiated
    pass
