from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.survey import SurveyFeedback
from agents.sentiment_agent import run_sentiment_crew
import json
import re

router = APIRouter()  # ✅ Required!

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to get latest upload session
def get_latest_session_id(db: Session):
    result = db.query(SurveyFeedback.upload_session_id)\
               .order_by(SurveyFeedback.id.desc())\
               .first()
    return result[0] if result else None

@router.post("/analyze-sentiment-crew/")
def analyze_sentiment_crew(db: Session = Depends(get_db)):
    session_id = get_latest_session_id(db)
    if not session_id:
        return {"message": "No data to analyze."}

    feedbacks = db.query(SurveyFeedback)\
        .filter(SurveyFeedback.sentiment == "Not Processed")\
        .filter(SurveyFeedback.upload_session_id == session_id)\
        .all()

    if not feedbacks:
        return {"message": "No unprocessed feedback found."}

    feedback_payload = [{"id": f.id, "text": f.feedback} for f in feedbacks]

    try:
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
        return {"message": "✅ Sentiment analysis completed via CrewAI"}

    except Exception as e:
        return {"error": f"❌ Failed to analyze sentiment: {str(e)}"}
