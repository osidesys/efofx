"""Configuration settings for the EFOFX Estimate Service."""

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_env: str = Field(default="dev", env="APP_ENV")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8080, env="APP_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # JWT Configuration
    jwt_public_key: str = Field(..., env="JWT_PUBLIC_KEY_PEM")
    jwt_issuer: str = Field(default="efofx-estimate", env="JWT_ISSUER")
    
    # MCP Configuration
    mcp_base_url: str = Field(..., env="MCP_BASE_URL")
    mcp_hmac_key_id: str = Field(..., env="HMAC_KEY_ID")
    mcp_hmac_secret: str = Field(..., env="HMAC_SECRET_B64")
    mcp_jwt_private_key: str = Field(..., env="MCP_JWT_PRIVATE_KEY")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # Prometheus Configuration
    prometheus_port: int = Field(default=9000, env="PROMETHEUS_PORT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration
    audit_db_uri: str = Field(default="", env="AUDIT_DB_URI")
    
    # Redis Configuration (Optional)
    redis_url: str = Field(default="", env="REDIS_URL")
    
    # Security
    allowed_hosts: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS",
        description="Comma-separated list of allowed hosts"
    )
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="Comma-separated list of CORS origins"
    )
    
    # Performance
    mcp_timeout: float = Field(default=5.0, env="MCP_TIMEOUT")
    llm_timeout: float = Field(default=30.0, env="LLM_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # Caching
    cache_ttl: int = Field(default=120, env="CACHE_TTL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Parse comma-separated lists
        if isinstance(self.allowed_hosts, str):
            self.allowed_hosts = [host.strip() for host in self.allowed_hosts.split(",")]
        
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() in ("prod", "production")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() in ("dev", "development")
    
    @property
    def has_redis(self) -> bool:
        """Check if Redis is configured."""
        return bool(self.redis_url)
    
    @property
    def has_audit_db(self) -> bool:
        """Check if audit database is configured."""
        return bool(self.audit_db_uri)


# Global settings instance
settings = Settings()
