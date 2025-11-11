"""
Reference service for efOfX Estimation Service.

This module provides functionality for managing reference classes
and reference projects used in RCF estimation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.reference import ReferenceClass, ReferenceProject
from app.db.mongodb import get_reference_classes_collection, get_reference_projects_collection

logger = logging.getLogger(__name__)


class ReferenceService:
    """Service for handling reference classes and projects."""
    
    def __init__(self):
        self.classes_collection = get_reference_classes_collection()
        self.projects_collection = get_reference_projects_collection()
    
    async def get_reference_classes(self, category: Optional[str] = None) -> List[ReferenceClass]:
        """Get reference classes, optionally filtered by category."""
        try:
            query = {"is_active": True}
            if category:
                query["category"] = category
            
            cursor = self.classes_collection.find(query)
            classes_list = await cursor.to_list(length=None)
            
            return [ReferenceClass(**cls) for cls in classes_list]
            
        except Exception as e:
            logger.error(f"Error getting reference classes: {e}")
            raise
    
    async def get_reference_class(self, name: str) -> Optional[ReferenceClass]:
        """Get specific reference class by name."""
        try:
            class_data = await self.classes_collection.find_one({"name": name, "is_active": True})
            
            if class_data:
                return ReferenceClass(**class_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reference class: {e}")
            raise
    
    async def get_reference_projects(
        self, 
        reference_class: str, 
        region: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get reference projects for a specific class and region."""
        try:
            cursor = self.projects_collection.find({
                "reference_class": reference_class,
                "region": region,
                "is_active": True
            }).sort("quality_score", -1).limit(limit)
            
            projects_list = await cursor.to_list(length=None)
            
            # Convert to simple dict format for easier processing
            return [
                {
                    "project_id": p.get("project_id"),
                    "total_cost": p.get("total_cost"),
                    "timeline_weeks": p.get("timeline_weeks"),
                    "team_size": p.get("team_size"),
                    "cost_breakdown": p.get("cost_breakdown"),
                    "quality_score": p.get("quality_score"),
                    "description": p.get("description"),
                    "metadata": p.get("metadata", {})
                }
                for p in projects_list
            ]
            
        except Exception as e:
            logger.error(f"Error getting reference projects: {e}")
            return []
    
    async def get_reference_project(self, project_id: str) -> Optional[ReferenceProject]:
        """Get specific reference project by ID."""
        try:
            project_data = await self.projects_collection.find_one({
                "project_id": project_id,
                "is_active": True
            })
            
            if project_data:
                return ReferenceProject(**project_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting reference project: {e}")
            raise
    
    async def create_reference_class(self, class_data: Dict[str, Any]) -> str:
        """Create a new reference class."""
        try:
            # Check if class already exists
            existing = await self.classes_collection.find_one({"name": class_data["name"]})
            if existing:
                raise ValueError("Reference class already exists")
            
            # Create new reference class
            reference_class = ReferenceClass(**class_data)
            result = await self.classes_collection.insert_one(reference_class.dict(by_alias=True))
            
            logger.info(f"Reference class created: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating reference class: {e}")
            raise
    
    async def create_reference_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new reference project."""
        try:
            # Check if project already exists
            existing = await self.projects_collection.find_one({"project_id": project_data["project_id"]})
            if existing:
                raise ValueError("Reference project already exists")
            
            # Create new reference project
            reference_project = ReferenceProject(**project_data)
            result = await self.projects_collection.insert_one(reference_project.dict(by_alias=True))
            
            logger.info(f"Reference project created: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating reference project: {e}")
            raise
    
    async def update_reference_class(self, name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing reference class."""
        try:
            result = await self.classes_collection.update_one(
                {"name": name},
                {"$set": {**updates, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating reference class: {e}")
            raise
    
    async def update_reference_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing reference project."""
        try:
            result = await self.projects_collection.update_one(
                {"project_id": project_id},
                {"$set": {**updates, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating reference project: {e}")
            raise
    
    async def deactivate_reference_class(self, name: str) -> bool:
        """Deactivate a reference class."""
        try:
            result = await self.classes_collection.update_one(
                {"name": name},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deactivating reference class: {e}")
            raise
    
    async def deactivate_reference_project(self, project_id: str) -> bool:
        """Deactivate a reference project."""
        try:
            result = await self.projects_collection.update_one(
                {"project_id": project_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deactivating reference project: {e}")
            raise
    
    async def get_reference_statistics(self) -> Dict[str, Any]:
        """Get statistics about reference data."""
        try:
            # Count active classes and projects
            class_count = await self.classes_collection.count_documents({"is_active": True})
            project_count = await self.projects_collection.count_documents({"is_active": True})
            
            # Get projects by region
            pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$region", "count": {"$sum": 1}}}
            ]
            
            region_stats = await self.projects_collection.aggregate(pipeline).to_list(None)
            
            # Get projects by reference class
            class_pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$reference_class", "count": {"$sum": 1}}}
            ]
            
            class_stats = await self.projects_collection.aggregate(class_pipeline).to_list(None)
            
            return {
                "total_classes": class_count,
                "total_projects": project_count,
                "projects_by_region": {r["_id"]: r["count"] for r in region_stats},
                "projects_by_class": {c["_id"]: c["count"] for c in class_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting reference statistics: {e}")
            raise 