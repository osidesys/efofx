"""Structured logging configuration for the EFOFX Estimate Service."""

import sys
import logging
from typing import Any, Dict
from datetime import datetime

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import (
    TimeStamper, JSONRenderer, add_log_level, 
    StackInfoRenderer, format_exc_info
)


def setup_logging() -> None:
    """Setup structured logging with structlog."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            TimeStamper(fmt="iso"),
            
            # Add log level
            add_log_level,
            
            # Add stack info for errors
            StackInfoRenderer(),
            
            # Add exception info
            format_exc_info,
            
            # Add caller info
            structlog.processors.CallsiteParameterAdder(
                parameters=["func_name", "lineno", "module"]
            ),
            
            # Render as JSON
            JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, "INFO")
    )
    
    # Set log level for third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Create root logger
    root_logger = structlog.get_logger()
    root_logger.info("Logging system initialized")


class StructuredLogger:
    """Enhanced structured logger with common fields."""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """Bind additional context to the logger."""
        return StructuredLogger(self.logger.bind(**kwargs))
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with structured data."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with structured data."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with structured data."""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with structured data."""
        self.logger.debug(message, **kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with structured data and traceback."""
        self.logger.exception(message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def log_request_start(
    logger: StructuredLogger,
    method: str,
    url: str,
    client_ip: str = None,
    user_agent: str = None,
    **kwargs: Any
) -> None:
    """Log the start of an HTTP request."""
    logger.info(
        "Request started",
        method=method,
        url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        **kwargs
    )


def log_request_complete(
    logger: StructuredLogger,
    method: str,
    url: str,
    status_code: int,
    process_time: float,
    **kwargs: Any
) -> None:
    """Log the completion of an HTTP request."""
    logger.info(
        "Request completed",
        method=method,
        url=url,
        status_code=status_code,
        process_time=process_time,
        **kwargs
    )


def log_estimate_start(
    logger: StructuredLogger,
    trace_id: str,
    tenant_id: str,
    user_id: str,
    message: str,
    **kwargs: Any
) -> None:
    """Log the start of estimate generation."""
    logger.info(
        "Estimate generation started",
        trace_id=trace_id,
        tenant_id=tenant_id,
        user_id=user_id,
        message_length=len(message),
        **kwargs
    )


def log_estimate_complete(
    logger: StructuredLogger,
    trace_id: str,
    tenant_id: str,
    user_id: str,
    rc_id: str,
    latency_ms: int,
    **kwargs: Any
) -> None:
    """Log the completion of estimate generation."""
    logger.info(
        "Estimate generation completed",
        trace_id=trace_id,
        tenant_id=tenant_id,
        user_id=user_id,
        rc_id=rc_id,
        latency_ms=latency_ms,
        **kwargs
    )


def log_mcp_call(
    logger: StructuredLogger,
    tool: str,
    tenant_id: str,
    rc_id: str = None,
    latency_ms: int = None,
    **kwargs: Any
) -> None:
    """Log MCP call information."""
    log_data = {
        "tool": tool,
        "tenant_id": tenant_id,
        **kwargs
    }
    
    if rc_id:
        log_data["rc_id"] = rc_id
    
    if latency_ms:
        log_data["latency_ms"] = latency_ms
    
    logger.info("MCP call", **log_data)


def log_llm_call(
    logger: StructuredLogger,
    model: str,
    prompt_length: int = None,
    response_length: int = None,
    tokens_used: int = None,
    latency_ms: int = None,
    **kwargs: Any
) -> None:
    """Log LLM call information."""
    log_data = {
        "model": model,
        **kwargs
    }
    
    if prompt_length:
        log_data["prompt_length"] = prompt_length
    
    if response_length:
        log_data["response_length"] = response_length
    
    if tokens_used:
        log_data["tokens_used"] = tokens_used
    
    if latency_ms:
        log_data["latency_ms"] = latency_ms
    
    logger.info("LLM call", **log_data)


def log_security_event(
    logger: StructuredLogger,
    event_type: str,
    user_id: str = None,
    tenant_id: str = None,
    ip_address: str = None,
    **kwargs: Any
) -> None:
    """Log security-related events."""
    log_data = {
        "event_type": event_type,
        **kwargs
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if tenant_id:
        log_data["tenant_id"] = tenant_id
    
    if ip_address:
        log_data["ip_address"] = ip_address
    
    logger.warning("Security event", **log_data)


def log_performance_metric(
    logger: StructuredLogger,
    metric_name: str,
    value: float,
    unit: str = None,
    **kwargs: Any
) -> None:
    """Log performance metrics."""
    log_data = {
        "metric_name": metric_name,
        "value": value,
        **kwargs
    }
    
    if unit:
        log_data["unit"] = unit
    
    logger.info("Performance metric", **log_data)
