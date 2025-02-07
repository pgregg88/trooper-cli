"""Manage conversation history for the Stormtrooper AI."""

import json
import os
from pathlib import Path
from typing import Optional, Tuple


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
            return data.get('last_user_input'), data.get('last_response')
    except (json.JSONDecodeError, IOError):
        return None, None

def save_history(user_input: str, response: str) -> None:
    """Save the conversation history to disk.
    
    Args:
        user_input: The user's last message
        response: The assistant's last response
    """
    history_file = get_history_file()
    data = {
        'last_user_input': user_input,
        'last_response': response
    }
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Fail silently if we can't save history

def clear_history() -> None:
    """Clear the conversation history."""
    history_file = get_history_file()
    if history_file.exists():
        try:
            history_file.unlink()
        except IOError:
            pass  # Fail silently if we can't delete the file 