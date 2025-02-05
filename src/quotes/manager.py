"""Quote management and selection functionality."""

import random
from pathlib import Path
from typing import List, Optional, Dict, Set
import yaml
from loguru import logger

from .models import Quote, QuoteCategory, UrgencyLevel
from .constants import CONTEXTS, COMMON_TAGS

class QuoteManager:
    """Manager for Stormtrooper quotes."""
    
    def __init__(self, quotes_file: Optional[Path] = None):
        """Initialize the quote manager.
        
        Args:
            quotes_file: Optional path to quotes YAML file
        """
        self.quotes: List[Quote] = []
        self.recent_quotes: List[str] = []  # Track recently used quotes
        self.max_recent = 10  # Max number of quotes to track as recent
        
        if quotes_file:
            self.load_quotes(quotes_file)
    
    def load_quotes(self, file_path: Path) -> None:
        """Load quotes from a YAML file.
        
        Args:
            file_path: Path to quotes YAML file
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            for category_name, category_data in data['categories'].items():
                category = QuoteCategory(category_name)
                
                for context_name, quotes in category_data['contexts'].items():
                    for quote_data in quotes:
                        quote = Quote(
                            text=quote_data['text'],
                            category=category,
                            context=context_name,
                            urgency=UrgencyLevel(quote_data['urgency']),
                            tags=quote_data['tags']
                        )
                        self.quotes.append(quote)
            
            logger.info(f"Loaded {len(self.quotes)} quotes from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load quotes from {file_path}: {str(e)}")
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
            filtered = [q for q in filtered if q.text not in self.recent_quotes]
            
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
        self._mark_quote_used(quote)
        return quote
    
    def _mark_quote_used(self, quote: Quote) -> None:
        """Mark a quote as recently used.
        
        Args:
            quote: Quote that was used
        """
        self.recent_quotes.append(quote.text)
        if len(self.recent_quotes) > self.max_recent:
            self.recent_quotes.pop(0)  # Remove oldest quote 