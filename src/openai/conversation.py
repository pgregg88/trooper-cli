"""Manage conversation history for the Stormtrooper AI."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Maximum number of turns to keep in history
MAX_HISTORY_TURNS = 3

def get_history_file() -> Path:
    """Get the path to the history file."""
    # Use XDG_DATA_HOME or fallback to ~/.local/share
    data_home = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    app_dir = Path(data_home) / 'trooper-cli'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / 'conversation_history.json'

def load_history() -> Tuple[Optional[str], Optional[str]]:
    """Load the last conversation from disk.
    
    Returns:
        Tuple of (last_user_input, last_response) or (None, None) if no history
    """
    history_file = get_history_file()
    if not history_file.exists():
        return None, None
        
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            history = data.get('history', [])
            if not history:
                return None, None
            # Return the most recent turn
            return history[-1].get('user_input'), history[-1].get('response')
    except (json.JSONDecodeError, IOError):
        return None, None

def get_context_window() -> List[Dict[str, str]]:
    """Get the conversation context window.
    
    Returns:
        List of conversation turns, each containing user_input and response
    """
    history_file = get_history_file()
    if not history_file.exists():
        return []
        
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            history = data.get('history', [])
            # Return up to MAX_HISTORY_TURNS most recent turns
            return history[-MAX_HISTORY_TURNS:]
    except (json.JSONDecodeError, IOError):
        return []

def save_history(user_input: str, response: str) -> None:
    """Save the conversation history to disk.
    
    Args:
        user_input: The user's last message
        response: The assistant's last response
    """
    history_file = get_history_file()
    
    # Load existing history
    try:
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history = data.get('history', [])
        else:
            history = []
            
        # Add new turn
        history.append({
            'user_input': user_input,
            'response': response
        })
        
        # Keep only the most recent turns
        history = history[-MAX_HISTORY_TURNS:]
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({'history': history}, f, indent=2)
    except (json.JSONDecodeError, IOError):
        pass  # Fail silently if we can't save history

def clear_history() -> None:
    """Clear the conversation history."""
    history_file = get_history_file()
    if history_file.exists():
        try:
            history_file.unlink()
        except IOError:
            pass  # Fail silently if we can't delete the file 