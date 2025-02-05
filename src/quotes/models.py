"""Quote models and related data structures."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class UrgencyLevel(str, Enum):
    """Urgency levels for quotes."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QuoteCategory(str, Enum):
    """Categories of quotes."""
    SPOTTED = "spotted"
    TAUNT = "taunt"
    SQUAD_COMMANDS = "squad_commands"
    CONVERSATION = "conversation"
    ANNOUNCEMENTS = "announcements"

@dataclass
class Quote:
    """A single quote with metadata."""
    
    text: str
    category: QuoteCategory
    context: str
    urgency: UrgencyLevel
    tags: List[str]
    
    def to_dict(self) -> dict:
        """Convert quote to dictionary format.
        
        Returns:
            Dictionary representation of the quote
        """
        return {
            "text": self.text,
            "category": self.category.value,
            "context": self.context,
            "urgency": self.urgency.value,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        """Create a Quote instance from a dictionary.
        
        Args:
            data: Dictionary containing quote data
            
        Returns:
            Quote instance
        """
        return cls(
            text=data["text"],
            category=QuoteCategory(data["category"]),
            context=data["context"],
            urgency=UrgencyLevel(data["urgency"]),
            tags=data["tags"]
        ) 