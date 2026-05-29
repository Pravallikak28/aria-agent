# 🤖 ARIA — Autonomous Retrieval & Interaction Agent

> A Claude-powered autonomous agent that connects **Gmail, Google Calendar, GitHub, Notion, and WhatsApp** — executing multi-step workflows from a single natural language command.

---

## ✨ What ARIA Can Do

| Command | What happens |
|---|---|
| *"Summarize my emails and add action items to Notion"* | Reads Gmail → extracts tasks → creates Notion entries |
| *"Check GitHub and WhatsApp me any failures"* | Checks notifications → sends WhatsApp alert |
| *"What meetings do I have tomorrow? Remind me on WhatsApp"* | Reads Calendar → sends WhatsApp message |
| *"Find internship emails and create a Notion tracker"* | Searches Gmail → organizes in Notion |
| *"Check my PRs and schedule a review session tomorrow"* | Reads GitHub → creates Calendar event |

---

## 🏗️ Architecture

```
User Prompt
     ↓
FastAPI Backend
     ↓
Claude Sonnet 4 (Agentic Tool-calling Loop)
     ↓
┌─────────────────────────────────────────────┐
│  Gmail  │  Calendar  │  GitHub              │
│  Notion │  WhatsApp  │  mem0 Memory         │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Sonnet 4 (Anthropic) |
| Agent Loop | Custom multi-step tool-calling |
| Memory | mem0 persistent long-term memory |
| Backend | FastAPI + Uvicorn |
| Email | Gmail API |
| Calendar | Google Calendar API |
| Code | GitHub API |
| Tasks | Notion API |
| Messaging | Twilio WhatsApp API |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Pravallikak28/aria-agent.git
cd aria-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_key_here
GOOGLE_CLIENT_ID=your_key_here
GOOGLE_CLIENT_SECRET=your_key_here
GITHUB_TOKEN=your_key_here
NOTION_API_KEY=your_key_here
NOTION_DATABASE_ID=your_key_here
TWILIO_ACCOUNT_SID=your_key_here
TWILIO_AUTH_TOKEN=your_key_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_TO_WHATSAPP=whatsapp:+91XXXXXXXXXX
MEM0_API_KEY=your_key_here
```

### 5. Add Google credentials
- Download `credentials.json` from Google Cloud Console
- Place it in `backend/` folder

### 6. Run setup check
```bash
cd backend
python test_setup.py
```

### 7. Start the server
```bash
uvicorn main:app --reload
```

---

## 💬 Usage

### Via terminal
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check my GitHub notifications and create Notion tasks for failures"}'
```

### Via Swagger UI
Open `http://127.0.0.1:8000/docs` in your browser for an interactive interface.

---

## 📁 Project Structure

```
aria-agent/
├── backend/
│   ├── agent.py          # Claude agent core + agentic loop
│   ├── main.py           # FastAPI server
│   ├── memory.py         # Persistent memory via mem0
│   ├── test_setup.py     # Setup verification script
│   └── tools/
│       ├── gmail.py      # Gmail read/send
│       ├── calendar.py   # Google Calendar
│       ├── github.py     # GitHub notifications + PRs
│       ├── notion.py     # Notion task management
│       └── whatsapp.py   # WhatsApp via Twilio
├── requirements.txt
└── .gitignore
```

---

## 🔮 Roadmap

- [ ] React frontend dashboard
- [ ] Gmail OAuth flow in browser
- [ ] Slack integration
- [ ] Deployment on Render
- [ ] Voice command support

---

## 👩‍💻 Built By

**Pravallika Kuruva** — AI & ML Student at GPREC

- GitHub: [@Pravallikak28](https://github.com/Pravallikak28)
- LinkedIn: [Pravallika Kuruva](https://www.linkedin.com/in/pravallika-kuruva)
