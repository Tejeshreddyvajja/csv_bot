# routes/crew_chat.py

from fastapi import APIRouter
from agents.crew import run_crew  # 👈 import the crew function

router = APIRouter()

@router.post("/chat-with-crew")
def chat_with_crew(question: str):
    result = run_crew(question)
    return {"answer": result}
