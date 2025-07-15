from db.database import Base, engine
from models.survey import SurveyFeedback

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("✅ Table dropped and recreated successfully.")
