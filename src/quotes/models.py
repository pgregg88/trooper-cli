"""Quote models and related data structures."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UrgencyLevel(str, Enum):
    """Urgency levels for quotes."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def _missing_(cls, value: str) -> Optional["UrgencyLevel"]:
        """Handle string value lookup, supporting both 'normal' and 'medium'."""
        try:
            if value == "normal":
                return cls.MEDIUM
            return cls(value)
        except ValueError:
            return None

class QuoteCategory(str, Enum):
    """Categories of quotes."""
    SPOTTED = "spotted"
    TAUNT = "taunt"
    SQUAD_COMMANDS = "squad_commands"
    CONVERSATION = "conversation"
    ANNOUNCEMENTS = "announcements"
    STALL = "stall"
    HUMOR = "humor"
    MONOLOGUES = "monologues"

@dataclass
class SequenceRules:
    """Rules for quote sequences within a context."""
    min_delay: float = 0.0
    max_delay: float = 1.0
    avoid_repeat_count: int = 5

@dataclass
class Quote:
    """A single quote with metadata."""
    
    text: str
    category: QuoteCategory
    context: str
    urgency: UrgencyLevel
    tags: List[str]
    # Optional fields for audio and sequence control
    audio_file: Optional[str] = None
    can_follow: List[str] = field(default_factory=list)  # Categories that can follow this quote
    min_pause: float = 0.0  # Minimum pause after this quote
    max_pause: float = 1.0  # Maximum pause after this quote
    
    def to_dict(self) -> dict:
        """Convert quote to dictionary format.
        
        Returns:
            Dictionary representation of the quote
        """
        data = {
            "text": self.text,
            "category": self.category.value,
            "context": self.context,
            "urgency": self.urgency.value,
            "tags": self.tags
        }
        
        # Add optional fields if they have non-default values
        if self.audio_file:
            data["audio_file"] = self.audio_file
        if self.can_follow:
            data["can_follow"] = self.can_follow
        if self.min_pause != 0.0:
            data["min_pause"] = self.min_pause
        if self.max_pause != 1.0:
            data["max_pause"] = self.max_pause
            
        return data
    
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
            tags=data["tags"],
            audio_file=data.get("audio_file"),
            can_follow=data.get("can_follow", []),
            min_pause=data.get("min_pause", 0.0),
            max_pause=data.get("max_pause", 1.0)
        ) 