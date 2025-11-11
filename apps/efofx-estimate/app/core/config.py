"""
Configuration settings for efOfX Estimation Service.

This module defines all configuration settings using Pydantic BaseSettings
for environment variable management and validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    DEBUG: bool = Field(default=False, env="DEBUG")
    APP_NAME: str = Field(default="efOfX Estimation Service", env="APP_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Database
    MONGO_URI: str = Field(..., env="MONGO_URI")
    MONGO_DB_NAME: str = Field(default="efofx_estimate", env="MONGO_DB_NAME")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Estimation
    MAX_ESTIMATION_SESSIONS: int = Field(default=100, env="MAX_ESTIMATION_SESSIONS")
    SESSION_TIMEOUT_MINUTES: int = Field(default=30, env="SESSION_TIMEOUT_MINUTES")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"], 
        env="ALLOWED_IMAGE_TYPES"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 