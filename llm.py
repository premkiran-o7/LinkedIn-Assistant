import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key, max_retries=3)



