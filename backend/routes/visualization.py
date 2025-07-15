from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.survey import SurveyFeedback
import matplotlib.pyplot as plt
import pandas as pd
import io

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        ##################################################
def get_latest_session_id(db: Session):
    result = db.query(SurveyFeedback.upload_session_id)\
               .order_by(SurveyFeedback.id.desc())\
               .first()
    return result[0] if result else None

@router.get("/sentiment-chart/")
def sentiment_chart(db: Session = Depends(get_db)):
    session_id = get_latest_session_id(db)
    if not session_id:
        return {"message": "No data to visualize."}
    feedbacks = db.query(SurveyFeedback)\
              .filter(SurveyFeedback.upload_session_id == session_id)\
              .all()


    # Convert to dataframe
    data = [{"sentiment": item.sentiment} for item in feedbacks]
    df = pd.DataFrame(data)

    if df.empty:
        return {"message": "No data found"}

    # Count sentiments
    sentiment_counts = df["sentiment"].value_counts()

    # Plot
    plt.figure(figsize=(6,4))
    sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'])
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")
