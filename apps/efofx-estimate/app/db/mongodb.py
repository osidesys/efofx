"""
MongoDB connection and database management for efOfX Estimation Service.

This module provides MongoDB connection management, database access,
and collection utilities for the estimation service.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.constants import DB_COLLECTIONS

logger = logging.getLogger(__name__)

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Create database connection."""
    global _client, _database
    
    try:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
        _database = _client[settings.MONGO_DB_NAME]
        
        # Test the connection
        await _client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    global _client
    
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return _database


def get_collection(collection_name: str):
    """Get collection instance."""
    db = get_database()
    return db[collection_name]


@asynccontextmanager
async def get_db_session():
    """Database session context manager."""
    if not _database:
        await connect_to_mongo()
    
    try:
        yield _database
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


# Collection access functions
def get_tenants_collection():
    """Get tenants collection."""
    return get_collection(DB_COLLECTIONS["TENANTS"])


def get_reference_classes_collection():
    """Get reference classes collection."""
    return get_collection(DB_COLLECTIONS["REFERENCE_CLASSES"])


def get_reference_projects_collection():
    """Get reference projects collection."""
    return get_collection(DB_COLLECTIONS["REFERENCE_PROJECTS"])


def get_estimates_collection():
    """Get estimates collection."""
    return get_collection(DB_COLLECTIONS["ESTIMATES"])


def get_feedback_collection():
    """Get feedback collection."""
    return get_collection(DB_COLLECTIONS["FEEDBACK"])


def get_chat_sessions_collection():
    """Get chat sessions collection."""
    return get_collection(DB_COLLECTIONS["CHAT_SESSIONS"])


# Database utilities
async def create_indexes():
    """Create database indexes for optimal performance."""
    try:
        # Tenants collection indexes
        tenants_collection = get_tenants_collection()
        await tenants_collection.create_index("api_key", unique=True)
        await tenants_collection.create_index("name")
        
        # Reference classes collection indexes
        ref_classes_collection = get_reference_classes_collection()
        await ref_classes_collection.create_index("name", unique=True)
        await ref_classes_collection.create_index("category")
        await ref_classes_collection.create_index("regions")
        
        # Reference projects collection indexes
        ref_projects_collection = get_reference_projects_collection()
        await ref_projects_collection.create_index("project_id", unique=True)
        await ref_projects_collection.create_index("reference_class")
        await ref_projects_collection.create_index("region")
        await ref_projects_collection.create_index("completion_date")
        
        # Estimates collection indexes
        estimates_collection = get_estimates_collection()
        await estimates_collection.create_index("session_id", unique=True)
        await estimates_collection.create_index("tenant_id")
        await estimates_collection.create_index("status")
        await estimates_collection.create_index("created_at")
        
        # Feedback collection indexes
        feedback_collection = get_feedback_collection()
        await feedback_collection.create_index("estimation_session_id")
        await feedback_collection.create_index("tenant_id")
        await feedback_collection.create_index("feedback_type")
        await feedback_collection.create_index("created_at")
        
        # Chat sessions collection indexes
        chat_sessions_collection = get_chat_sessions_collection()
        await chat_sessions_collection.create_index("session_id", unique=True)
        await chat_sessions_collection.create_index("tenant_id")
        await chat_sessions_collection.create_index("estimation_session_id")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")
        raise


async def health_check():
    """Check database health."""
    try:
        if _database is None:
            return False
        await _database.command("ping")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_database_stats():
    """Get database statistics."""
    try:
        if _database is None:
            return None
        stats = await _database.command("dbStats")
        return {
            "collections": stats.get("collections", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "index_size": stats.get("indexSize", 0)
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return None 