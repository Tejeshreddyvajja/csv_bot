# Feedback Chatbot

This repository contains a Feedback Chatbot application, including both a frontend interface and backend API to upload, analyze, and visualize feedback data.

## Features

- 💬 Chat with an AI chatbot about feedback data
- 📤 Upload feedback CSV files for analysis
- 📊 View sentiment analysis charts and visualizations
- 🤖 AI-powered sentiment analysis using CrewAI
- 🔍 Vector database search for feedback insights

## Project Structure

```
├── backend/
│   ├── agents/          # CrewAI agents for chatbot and sentiment analysis
│   ├── db/              # Database models and connection
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # FastAPI route handlers
│   └── main.py          # FastAPI application entry point
├── frontend_streamlit.py # Streamlit frontend application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Tejeshreddyvajja/csv_bot.git
   cd csv_bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the `backend/` directory with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

### Running the Frontend

1. In a new terminal, run the Streamlit app:
   ```bash
   streamlit run frontend_streamlit.py
   ```

   The web interface will be available at `http://localhost:8501`

## Features Overview

### CSV Upload
- Upload CSV files with `respondent` and `feedback` columns
- Automatic sentiment analysis using AI agents
- Vector database creation for efficient searching

### AI Chatbot
- Query your feedback data using natural language
- Get insights and summaries about customer feedback
- Powered by CrewAI for intelligent responses

### Sentiment Analysis
- Automatic sentiment classification (Positive, Negative, Neutral)
- Visual charts showing sentiment distribution
- Real-time analysis on uploaded data

## API Endpoints

- `POST /upload-csv/` - Upload and process feedback CSV files
- `POST /chat-with-crew/` - Chat with AI about feedback data
- `GET /sentiment-chart/` - Get sentiment analysis visualization

## Technologies Used

- **FastAPI** - Backend web framework
- **Streamlit** - Frontend web interface
- **CrewAI** - AI agent framework
- **LangChain** - LLM integration and vector stores
- **Chroma** - Vector database for embeddings
- **SQLAlchemy** - Database ORM
- **Pandas** - Data manipulation
- **HuggingFace** - Text embeddings

## Contributing

Feel free to open issues or create pull requests to improve this project.

## License

This project is open source and available under the MIT License.
