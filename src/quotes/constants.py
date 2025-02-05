"""Constants for quote management."""

from typing import Dict, List

# Quote contexts by category
CONTEXTS: Dict[str, List[str]] = {
    "spotted": ["combat", "patrol"],
    "taunt": ["arrest", "combat", "pursuit"],
    "squad_commands": ["combat", "formation", "tactical"],
    "conversation": ["casual", "inspection", "warning"],
    "announcements": ["alert", "update"]
}

# Common tags for quotes
COMMON_TAGS = [
    "combat",
    "alert",
    "jedi",
    "patrol",
    "command",
    "tactical",
    "pursuit",
    "official",
    "casual",
    "warning"
]

# Audio effect parameters by urgency
URGENCY_EFFECTS = {
    "low": {
        "static_duration_min": 0.05,
        "static_duration_max": 0.1,
        "static_volume": 0.08,
        "static_variation": 0.3,
        "click_volume": 0.12,
        "click_variation": 0.2
    },
    "medium": {
        "static_duration_min": 0.03,
        "static_duration_max": 0.07,
        "static_volume": 0.1,
        "static_variation": 0.4,
        "click_volume": 0.15,
        "click_variation": 0.3
    },
    "high": {
        "static_duration_min": 0.02,
        "static_duration_max": 0.05,
        "static_volume": 0.12,
        "static_variation": 0.5,
        "click_volume": 0.18,
        "click_variation": 0.4
    }
} 