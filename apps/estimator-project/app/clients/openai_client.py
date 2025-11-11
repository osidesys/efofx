"""OpenAI client for LLM completions."""

import time
from typing import Dict, Any, Optional
import openai
import structlog
from app.core.config import settings
from app.observability.metrics import llm_metrics

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """OpenAI client for LLM completions."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.timeout = settings.llm_timeout
    
    async def generate_estimate(self, prompt: str) -> Dict[str, Any]:
        """Generate estimate using OpenAI LLM."""
        start_time = time.time()
        
        try:
            logger.info(
                "Generating estimate with OpenAI",
                model=self.model,
                prompt_length=len(prompt)
            )
            
            # Create completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert estimator. Generate accurate, professional estimates based on the provided facts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent output
                max_tokens=2000,
                response_format={"type": "json_object"},  # Ensure JSON output
                timeout=self.timeout
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Parse JSON response
            import json
            try:
                parsed_response = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(
                    "Failed to parse OpenAI response as JSON",
                    content=content,
                    error=str(e)
                )
                raise ValueError(f"Invalid JSON response from OpenAI: {e}")
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            llm_metrics.record_llm_call_success(
                model=self.model,
                latency_ms=latency_ms,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            logger.info(
                "Successfully generated estimate with OpenAI",
                model=self.model,
                latency_ms=latency_ms,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return parsed_response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            llm_metrics.record_llm_call_failure(
                model=self.model,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to generate estimate with OpenAI",
                model=self.model,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
    
    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a concise summary of content."""
        start_time = time.time()
        
        try:
            prompt = f"""
Summarize the following content in {max_length} characters or less:

{content}

Summary:
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional summarizer. Create concise, accurate summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=100,
                timeout=self.timeout
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            llm_metrics.record_llm_call_success(
                model=self.model,
                latency_ms=latency_ms,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return summary
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            llm_metrics.record_llm_call_failure(
                model=self.model,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to generate summary with OpenAI",
                model=self.model,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
    
    async def validate_estimate(self, estimate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and potentially fix estimate data using LLM."""
        start_time = time.time()
        
        try:
            prompt = f"""
Validate and fix the following estimate data. Ensure it follows the correct schema:

{estimate_data}

If there are any issues, fix them and return the corrected data. If the data is valid, return it unchanged.

Return only valid JSON in the expected format.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data validation expert. Fix any issues in the provided data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            import json
            try:
                validated_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(
                    "Failed to parse validation response as JSON",
                    content=content,
                    error=str(e)
                )
                raise ValueError(f"Invalid JSON response from validation: {e}")
            
            # Record success metrics
            latency_ms = int((time.time() - start_time) * 1000)
            llm_metrics.record_llm_call_success(
                model=self.model,
                latency_ms=latency_ms,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return validated_data
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Record failure metrics
            llm_metrics.record_llm_call_failure(
                model=self.model,
                error_type=type(e).__name__,
                latency_ms=latency_ms
            )
            
            logger.error(
                "Failed to validate estimate with OpenAI",
                model=self.model,
                error=str(e),
                latency_ms=latency_ms,
                exc_info=True
            )
            raise
