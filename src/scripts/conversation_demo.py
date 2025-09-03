# conversation_demo.py
"""This script demonstrates a conversation with the AI model."""
from typing import Dict, Any
import anthropic
import json

def fake_chat_with_ai(messages: Dict[str, Any]):
    # Simulate a conversation with the AI model
    messages.append(
        {"role": "assistant", "content": "This is a simulated response from the AI."}
    )
    return messages

def rulebook(query:str):
    """Provides the rules for the play."""
    rules = [
        "1. Be respectful and polite.",
        "2. Provide accurate information.",
        "3. If you don't know the answer, say so.",
        "4. Keep responses concise and to the point.",
        "5. Do not under any circumstances look at the queen."
    ]
    response = "Here are the rules:\n" + "\n".join(rules)
    return response

def actual_claude(messages: Dict[str, Any]):
    """This is experimental code. Does not provide retries."""
    client = anthropic.Anthropic()
    system=("You are a helpful assistant."
                "Your task is to assist the user in finding information about the characters from the play."
                "You should provide accurate and concise answers based on the user's queries."
                "If you don't know the answer, it's okay to say so."
                "Always be polite and helpful.\n\n")
    tools = [
        {
            "name": "consult_rulebook",
            "description": "Look up rules for the play.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }
    ]
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            system=system+json.dumps(personae),
            tools=tools,
            messages=messages
        )
        return response.model_dump()
    except Exception as e:
        return [{"error": str(e)}]

personae = [
    {"name": "Alice Liddell", "description": "A curious and adventurous girl who loves exploring new worlds."},
    {"name": "The Queen", "description": "A regal figure who commands attention and respect."},
    {"name": "The Cheshire Cat", "description": "A grinning cat who can appear and disappear at will."}
]
if __name__ == "__main__":
    user_input = "Who may look at the queen?"
    user_message = {
        "role": "user",
        "content": user_input
    }

    response = actual_claude([user_message])
    print(json.dumps(response, indent=2))