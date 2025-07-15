from fastapi import APIRouter, Depends
from pydantic import BaseModel
from agents.chatbot_agent import get_chatbot_chain

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/chat-with-feedback/")
def chat_with_feedback(query: QueryRequest):
    chain = get_chatbot_chain()
    response = chain(query.question)
    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]]
    }