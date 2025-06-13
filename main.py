import os
from dotenv import load_dotenv
import streamlit as st
from langgraph.graph import StateGraph
from llm import generate_response


def main():
    st.title("Linkedin Assistant")
    messages = {}

    prompt = st.chat_input("How can I help you?")
    
    if prompt:

        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.session_state["messages"].append({'role':'user',
                         'content':prompt})
        st.session_state["messages"].append({'role':'ai',
                         'content':generate_response(prompt)})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


        



if __name__ == "__main__":
    main()
