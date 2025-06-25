import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# groq_api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key, max_retries=3)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    max_retries=3,
    temperature=0.1,
)

