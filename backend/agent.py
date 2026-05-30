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
    {"type": "function", "function": {"name": "get_unread_emails", "description": "Get unread emails from Gmail inbox. Use when user asks about emails.", "parameters": {"type": "object", "properties": {"max_results": {"type": "integer"}}, "required": []}}},
    {"type": "function", "function": {"name": "send_email", "description": "Send an email via Gmail.", "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}}},
    {"type": "function", "function": {"name": "get_github_notifications", "description": "Get GitHub notifications and activity.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "create_notion_task", "description": "Create a task in Notion.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_notion_tasks", "description": "Get tasks from Notion.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "send_whatsapp", "description": "Send a WhatsApp message.", "parameters": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}}},
    {"type": "function", "function": {"name": "get_calendar_events", "description": "Get upcoming Google Calendar events.", "parameters": {"type": "object", "properties": {"max_results": {"type": "integer"}}, "required": []}}},
    {"type": "function", "function": {"name": "create_calendar_event", "description": "Create a Google Calendar event.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}, "description": {"type": "string"}}, "required": ["title", "start_time", "end_time"]}}}
]


def process_tool_call(tool_name, tool_input):
    print(f"\n🔧 Executing: {tool_name}")
    if tool_name == "get_unread_emails":
        return get_unread_emails(tool_input.get("max_results", 5))
    elif tool_name == "send_email":
        return send_email(tool_input["to"], tool_input["subject"], tool_input["body"])
    elif tool_name == "get_github_notifications":
        return get_notifications()
    elif tool_name == "create_notion_task":
        return create_notion_task(tool_input["title"])
    elif tool_name == "get_notion_tasks":
        return get_notion_tasks()
    elif tool_name == "send_whatsapp":
        return send_whatsapp_message(tool_input["message"])
    elif tool_name == "get_calendar_events":
        return get_events(tool_input.get("max_results", 5))
    elif tool_name == "create_calendar_event":
        return create_event(
            tool_input["title"],
            tool_input["start_time"],
            tool_input["end_time"],
            tool_input.get("description", "")
        )
    return f"Unknown tool: {tool_name}"


def run_agent(user_message: str, user_id: str = "pravallika"):
    print(f"\n{'='*50}\n👤 User: {user_message}\n{'='*50}")

    memory_context = get_memory(user_id)

    system_prompt = f"""You are ARIA (Autonomous Retrieval & Interaction Agent), a powerful AI assistant.
You have access to: Gmail, GitHub, Notion, WhatsApp, and Google Calendar.

When given a task:
1. Break it into steps
2. Use the right tools in sequence
3. Summarize clearly what you did at the end

User memory context:
{memory_context}

Always be proactive — if you find action items in emails, offer to add them to Notion.
If there are GitHub failures, offer to notify via WhatsApp."""

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

        if finish_reason == "stop" or not msg.tool_calls:
            final_response = msg.content or "Task completed!"
            save_memory(user_id, user_message, final_response)
            print(f"\n✅ ARIA: {final_response}")
            return final_response

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