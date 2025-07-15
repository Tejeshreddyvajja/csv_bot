# from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
# import pandas as pd
# from sqlalchemy.orm import Session
# from db.database import SessionLocal
# from models.survey import SurveyFeedback
# import uuid 
# import os
# import shutil

# from langchain_core.documents import Document
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

        
# @router.post("/upload-csv/")
# async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     # ✅ Check file type
#     if not file.filename.endswith('.csv'):
#         raise HTTPException(status_code=400, detail="Invalid file format. Upload CSV only.")
    
#         # ✅ Read CSV into DataFrame
#     df = pd.read_csv(file.file)

#         # ✅ Check required columns
#     if 'respondent' not in df.columns or 'feedback' not in df.columns:
#             raise HTTPException(status_code=400, detail="CSV must have 'respondent' and 'feedback' columns.")
        
# ########################################
#     session_id = str(uuid.uuid4())

#     for _, row in df.iterrows():
#             feedback = SurveyFeedback(
#                 respondent=row['respondent'],
#                 feedback=row['feedback'],
#                 sentiment="Not Processed",
#                 upload_session_id=session_id

#             )
#             db.add(feedback)
        
#     db.commit()

#     CHROMA_PATH = "./chroma_store"
#     if os.path.exists(CHROMA_PATH):
#         shutil.rmtree(CHROMA_PATH)

#     # Convert feedback to LangChain documents
#     docs = [
#         Document(page_content=row['feedback'], metadata={"respondent": row['respondent']})
#         for _, row in df.iterrows()
#     ]

#     # Embed and persist to Chroma
#     try:
#         embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#         vectorstore = Chroma.from_documents(docs, embedding_model, persist_directory=CHROMA_PATH)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")
#     vectorstore.persist()

#     return {"message": f"Uploaded {len(df)} entries successfully.", "session_id": session_id}


from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.survey import SurveyFeedback
import uuid 
import os
import shutil
import json
import re

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from agents.sentiment_agent import run_sentiment_crew  # ✅ import crewAI function

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Upload CSV only.")
    
    df = pd.read_csv(file.file)

    if 'respondent' not in df.columns or 'feedback' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must have 'respondent' and 'feedback' columns.")
    
    session_id = str(uuid.uuid4())

    for _, row in df.iterrows():
        feedback = SurveyFeedback(
            respondent=row['respondent'],
            feedback=row['feedback'],
            sentiment="Not Processed",
            upload_session_id=session_id
        )
        db.add(feedback)
    
    db.commit()

    # Build vector DB
    CHROMA_PATH = "./chroma_store"
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    docs = [
        Document(page_content=row['feedback'], metadata={"respondent": row['respondent']})
        for _, row in df.iterrows()
    ]

    try:
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embedding_model, persist_directory=CHROMA_PATH)
        vectorstore.persist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")

    # ✅ Trigger Sentiment Analysis here
    try:
        feedbacks = db.query(SurveyFeedback)\
            .filter(SurveyFeedback.sentiment == "Not Processed")\
            .filter(SurveyFeedback.upload_session_id == session_id)\
            .all()

        feedback_payload = [{"id": f.id, "text": f.feedback} for f in feedbacks]
        result = run_sentiment_crew(feedback_payload)

        try:
            parsed = json.loads(result)
        except:
            fixed = re.search(r'\[.*\]', result, re.DOTALL)
            parsed = json.loads(fixed.group(0)) if fixed else []

        for item in parsed:
            fb = next((f for f in feedbacks if f.id == item["id"]), None)
            if fb and item["sentiment"] in ["Positive", "Negative", "Neutral"]:
                fb.sentiment = item["sentiment"]
                db.add(fb)

        db.commit()
    except Exception as e:
        return {"message": "Upload complete but sentiment analysis failed.", "error": str(e)}

    return {
        "message": f"Uploaded {len(df)} entries and ran sentiment analysis successfully.",
        "session_id": session_id
    }
