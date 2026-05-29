import os
from groq import Groq
from dotenv import load_dotenv
import json
 
load_dotenv(override=True)
 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 
from tools.gmail import get_unread_emails, send_email
from tools.calendar import get_events, create_event
from tools.github import get_notifications, get_pull_requests
from tools.notion import create_notion_task, get_notion_tasks
from tools.whatsapp import send_whatsapp_message
from memory import get_memory, save_memory
 
tools = [
    {"type": "function", "function": {"name": "get_github_notifications", "description": "Get GitHub notifications", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "create_notion_task", "description": "Create a Notion task", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "Task title"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_notion_tasks", "description": "Get all Notion tasks", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "send_whatsapp", "description": "Send a WhatsApp message to the user", "parameters": {"type": "object", "properties": {"message": {"type": "string", "description": "The message text to send"}}, "required": ["message"]}}}
]
 
 
def process_tool_call(tool_name, tool_input):
    print(f"\n🔧 Executing: {tool_name}")
    if tool_name == "get_unread_emails":
        return get_unread_emails(tool_input.get("max_results", 5))
    elif tool_name == "send_email":
        return send_email(tool_input["to"], tool_input["subject"], tool_input["body"])
    elif tool_name == "get_calendar_events":
        return get_events(tool_input.get("max_results", 5))
    elif tool_name == "create_calendar_event":
        return create_event(tool_input["title"], tool_input["start_time"], tool_input["end_time"], tool_input.get("description", ""))
    elif tool_name == "get_github_notifications":
        return get_notifications()
    elif tool_name == "create_notion_task":
        return create_notion_task(tool_input["title"], tool_input.get("status", "Not started"), tool_input.get("tags", ""))
    elif tool_name == "get_notion_tasks":
        return get_notion_tasks()
    elif tool_name == "send_whatsapp":
        return send_whatsapp_message(tool_input["message"])
    return f"Unknown tool: {tool_name}"
 
 
def run_agent(user_message: str, user_id: str = "pravallika"):
    print(f"\n{'='*50}\n👤 User: {user_message}\n{'='*50}")
 
    memory_context = get_memory(user_id)
 
    system_prompt = f"""You are ARIA (Autonomous Retrieval & Interaction Agent), a powerful AI assistant.
You can access Gmail, Google Calendar, GitHub, Notion, and WhatsApp.
Break tasks into steps, use tools in sequence, summarize what you did clearly at the end.
User memory context: {memory_context}"""
 
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
 
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
 
        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
 
        print(f"\n🤖 ARIA thinking... (finish_reason: {finish_reason})")
 
        # If done
        if finish_reason == "stop" or not msg.tool_calls:
            final_response = msg.content or "Task completed!"
            save_memory(user_id, user_message, final_response)
            print(f"\n✅ ARIA: {final_response}")
            return final_response
 
        # Process tool calls
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in msg.tool_calls
            ]
        })
 
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            tool_input = json.loads(tc.function.arguments)
            result = process_tool_call(tool_name, tool_input)
            print(f"   ✓ {tool_name} done")
 
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })