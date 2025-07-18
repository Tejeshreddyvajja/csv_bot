# Import configuration first to suppress warnings
import sys
sys.path.append('..')
from config import setup_environment
setup_environment()

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatLiteLLM
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm():
    return ChatOpenAI(
        temperature=0.7,
        model="gpt-4",  # You can switch to "gpt-3.5-turbo" if needed
        api_key=os.getenv("OPENAI_API_KEY")
    )

# def get_llm():
#     return ChatLiteLLM(
#         model="llama3-70b-8192",
#         litellm_params={
#             "model": "llama3-70b-8192",
#             "api_base": "https://api.groq.com/openai/v1",
#             "api_key": os.getenv("GROQ_API_KEY"),
#             "litellm_provider": "groq"
#         }
#     )


# def run_crew(user_question: str, feedback_data: str):
#     feedback_analyst = Agent(
#         role="Feedback Analyst",
#         goal="Analyze the feedback and answer user queries",
#         backstory=(
#             "You are an expert at understanding customer feedback and turning it into meaningful insights."
#         ),
#         verbose=True,
#         allow_delegation=False, 
#         llm=get_llm()
#     )

#     task = Task(
#         description=f"Use the following feedback data to answer the user's question:\n\nFeedback:\n{feedback_data}\n\nQuestion: {user_question}",
#         agent=feedback_analyst,
#         expected_output="A clear and useful response to the user's query based on the feedback data."
#     )

#     crew = Crew(
#         agents=[feedback_analyst],
#         tasks=[task],
#         verbose=True
#     )

#     result= crew.kickoff()
#     print(result)
def run_crew(user_question: str, chroma_path: str = "./chroma_store"):
    try:
        # Load the vector store
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(
            persist_directory=chroma_path,
            embedding_function=embedding_model
        )
        
        # Search for relevant feedback based on the question
        relevant_docs = vectorstore.similarity_search(user_question, k=5)
        if not relevant_docs:
            return "I couldn't find any relevant feedback to answer your question."

        # Build context for the agent
        feedback_context = "\n".join(
            f"{i+1}. {doc.page_content} (from {doc.metadata.get('respondent', 'Unknown')})"
            for i, doc in enumerate(relevant_docs)
        )

    except Exception as e:
        return f"Error while retrieving feedback: {str(e)}"

    # Create the Agent
    feedback_analyst = Agent(
        role="Customer Feedback Analyst",
        goal="Answer user questions using customer feedback",
        backstory=(
            "You analyze customer feedback and answer queries with insights backed by actual responses."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )

    # Create the Task
    task = Task(
    description=(
        "You are a helpful assistant analyzing customer feedback.\n"
        "Speak naturally and conversationally like you're talking to a human.\n\n"
        "Use the feedback below to answer the user's question.\n\n"
        f"Feedback Data:\n{feedback_context}\n\n"
        f"User Question: {user_question}\n\n"
        "Respond in a warm, friendly tone. Mention the number of positive responses and summarize them like you're explaining to a person."
    ),
    agent=feedback_analyst,
    expected_output=(
        "A human-like, friendly, and easy-to-understand answer to the user's question, "
        "clearly highlighting the number of relevant responses and key points."
    )
)


    # Run the Crew
    crew = Crew(
        agents=[feedback_analyst],
        tasks=[task],
        verbose=True
    )

    try:
        result = crew.kickoff()

        # Extract the actual answer safely
        if isinstance(result, dict):
            answer = result.get("tasks_output", [{}])[0].get("raw") or result.get("raw")
        else:
            answer = str(result)

        return answer

    except Exception as e:
        return f"CrewAI failed to generate a response: {e}"
