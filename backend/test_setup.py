"""
Quick test script to verify ARIA agent is working
Run this before starting the full server
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_keys():
    print("🔍 Checking API keys...\n")
    keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "NOTION_API_KEY": os.getenv("NOTION_API_KEY"),
        "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "MEM0_API_KEY": os.getenv("MEM0_API_KEY"),
    }
    
    all_good = True
    for key, value in keys.items():
        if value and value != "your_key_here":
            print(f"  ✅ {key}")
        else:
            print(f"  ❌ {key} — MISSING or not set!")
            all_good = False
    
    return all_good

def test_notion():
    print("\n📝 Testing Notion connection...")
    from tools.notion import create_notion_task
    result = create_notion_task("ARIA Test Task", "To Do", "test")
    print(f"  {result}")

def test_github():
    print("\n🐙 Testing GitHub connection...")
    from tools.github import get_notifications
    result = get_notifications()
    print(f"  {result[:100]}...")

def test_whatsapp():
    print("\n📱 Testing WhatsApp...")
    from tools.whatsapp import send_whatsapp_message
    result = send_whatsapp_message("🤖 ARIA Agent is online and working!")
    print(f"  {result}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ARIA Agent — System Check")
    print("=" * 50)
    
    if test_keys():
        print("\n✅ All keys present! Running connection tests...\n")
        test_notion()
        test_github()
        
        run_whatsapp = input("\n📱 Send test WhatsApp message? (y/n): ")
        if run_whatsapp.lower() == 'y':
            test_whatsapp()
        
        print("\n" + "=" * 50)
        print("✅ All systems go! Run the agent with:")
        print("   cd backend && uvicorn main:app --reload")
        print("=" * 50)
    else:
        print("\n❌ Fix missing keys in .env first!")