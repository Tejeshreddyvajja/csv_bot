import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatLiteLLM
from langchain_openai import ChatOpenAI


load_dotenv()

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
def get_llm():
    return ChatOpenAI(
        temperature=0.2,
        model="gpt-3.5-turbo-0125",  # You can switch to "gpt-3.5-turbo" if needed
        api_key=os.getenv("OPENAI_API_KEY")
    )

def run_sentiment_crew(feedback_items: list):
    feedback_text = "\n".join([
        f"{item['id']}: {item['text']}" for item in feedback_items
    ])

    prompt = (
        "You are a sentiment analysis agent. For each feedback entry below, classify it as 'Positive', 'Negative', or 'Neutral'. "
        "Return the result as a JSON list like this:\n\n"
        "[{\"id\": 1, \"sentiment\": \"Positive\"}, {\"id\": 2, \"sentiment\": \"Negative\"}]\n\n"
        f"Feedback data:\n{feedback_text}"
    )

    agent = Agent(
        role="Sentiment Classifier",
        goal="Analyze feedback and classify sentiment as Positive, Negative, or Neutral",
        backstory="You are an expert sentiment analyzer for customer feedback.",
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )

    task = Task(
        description=prompt,
        agent=agent,
        expected_output="A JSON list with sentiment classification for each feedback item."
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    return str(result)  