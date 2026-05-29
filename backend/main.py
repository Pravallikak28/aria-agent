from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="ARIA Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    user_id: str = "pravallika"

class MessageResponse(BaseModel):
    response: str
    status: str

@app.get("/")
def root():
    return {"status": "ARIA Agent is running 🚀"}

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    try:
        response = run_agent(request.message, request.user_id)
        return MessageResponse(response=response, status="success")
    except Exception as e:
        return MessageResponse(response=f"Error: {str(e)}", status="error")

@app.get("/health")
def health():
    return {"status": "healthy", "agent": "ARIA", "version": "1.0"}