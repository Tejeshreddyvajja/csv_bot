from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.survey import SurveyFeedback
import os

# Use HuggingFace for embeddings (lazy initialization)
embedding_model = None

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        try:
            embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load HuggingFace embeddings: {e}")
            # Fallback to a simpler embedding method if needed
            raise e
    return embedding_model

# Folder to persist Chroma vector store
CHROMA_PATH = "./chroma_store"

def load_feedback_from_db(db: Session):
    feedbacks = db.query(SurveyFeedback).all()
    return [Document(page_content=f.feedback, metadata={"respondent": f.respondent}) for f in feedbacks]

def create_vector_store(documents):
    # Create or load vector store
    embedding_model = get_embedding_model()
    vectorstore = Chroma.from_documents(documents, embedding_model, persist_directory=CHROMA_PATH)
    vectorstore.persist()
    return vectorstore

def get_chatbot_chain():
    try:
        db = SessionLocal()
        documents = load_feedback_from_db(db)
        db.close()

        # Only create vector store if we have documents
        if not documents:
            raise ValueError("No feedback documents found in database")

        vectorstore = create_vector_store(documents)
        retriever = vectorstore.as_retriever()

        # LangChain QA chain using Groq/OpenAI-compatible client
        llm = ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            temperature=0
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        return qa_chain
    except Exception as e:
        print(f"Error creating chatbot chain: {e}")
        raise e
