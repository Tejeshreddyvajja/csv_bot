from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.survey import SurveyFeedback
import os
from dotenv import load_dotenv
import openai

load_dotenv()

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

###############################################################        
def get_latest_session_id(db: Session):
    result = db.query(SurveyFeedback.upload_session_id)\
               .order_by(SurveyFeedback.id.desc())\
               .first()
    return result[0] if result else None

################################################################
@router.post("/analyze-sentiment/")
def analyze_sentiment(db: Session = Depends(get_db)):
    client = openai.OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    session_id = get_latest_session_id(db)
    if not session_id:
        return {"message": "No data to analyze."}

    feedbacks = db.query(SurveyFeedback)\
                  .filter(SurveyFeedback.sentiment == "Not Processed")\
                  .filter(SurveyFeedback.upload_session_id == session_id)\
                  .all()

    if not feedbacks:
        return {"message": "No unprocessed feedback found."}
    
    # [rest of your logic remains unchanged...]



    for item in feedbacks:
        prompt = f"""
Classify the sentiment of the following feedback into Positive, Negative, or Neutral.

Feedback: "{item.feedback}"

Just output one word: Positive, Negative, or Neutral.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            sentiment = response.choices[0].message.content.strip()

            print(f"Processing ID {item.id}: {item.feedback}")
            print(f"Predicted sentiment: {sentiment}")

            if sentiment not in ["Positive", "Negative", "Neutral"]:
                sentiment = "Neutral"

            item.sentiment = sentiment
            db.add(item)

        except Exception as e:
            print(f"❌ Error processing feedback ID {item.id}: {e}")
            continue

    db.commit()
    return {"message": "Sentiment analysis completed successfully ✅"}


# @router.post("/analyze-sentiment/")
# def analyze_sentiment(db: Session = Depends(get_db)):
#     # ✅ Initialize Groq client inside the route to avoid blocking FastAPI
#     client = openai.OpenAI(
#         api_key=os.getenv("GROQ_API_KEY"),
#         base_url="https://api.groq.com/openai/v1"
#     )

#     feedbacks = db.query(SurveyFeedback).filter(SurveyFeedback.sentiment == "Not Processed").all()

#     if not feedbacks:
#         return {"message": "No unprocessed feedback found."}