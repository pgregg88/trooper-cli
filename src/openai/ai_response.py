import os

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI client (NEW required syntax)
client = openai.OpenAI(api_key=api_key)

# Function to get a Stormtrooper response
def get_stormtrooper_response(user_input, cliff_clavin_mode=False):
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
maximum maneuverability.'

### Example Responses ###
- 'Affirmative, civilian. Orders received.'
- 'Move along. Official Imperial business.'
- 'Error: Insufficient clearance for that information.'
- 'It's a little-known fact that blaster rifles require routine calibration for optimal performance.'
    """

    # Modify user input based on Cliff Clavin Mode
    if cliff_clavin_mode:
        user_input += " (Cliff Clavin Mode is ON)"

    # Call OpenAI API (NEW syntax)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,  # Keeps responses consistent
        max_tokens=75  # Short responses for low latency
    )

    # Extract and return the response text
    response_text = response.choices[0].message.content  # ✅ Corrected for OpenAI v1.x
    return response_text.strip() if response_text else ""

# Example usage
if __name__ == "__main__":
    user_input = "Where is Darth Vader?"
    print(get_stormtrooper_response(user_input, cliff_clavin_mode=True))