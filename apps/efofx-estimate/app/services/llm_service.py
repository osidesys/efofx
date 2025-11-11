"""
LLM service for efOfX Estimation Service.

This module provides integration with OpenAI and other LLM providers
for natural language processing and estimation generation.
"""

import logging
from typing import Optional, Dict, Any
import openai
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM integration and text generation."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    async def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate response using OpenAI API."""
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def classify_project(self, description: str, region: str, reference_classes: list) -> str:
        """Classify project into reference class using LLM."""
        try:
            prompt = f"""
            Analyze the following project description and classify it into the most appropriate reference class.
            
            Project Description: {description}
            Region: {region}
            
            Available Reference Classes: {reference_classes}
            
            Please provide only the reference class name as your response.
            """
            
            system_message = """
            You are an expert construction estimator. Your task is to classify construction projects 
            into appropriate reference classes based on project descriptions and regional context.
            Respond with only the reference class name, nothing else.
            """
            
            response = await self.generate_response(prompt, system_message)
            return response.strip().lower()
            
        except Exception as e:
            logger.error(f"Error classifying project: {e}")
            return "general"
    
    async def generate_estimation(
        self, 
        description: str, 
        region: str, 
        reference_class: str, 
        reference_projects: list
    ) -> Dict[str, Any]:
        """Generate estimation using LLM and reference data."""
        try:
            prompt = f"""
            Based on the following project details and reference data, generate a comprehensive estimate.
            
            Project Details:
            - Description: {description}
            - Region: {region}
            - Reference Class: {reference_class}
            
            Reference Projects: {reference_projects[:5]}
            
            Please provide a structured estimate with:
            1. Total estimated cost
            2. Estimated timeline (weeks)
            3. Recommended team size
            4. Cost breakdown by category (materials, labor, equipment, permits, design, contingency, profit_margin)
            5. Confidence score (0-1)
            6. Key assumptions
            7. Identified risks
            """
            
            system_message = """
            You are an expert construction estimator using Reference Class Forecasting (RCF).
            Analyze the project description and reference data to provide accurate estimates.
            Consider regional factors, project complexity, and historical data patterns.
            """
            
            response = await self.generate_response(prompt, system_message)
            
            # Parse the response into structured data
            # This is a simplified parser - in production, you'd use more sophisticated parsing
            return self._parse_estimation_response(response)
            
        except Exception as e:
            logger.error(f"Error generating estimation: {e}")
            return self._create_default_estimation()
    
    def _parse_estimation_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured estimation data."""
        # This is a simplified parser - in production, you'd use more sophisticated parsing
        # or structured output from the LLM
        
        # For now, return a default structure
        return {
            "total_cost": 50000.0,
            "timeline_weeks": 8,
            "team_size": 4,
            "cost_breakdown": {
                "materials": 20000.0,
                "labor": 12500.0,
                "equipment": 4000.0,
                "permits": 1500.0,
                "design": 2500.0,
                "contingency": 4000.0,
                "profit_margin": 5500.0
            },
            "confidence_score": 0.8,
            "assumptions": ["Standard project scope", "No major site preparation required"],
            "risks": ["Weather delays", "Material cost fluctuations"],
            "reference_projects_used": []
        }
    
    def _create_default_estimation(self) -> Dict[str, Any]:
        """Create default estimation when LLM processing fails."""
        return {
            "total_cost": 50000.0,
            "timeline_weeks": 8,
            "team_size": 4,
            "cost_breakdown": {
                "materials": 20000.0,
                "labor": 12500.0,
                "equipment": 4000.0,
                "permits": 1500.0,
                "design": 2500.0,
                "contingency": 4000.0,
                "profit_margin": 5500.0
            },
            "confidence_score": 0.5,
            "assumptions": ["Default estimation due to processing error"],
            "risks": ["Estimation accuracy may be lower than usual"],
            "reference_projects_used": []
        } 