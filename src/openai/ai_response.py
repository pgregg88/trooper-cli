"""OpenAI integration for Stormtrooper responses."""

import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

import openai
from openai.types.chat import ChatCompletionMessageParam

from .conversation import get_context_window

# Load environment variables
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI client (NEW required syntax)
client = openai.OpenAI(api_key=api_key)

# Function to get a Stormtrooper response
def get_stormtrooper_response(
    user_input: str, 
    cliff_clavin_mode: bool = False,
    previous_user_input: Optional[str] = None,
    previous_response: Optional[str] = None
) -> Tuple[str, str, str]:
    """Get a response from the Stormtrooper AI.
    
    Args:
        user_input: The current user's question/input
        cliff_clavin_mode: Whether to enable Cliff Clavin mode
        previous_user_input: The last user message (optional)
        previous_response: The last assistant response (optional)
        
    Returns:
        tuple: (response_text, user_input, response_text) - Current response and context for next call
    """
    # Set system prompt
    system_prompt = """You are an Imperial Stormtrooper, a loyal soldier of the Galactic Empire. 
You speak in short, military-style responses, always addressing non-Troopers as 'civilian' 
unless they are of higher rank (e.g., an officer or Sith Lord).

Stay in character at all times. You are serious, obedient, and slightly dim-witted, 
following orders without question. Avoid modern slang or humor unless it aligns with 
Imperial regulations. If asked about restricted or classified information, respond formally but do not prefix with "Error:". Instead, say: "That information is classified, civilian."

If asked about complex galactic history, answer with surface-level knowledge, avoiding 
deep philosophy unless 'Cliff Clavin Mode' is activated.

If 'Cliff Clavin Mode' is ON, occasionally inject deep trivia into your responses, but only when relevant. Example: 
'It's a little-known fact that TIE Fighter engines use twin ion propulsion systems for 
maximum maneuverability.'"""

    # Build messages array with context
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Get conversation context window
    context = get_context_window()
    
    # Add context messages
    for turn in context:
        messages.extend([
            {"role": "user", "content": turn['user_input']},
            {"role": "assistant", "content": turn['response']}
        ])
    
    # Add current user input
    current_input = user_input
    if cliff_clavin_mode:
        current_input += " (Cliff Clavin Mode is ON)"
    messages.append({"role": "user", "content": current_input})

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=75
    )

    # Extract response text
    response_text = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    
    # Return current response and context for next call
    return response_text, user_input, response_text

# Example usage
if __name__ == "__main__":
    # First message
    response1, prev_input, prev_response = get_stormtrooper_response(
        "What's your designation?", 
        cliff_clavin_mode=True
    )
    print("Response 1:", response1)
    
    # Second message with context
    response2, _, _ = get_stormtrooper_response(
        "And what's your current assignment?",
        cliff_clavin_mode=True,
        previous_user_input=prev_input,
        previous_response=prev_response
    )
    print("Response 2:", response2)