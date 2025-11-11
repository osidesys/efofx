"""
Tenant model for efOfX Estimation Service.

This module defines the tenant data model used for multitenancy support.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic compatibility."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_after_validator_function(
            cls._validate,
            handler(source_type),
        )
    
    @classmethod
    def _validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class Tenant(BaseModel):
    """Tenant model for multitenancy support."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Tenant name")
    api_key: str = Field(..., description="API key for authentication")
    openai_api_key: Optional[str] = Field(None, description="Tenant-specific OpenAI API key")
    regions: List[str] = Field(default=[], description="Allowed regions for estimation")
    max_estimations_per_month: int = Field(default=1000, description="Monthly estimation limit")
    is_active: bool = Field(default=True, description="Whether tenant is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = Field(default_factory=dict, description="Tenant-specific settings")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Acme Construction",
                "api_key": "sk_acme_123456789",
                "openai_api_key": "sk-openai-tenant-key",
                "regions": ["SoCal - Coastal", "NorCal - Bay Area"],
                "max_estimations_per_month": 1000,
                "is_active": True,
                "settings": {
                    "default_confidence_threshold": 0.7,
                    "enable_image_upload": True
                }
            }
        }


class TenantCreate(BaseModel):
    """Model for creating a new tenant."""
    
    name: str = Field(..., description="Tenant name")
    api_key: str = Field(..., description="API key for authentication")
    openai_api_key: Optional[str] = Field(None, description="Tenant-specific OpenAI API key")
    regions: List[str] = Field(default=[], description="Allowed regions for estimation")
    max_estimations_per_month: int = Field(default=1000, description="Monthly estimation limit")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Tenant-specific settings")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Acme Construction",
                "api_key": "sk_acme_123456789",
                "openai_api_key": "sk-openai-tenant-key",
                "regions": ["SoCal - Coastal", "NorCal - Bay Area"],
                "max_estimations_per_month": 1000,
                "settings": {
                    "default_confidence_threshold": 0.7,
                    "enable_image_upload": True
                }
            }
        }


class TenantUpdate(BaseModel):
    """Model for updating an existing tenant."""
    
    name: Optional[str] = Field(None, description="Tenant name")
    openai_api_key: Optional[str] = Field(None, description="Tenant-specific OpenAI API key")
    regions: Optional[List[str]] = Field(None, description="Allowed regions for estimation")
    max_estimations_per_month: Optional[int] = Field(None, description="Monthly estimation limit")
    is_active: Optional[bool] = Field(None, description="Whether tenant is active")
    settings: Optional[Dict[str, Any]] = Field(None, description="Tenant-specific settings")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Acme Construction Updated",
                "regions": ["SoCal - Coastal", "NorCal - Bay Area", "Arizona - Phoenix"],
                "max_estimations_per_month": 2000,
                "is_active": True,
                "settings": {
                    "default_confidence_threshold": 0.8,
                    "enable_image_upload": True
                }
            }
        } 