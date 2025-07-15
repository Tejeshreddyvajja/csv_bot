from routes import visualization
from fastapi import FastAPI
from routes import upload, visualization,sentiment
from routes import chatbot 
from routes import crew_chat
from routes import api


app = FastAPI(title="Survey Insights API")

# ✅ Register all routes
app.include_router(upload.router)
# app.include_router(sentiment.router)
app.include_router(visualization.router)
# app.include_router(chatbot.router)  
app.include_router(crew_chat.router)
# app.include_router(api.router)


@app.get("/")
def read_root():
    return {"message": "Survey Insights API is running 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
