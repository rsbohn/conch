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
        "5. Do not under any circumstances look at the queen.",
        "(Unless you are wearing sunglasses.)"
    ]
    response = "Here are the rules:\n" + "\n".join(rules)
    return response

def actual_claude(messages: Dict[str, Any]):
    """This is experimental code. Does not provide retries."""
    client = anthropic.Anthropic()
    system=("You are a helpful assistant."
                "Your task is to assist the user in finding "
                "information about the characters from the play. "
                "You should provide accurate and concise answers based on the user's queries. "
                "If you don't know the answer, it's okay to say so. "
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
    
def _tool(item: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = item["name"]
    if tool_name == "consult_rulebook":
        query = item["input"].get("query", "")
        tool_result = rulebook(query)
    else:
        tool_result = f"<unknown tool: {tool_name}>"
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": item["id"],
                "content": tool_result
            }
        ]
    }

personae = [
    {"name": "Alice Liddell", "description": 
        "A curious and adventurous girl who loves exploring new worlds."},
    {"name": "The Queen", "description":
        "A regal figure who commands attention and respect."},
    {"name": "The Cheshire Cat", "description":
        "A grinning cat who can appear and disappear at will. Today the cat is wearing sunglasses."}
]
if __name__ == "__main__":
    user_input = "Who may look at the queen?"
    user_message = {
        "role": "user",
        "content": user_input
    }

    conversation = [user_message]
    response = actual_claude(conversation)
    print(response["stop_reason"])
    print(json.dumps(response["content"], indent=2))
    conversation.append({"role": "assistant", "content": response["content"]})

    if response["stop_reason"] == "tool_use":
        print("*** Tool use detected.")
        for item in response["content"]:
            if item["type"] == "tool_use":
                tool_message = _tool(item)
                conversation.append(tool_message)
        response = actual_claude(conversation)
        if "error" in response:
            print("Error during Claude interaction:", response["error"])
        else:
            print(response["stop_reason"])
            print(json.dumps(response["content"], indent=2))
    
    print("Done.")