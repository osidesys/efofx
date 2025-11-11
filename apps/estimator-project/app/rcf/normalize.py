"""Attribute normalization and extraction from chat messages."""

import re
from typing import Dict, Any, Optional
from app.rcf.schemas import ProjectAttributes


class AttributeNormalizer:
    """Normalize and extract project attributes from chat messages."""
    
    def __init__(self):
        # Define patterns for common project attributes
        self.patterns = {
            "category": {
                "construction": r"\b(construction|build|install|renovation|remodel)\b",
                "technology": r"\b(software|app|website|system|platform|api)\b",
                "service": r"\b(service|consulting|support|maintenance)\b",
            },
            "subcategory": {
                "pool": r"\b(pool|swimming|aquatic)\b",
                "kitchen": r"\b(kitchen|bathroom|renovation)\b",
                "web": r"\b(web|website|frontend|backend)\b",
                "mobile": r"\b(mobile|app|ios|android)\b",
            },
            "region": {
                "socal": r"\b(socal|southern california|california|ca)\b",
                "norcal": r"\b(norcal|northern california|san francisco|sf)\b",
                "nyc": r"\b(new york|nyc|manhattan|brooklyn)\b",
                "texas": r"\b(texas|tx|houston|dallas|austin)\b",
            },
            "scope": {
                "small": r"\b(small|basic|simple|minimal)\b",
                "medium": r"\b(medium|standard|typical|normal)\b",
                "large": r"\b(large|complex|extensive|comprehensive)\b",
            },
            "complexity": {
                "low": r"\b(low|simple|basic|straightforward)\b",
                "medium": r"\b(medium|moderate|standard)\b",
                "high": r"\b(high|complex|advanced|sophisticated)\b",
            },
            "timeline": {
                "urgent": r"\b(urgent|asap|quick|fast|rush)\b",
                "normal": r"\b(normal|standard|typical)\b",
                "flexible": r"\b(flexible|no rush|whenever)\b",
            },
            "budget": {
                "low": r"\b(low|budget|affordable|cheap|economical)\b",
                "midrange": r"\b(midrange|mid-range|moderate|standard)\b",
                "high": r"\b(high|premium|luxury|top-tier)\b",
            }
        }
    
    def normalize_message(self, message: str) -> str:
        """Normalize message text for consistent processing."""
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', message.lower().strip())
        
        # Remove common filler words
        filler_words = r'\b(um|uh|like|you know|i mean)\b'
        normalized = re.sub(filler_words, '', normalized)
        
        return normalized
    
    def extract_attributes(self, message: str) -> ProjectAttributes:
        """Extract project attributes from chat message."""
        normalized_msg = self.normalize_message(message)
        
        # Extract attributes using patterns
        attrs = {}
        
        for attr_type, patterns in self.patterns.items():
            for value, pattern in patterns.items():
                if re.search(pattern, normalized_msg, re.IGNORECASE):
                    attrs[attr_type] = value
                    break
        
        # Ensure required attributes have defaults
        required_attrs = {
            "category": attrs.get("category", "construction"),
            "subcategory": attrs.get("subcategory", "general"),
            "region": attrs.get("region", "general"),
            "scope": attrs.get("scope", "medium"),
        }
        
        # Add optional attributes if found
        optional_attrs = {
            "complexity": attrs.get("complexity"),
            "timeline": attrs.get("timeline"),
            "budget": attrs.get("budget"),
        }
        
        # Combine all attributes
        all_attrs = {**required_attrs, **optional_attrs}
        
        return ProjectAttributes(**all_attrs)
    
    def get_reference_class_id(self, attrs: ProjectAttributes) -> str:
        """Generate reference class ID from normalized attributes."""
        # Format: {category}-{subcategory}-{scope}-{region}@v{distribution_version}
        # Example: pool-installation-midrange-socal@v3
        
        parts = [
            attrs.subcategory,
            attrs.category,
            attrs.scope,
            attrs.region
        ]
        
        # Clean and format parts
        clean_parts = [part.replace("-", "").lower() for part in parts if part]
        
        # Default to v1 if no distribution version specified
        distribution_version = 1
        
        return f"{'-'.join(clean_parts)}@v{distribution_version}"
    
    def apply_policy_modifiers(self, attrs: ProjectAttributes) -> Dict[str, Any]:
        """Apply policy modifiers based on attributes."""
        modifiers = []
        
        # Region-based modifiers
        if attrs.region == "socal":
            modifiers.append({
                "type": "region",
                "factor": 1.15,
                "reason": "Southern California cost premium"
            })
        elif attrs.region == "nyc":
            modifiers.append({
                "type": "region",
                "factor": 1.25,
                "reason": "New York City cost premium"
            })
        
        # Scope-based modifiers
        if attrs.scope == "large":
            modifiers.append({
                "type": "scope",
                "factor": 1.3,
                "reason": "Large scope complexity multiplier"
            })
        elif attrs.scope == "small":
            modifiers.append({
                "type": "scope",
                "factor": 0.8,
                "reason": "Small scope efficiency discount"
            })
        
        # Timeline modifiers
        if attrs.timeline == "urgent":
            modifiers.append({
                "type": "timeline",
                "factor": 1.2,
                "reason": "Urgent timeline premium"
            })
        
        return {
            "modifiers": modifiers,
            "total_factor": self._calculate_total_factor(modifiers)
        }
    
    def _calculate_total_factor(self, modifiers: list) -> float:
        """Calculate total modifier factor."""
        if not modifiers:
            return 1.0
        
        total_factor = 1.0
        for modifier in modifiers:
            total_factor *= modifier.get("factor", 1.0)
        
        return total_factor


# Global normalizer instance
attribute_normalizer = AttributeNormalizer()
