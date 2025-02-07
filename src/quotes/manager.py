"""Quote management and selection functionality."""

import random
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Optional, Set

import yaml
from loguru import logger

from .constants import COMMON_TAGS, CONTEXTS
from .models import Quote, QuoteCategory, SequenceRules, UrgencyLevel


class QuoteManager:
    """Manager for Stormtrooper quotes."""
    
    def __init__(self, quotes_file: Path):
        """Initialize the quote manager.
        
        Args:
            quotes_file: Path to quotes YAML file
        """
        self.quotes_file = quotes_file
        self.quotes: List[Quote] = []
        self._quote_history: Deque[Quote] = deque(maxlen=10)  # Track recent quotes
        self._sequence_rules = SequenceRules()  # Default rules
        self._load_quotes()
    
    def _load_quotes(self) -> None:
        """Load quotes from YAML file."""
        try:
            with open(self.quotes_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "categories" not in data:
                raise ValueError("Invalid quotes file format")
                
            self.quotes = []
            for category, cat_data in data["categories"].items():
                if "contexts" not in cat_data:
                    continue
                    
                for context, quotes in cat_data["contexts"].items():
                    for quote_data in quotes:
                        quote_data["category"] = category
                        quote_data["context"] = context
                        self.quotes.append(Quote.from_dict(quote_data))
                        
        except Exception as e:
            logger.error(f"Failed to load quotes: {e}")
            raise
    
    def get_quotes(
        self,
        category: Optional[str] = None,
        context: Optional[str] = None,
        urgency: Optional[str] = None,
        tags: Optional[List[str]] = None,
        exclude_recent: bool = True,
        min_matching_tags: int = 1
    ) -> List[Quote]:
        """Get quotes matching the specified criteria.
        
        Args:
            category: Optional category to filter by
            context: Optional context to filter by
            urgency: Optional urgency level to filter by
            tags: Optional list of tags to filter by
            exclude_recent: Whether to exclude recently used quotes
            min_matching_tags: Minimum number of tags that must match (default: 1)
            
        Returns:
            List of matching quotes
        """
        filtered = self.quotes.copy()
        
        # Apply filters
        if category:
            filtered = [q for q in filtered if q.category == QuoteCategory(category)]
            
        if context:
            filtered = [q for q in filtered if q.context == context]
            
        if urgency:
            filtered = [q for q in filtered if q.urgency == UrgencyLevel(urgency)]
            
        if tags:
            # Count matching tags for each quote
            filtered = [
                q for q in filtered 
                if sum(1 for tag in tags if tag in q.tags) >= min_matching_tags
            ]
            
        if exclude_recent:
            recent_texts = {q.text for q in self._quote_history}
            filtered = [q for q in filtered if q.text not in recent_texts]
            
        return filtered
    
    def get_random_quote(
        self,
        category: Optional[str] = None,
        context: Optional[str] = None,
        urgency: Optional[str] = None,
        tags: Optional[List[str]] = None,
        exclude_recent: bool = True,
        min_matching_tags: int = 1
    ) -> Optional[Quote]:
        """Get a random quote matching the specified criteria.
        
        Args:
            category: Optional category to filter by
            context: Optional context to filter by
            urgency: Optional urgency level to filter by
            tags: Optional list of tags to filter by
            exclude_recent: Whether to exclude recently used quotes
            min_matching_tags: Minimum number of tags that must match (default: 1)
            
        Returns:
            A random matching quote, or None if no matches found
        """
        matching_quotes = self.get_quotes(
            category=category,
            context=context,
            urgency=urgency,
            tags=tags,
            exclude_recent=exclude_recent,
            min_matching_tags=min_matching_tags
        )
        
        if not matching_quotes:
            if exclude_recent:
                # Try again including recent quotes
                return self.get_random_quote(
                    category=category,
                    context=context,
                    urgency=urgency,
                    tags=tags,
                    exclude_recent=False,
                    min_matching_tags=min_matching_tags
                )
            # If still no matches, try with fewer required matching tags
            elif tags and min_matching_tags > 1:
                return self.get_random_quote(
                    category=category,
                    context=context,
                    urgency=urgency,
                    tags=tags,
                    exclude_recent=exclude_recent,
                    min_matching_tags=min_matching_tags - 1
                )
            return None
            
        quote = random.choice(matching_quotes)
        self._quote_history.append(quote)
        return quote
    
    def select_quote(
        self,
        category: Optional[QuoteCategory] = None,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None,
        avoid_recent: bool = True
    ) -> Optional[Quote]:
        """Select a quote matching the given criteria.
        
        Args:
            category: Optional category to filter by
            context: Optional context to filter by
            tags: Optional list of tags to filter by
            avoid_recent: Whether to avoid recently used quotes
            
        Returns:
            Selected quote or None if no matching quotes found
        """
        # Filter quotes
        candidates = self.quotes
        
        if category:
            candidates = [q for q in candidates if q.category == category]
            
        if context:
            candidates = [q for q in candidates if q.context == context]
            
        if tags:
            candidates = [q for q in candidates if any(tag in q.tags for tag in tags)]
            
        if avoid_recent:
            recent_texts = {q.text for q in self._quote_history}
            candidates = [q for q in candidates if q.text not in recent_texts]
            
        if not candidates:
            return None
            
        # Select quote
        quote = random.choice(candidates)
        self._quote_history.append(quote)
        return quote
        
    def select_sequence(
        self,
        category: Optional[QuoteCategory] = None,
        context: Optional[str] = None,
        count: int = 3,
        tags: Optional[List[str]] = None
    ) -> List[Quote]:
        """Select a sequence of quotes matching the criteria.
        
        Args:
            category: Optional category to filter by
            context: Optional context to filter by
            count: Number of quotes to select
            tags: Optional list of tags to filter by
            
        Returns:
            List of selected quotes
        """
        sequence: List[Quote] = []
        used_texts: Set[str] = set()
        
        for _ in range(count):
            # Get candidates that can follow the last quote
            candidates = self.quotes
            
            if category:
                candidates = [q for q in candidates if q.category == category]
                
            if context:
                candidates = [q for q in candidates if q.context == context]
                
            if tags:
                candidates = [q for q in candidates if any(tag in q.tags for tag in tags)]
                
            # Filter by sequence rules
            if sequence:
                last_quote = sequence[-1]
                if last_quote.can_follow:
                    candidates = [q for q in candidates if q.category.value in last_quote.can_follow]
                    
            # Remove already used quotes
            candidates = [q for q in candidates if q.text not in used_texts]
            
            if not candidates:
                break
                
            # Select quote
            quote = random.choice(candidates)
            sequence.append(quote)
            used_texts.add(quote.text)
            self._quote_history.append(quote)
            
        return sequence
        
    def get_pause_duration(self, quote: Quote) -> float:
        """Get the pause duration after a quote.
        
        Args:
            quote: Quote to get pause duration for
            
        Returns:
            Pause duration in seconds
        """
        if quote.min_pause == quote.max_pause:
            return quote.min_pause
            
        return random.uniform(quote.min_pause, quote.max_pause)
        
    @property
    def sequence_rules(self) -> SequenceRules:
        """Get the current sequence rules."""
        return self._sequence_rules
        
    @sequence_rules.setter
    def sequence_rules(self, rules: SequenceRules) -> None:
        """Set new sequence rules."""
        self._sequence_rules = rules 