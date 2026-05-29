import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv(override=True)

def get_notion_client():
    return Client(auth=os.getenv("NOTION_API_KEY"))

def create_notion_task(title: str, status: str = "Not started", tags: str = "") -> str:
    try:
        notion = get_notion_client()
        database_id = os.getenv("NOTION_DATABASE_ID")
        properties = {
            "Name": {
                "title": [{"text": {"content": title}}]
            }
        }
        notion.pages.create(parent={"database_id": database_id}, properties=properties)
        return f"Task created in Notion: '{title}'"
    except Exception as e:
        return f"Notion create error: {str(e)}"

def get_notion_tasks() -> str:
    try:
        notion = get_notion_client()
        database_id = os.getenv("NOTION_DATABASE_ID")
        results = notion.databases.query(database_id=database_id, page_size=10)
        pages = results.get("results", [])
        if not pages:
            return "No tasks found in Notion."
        tasks = []
        for page in pages:
            props = page["properties"]
            title_prop = props.get("Name", {}).get("title", [])
            title = title_prop[0]["text"]["content"] if title_prop else "Untitled"
            tasks.append(f"?? {title}")
        return "\n".join(tasks)
    except Exception as e:
        return f"Notion fetch error: {str(e)}"
