import os
import streamlit as st
from dotenv import load_dotenv
from graph import initialize_state
from state import ProfileState
from graph import career_graph  # LangGraph you built
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# Load environment variables if any
load_dotenv()

# Generate unique thread ID once
if "thread" not in st.session_state:
    st.session_state["thread"] = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

# Initialize message history & profile state
st.session_state.setdefault("messages", [])
st.session_state.setdefault("profile_state", None)
st.session_state.setdefault("linkedin_url", "")

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

    # Sidebar for LinkedIn URL input
    with st.sidebar:
        st.subheader("Load LinkedIn Profile")
        # Sidebar for LinkedIn URL input
with st.sidebar:
    st.subheader("Load LinkedIn Profile")
    
    linkedin_url_input = st.text_input(
        "Enter LinkedIn Profile URL", 
        value=st.session_state.get("linkedin_url", "")
    )
    
    update_clicked = st.button("Update Profile")

    if update_clicked:
        current_url = st.session_state.get("linkedin_url", "")
        
        if linkedin_url_input.strip() == "":
            st.warning("Please enter a LinkedIn URL.")
        
        elif linkedin_url_input == current_url:
            st.info("This profile is already loaded.")
        
        else:
            with st.spinner("Loading profile..."):
                # Call your profile loader
                st.session_state["profile_state"] = initialize_state({}, linkedin_url_input)
                st.session_state["linkedin_url"] = linkedin_url_input  # Persist URL across reruns
            st.success("Profile loaded successfully!")


    # Check if profile is loaded
    if st.session_state["profile_state"] is not None:
        # Chat interface
        user_input = st.chat_input("How can I help you?")

        if user_input:
            # Append user message
            st.session_state["messages"].append({
                "type": "human",
                "content": user_input
            })

            # Update state with user query & message history
            st.session_state["profile_state"]["user_query"] = user_input
            st.session_state["profile_state"]["messages"] = [
                convert_message_obj_to_lc(msg) for msg in st.session_state["messages"]
            ]

            # Call LangGraph agent
            output = career_graph.invoke(st.session_state["profile_state"], st.session_state["thread"])

            # Get AI response
            ai_response = output.get("messages", [])[-1].content if output.get("messages") else "No response"
            st.session_state["messages"].append({
                "type": "ai",
                "content": ai_response
            })

            # Update profile state for next turn
            st.session_state["profile_state"] = output

        # Render chat history
        for message in st.session_state["messages"]:
            role = "User" if message["type"] == "human" else "AI"
            content = message.get("content", "")
            if content:
                st.chat_message(role).markdown(content)
                
    else:
        st.warning("Please enter a LinkedIn profile URL in the sidebar to start.")


if __name__ == "__main__":
    main()
