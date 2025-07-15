from sqlalchemy import Column, Integer, String, Text
from db.database import Base

# creates table to store data
class SurveyFeedback(Base):
    __tablename__ = "survey_feedback"

    id = Column(Integer, primary_key=True, index=True)
    respondent = Column(String, index=True)
    feedback = Column(Text, nullable=False)
    sentiment = Column(String, index=True)
    ############################################
    upload_session_id = Column(String, index=True)
