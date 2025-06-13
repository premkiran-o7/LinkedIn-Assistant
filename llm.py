import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEy")
llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)


def generate_response(prompt:str):
    response = llm.invoke(prompt)
    return response.content



