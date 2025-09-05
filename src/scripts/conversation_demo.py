# conversation_demo.py
"""This script demonstrates a conversation with the AI model."""
from typing import Dict, Any
import anthropic
import asyncio
import json
from conch.anthropic import AnthropicClient

def rulebook(query:str) -> str:
    """Provides the rules for the play."""
    rules = [
        "1. Be respectful and polite.",
        "2. Provide accurate information.",
        "3. If you don't know the answer, say so.",
        "4. Keep responses concise and to the point.",
        "5. Do not under any circumstances look at the queen.",
        "(Unless you are wearing sunglasses.)",
        "42. All persons more than a mile high must leave the courtroom immediately.",
        "43. No person shall be punished for merely being a person.",
    ]
    response = "Here are the rules:\n" + "\n".join(rules)
    return response

system=("You are a helpful assistant."
            "Your task is to assist the user in finding "
            "information about the characters from the play. "
            "You should provide accurate and concise answers based on the user's queries. "
            "If you don't know the answer, it's okay to say so. "
            "Always be polite and helpful.\n\n")

personae = [
    {"name": "Alice Liddell", "description": 
        "A curious and adventurous girl who loves exploring new worlds."},
    {"name": "The Queen", "description":
        "A regal figure who commands attention and respect."},
    {"name": "The Cheshire Cat", "description":
        "A grinning cat who can appear and disappear at will. Today the cat is wearing sunglasses."}
]
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

class ToolRouter:
    def route(self, tool_name: str, **kwargs) -> str:
        if tool_name == "consult_rulebook":
            return rulebook(kwargs.get("query", ""))
        else:
            return f"Tool '{tool_name}' not recognized."
        
async def main():
    client = AnthropicClient()
    client.system = system + str(personae)
    client.tools = tools
    client.tool_router = ToolRouter()

    user_input = "What color is the cat?"
    user_input = "Who may sass the queen?"
    user_input = "Are tall people allowed in the court?"
    user_message = {
        "role": "user",
        "content": user_input
    }

    conversation = [user_message]

    stop_reason, conversation = await client.tool_use_turn(conversation)
    if stop_reason == "tool_use":
        stop_reason, conversation = await client.tool_use_turn(conversation)
    for message in conversation:
        print(json.dumps(message, indent=2))
    print(f"Stop reason: {stop_reason}")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())