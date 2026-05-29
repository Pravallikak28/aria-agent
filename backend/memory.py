import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

def save_memory(user_id: str, user_message: str, agent_response: str):
    """Save conversation to long-term memory"""
    try:
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": agent_response}
        ]
        client.add(messages, user_id=user_id)
        print(f"💾 Memory saved for {user_id}")
    except Exception as e:
        print(f"Memory save error: {e}")

def get_memory(user_id: str) -> str:
    """Retrieve relevant memories for user"""
    try:
        memories = client.get_all(user_id=user_id)
        if not memories:
            return "No previous context found."
        
        memory_text = "\n".join([f"- {m['memory']}" for m in memories[:10]])
        return memory_text
    except Exception as e:
        print(f"Memory fetch error: {e}")
        return "No previous context found."