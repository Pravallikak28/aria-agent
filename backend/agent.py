import os
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

from tools.gmail import get_unread_emails, send_email
from tools.calendar import get_events, create_event
from tools.github import get_notifications, get_pull_requests
from tools.notion import create_notion_task, get_notion_tasks
from tools.whatsapp import send_whatsapp_message
from memory import get_memory, save_memory

tools = [
    {"name": "get_unread_emails", "description": "Get unread emails from Gmail", "input_schema": {"type": "object", "properties": {"max_results": {"type": "integer"}}, "required": []}},
    {"name": "send_email", "description": "Send an email", "input_schema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
    {"name": "get_calendar_events", "description": "Get upcoming calendar events", "input_schema": {"type": "object", "properties": {"max_results": {"type": "integer"}}, "required": []}},
    {"name": "create_calendar_event", "description": "Create a calendar event", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}, "description": {"type": "string"}}, "required": ["title", "start_time", "end_time"]}},
    {"name": "get_github_notifications", "description": "Get GitHub notifications", "input_schema": {"type": "object", "properties": {}, "required": []}},
    {"name": "create_notion_task", "description": "Create a Notion task", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "status": {"type": "string"}, "tags": {"type": "string"}}, "required": ["title"]}},
    {"name": "get_notion_tasks", "description": "Get Notion tasks", "input_schema": {"type": "object", "properties": {}, "required": []}},
    {"name": "send_whatsapp", "description": "Send a WhatsApp message", "input_schema": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}}
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
Break tasks into steps, use tools in sequence, summarize what you did.
User memory: {memory_context}"""

    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        print(f"\n🤖 ARIA thinking... (stop_reason: {response.stop_reason})")

        if response.stop_reason == "end_turn":
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response = block.text
            save_memory(user_id, user_message, final_response)
            print(f"\n✅ ARIA: {final_response}")
            return final_response

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(result)})
                    print(f"   ✓ {block.name} done")
            messages.append({"role": "user", "content": tool_results})