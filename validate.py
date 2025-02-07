#!/usr/bin/env python3
"""Validate quotes YAML file structure and content."""

import sys
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


def validate_quote(quote: Dict[str, Any], category: str, context: str) -> bool:
    """Validate a single quote entry."""
    required_fields = ["text", "urgency", "tags"]
    for field in required_fields:
        if field not in quote:
            print(f"Error: Missing required field '{field}' in {category}/{context}")
            return False
            
    # Validate urgency
    if quote["urgency"] not in ["low", "medium", "high", "normal"]:
        print(f"Error: Invalid urgency '{quote['urgency']}' in {category}/{context}")
        return False
        
    # Validate tags
    if not isinstance(quote["tags"], list):
        print(f"Error: Tags must be a list in {category}/{context}")
        return False
        
    # Validate optional sequence fields if present
    if "audio_file" in quote and not isinstance(quote["audio_file"], str):
        print(f"Error: audio_file must be a string in {category}/{context}")
        return False
        
    if "can_follow" in quote and not isinstance(quote["can_follow"], list):
        print(f"Error: can_follow must be a list in {category}/{context}")
        return False
        
    if "min_pause" in quote and not isinstance(quote["min_pause"], (int, float)):
        print(f"Error: min_pause must be a number in {category}/{context}")
        return False
        
    if "max_pause" in quote and not isinstance(quote["max_pause"], (int, float)):
        print(f"Error: max_pause must be a number in {category}/{context}")
        return False
        
    return True

def validate_context(context_data: List[Dict[str, Any]], category: str, context: str) -> bool:
    """Validate a context section."""
    if not isinstance(context_data, list):
        print(f"Error: Context {category}/{context} must contain a list of quotes")
        return False
        
    return all(validate_quote(quote, category, context) for quote in context_data)

def validate_category(category_data: Dict[str, Any], category: str) -> bool:
    """Validate a category section."""
    if "description" not in category_data:
        print(f"Error: Missing description in category {category}")
        return False
        
    if "contexts" not in category_data:
        print(f"Error: Missing contexts in category {category}")
        return False
        
    contexts = category_data["contexts"]
    if not isinstance(contexts, dict):
        print(f"Error: Contexts in category {category} must be a dictionary")
        return False
        
    return all(
        validate_context(context_data, category, context)
        for context, context_data in contexts.items()
    )

def main() -> int:
    """Validate the quotes YAML file."""
    try:
        quotes_file = Path("config/quotes.yaml")
        if not quotes_file.exists():
            print(f"Error: {quotes_file} not found")
            return 1
            
        with open(quotes_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        if "categories" not in data:
            print("Error: Missing top-level 'categories' key")
            return 1
            
        categories = data["categories"]
        if not isinstance(categories, dict):
            print("Error: Categories must be a dictionary")
            return 1
            
        if all(validate_category(cat_data, category) 
              for category, cat_data in categories.items()):
            print("YAML is valid!")
            return 0
        return 1
        
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
