import os
import streamlit as st
from dotenv import load_dotenv
from graph import initialize_state

from state import ProfileState
from graph import career_graph  # Full LangGraph graph we built
from langchain_core.messages import HumanMessage, AIMessage

import uuid

thread = {
    "configurable": {
        "thread_id": str(uuid.uuid4())
    }
}

# Load environment variables if needed
load_dotenv()
st.session_state.setdefault("messages", [])
state: ProfileState = {}

def convert_message_obj_to_lc(msg):
    if msg["type"] == "human":
        return HumanMessage(content=msg["content"])
    elif msg["type"] == "ai":
        return AIMessage(content=msg["content"])
    else:
        raise ValueError("Unknown message type.")

def main():
    st.set_page_config(page_title="LinkedIn Career Coach", page_icon="🧑‍💼")
    st.title("LinkedIn Career Coach")

    # Sidebar for LinkedIn URL and profile loading
    with st.sidebar:
        st.subheader("Load LinkedIn Profile")
        linkedin_url = st.text_input("Enter LinkedIn Profile URL")
        update_clicked = st.button("Update Profile")

        if update_clicked:
            st.session_state.profile_state = initialize_state({}, linkedin_url)
            st.success("Profile loaded successfully!")

    # Chat interface
    prompt = st.chat_input("How can I help you?")

    if prompt:
        # Append user message
        st.session_state['messages'].append({
            "type": "human",
            "content": prompt
        })

        # Update state with user query
        st.session_state.profile_state["user_query"] = prompt
        st.session_state.profile_state["messages"] = [
            convert_message_obj_to_lc(msg) for msg in st.session_state['messages']
        ]

        # Call LangGraph
        output = career_graph.invoke(st.session_state.profile_state,thread)

        # Extract AI response
        ai_response = output['messages'][-1].content if output.get('messages') else "No response"
        st.session_state['messages'].append({
            "type": "ai",
            "content": ai_response
        })

        # Update profile_state for next round
        st.session_state.profile_state = output

    # Render chat history
    for message in st.session_state['messages']:
        role = "User" if message["type"] == "human" else "AI"
        content = message.get("content", "")
        if content:
            st.chat_message(role).markdown(content)





if __name__ == "__main__":
    main()