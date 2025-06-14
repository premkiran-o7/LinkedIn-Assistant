import json
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from llm import llm
from state import ProfileState
from typing import List, Dict, Optional, Annotated
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from state import Intent
import os
from dotenv import load_dotenv
from apify_client import ApifyClient
import streamlit as st
import base64
from prompts import job_description_generation_prompt

from nodes import (
    enhance_summary,
    suggest_skills,
    suggest_certifications,
    generate_job_description,
    analyze_skill_gap,
    analyze_profile,
    generate_career_plan,
    comprehensive_profile_analysis,
    update_about_section,
    general_response,
    extract_and_update_job_title
)

load_dotenv()  # Load environment variables from .env file
def initialize_state(state: ProfileState, profile_url: str):
    # Initialize Apify client with your API token
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    
    client = ApifyClient(APIFY_TOKEN)

    with open("cookies.json", "r") as f:
        cookie_data = json.load(f)
    



    # Prepare actor input — scrape a specific profile
    run_input = {
        "urls": [profile_url],  # pass the LinkedIn profile URL
        "cookie": cookie_data,
        "minDelay": 15,
        "maxDelay": 60,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyCountry": "US",
        },
        "findContacts.contactCompassToken": "",
    }

    print("Starting LinkedIn scraping on Apify...")

    # Run the Apify actor
    run = client.actor("curious_coder/linkedin-profile-scraper").call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]

    # Fetch scraped profile data
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        raise ValueError("No profile data returned from Apify.")

    profile = items[0]

    # Map Apify profile fields to your state
    state["name"] = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
    state["headline"] = profile.get("headline", "")
    state["occupation"] = profile.get("occupation", "")
    state["education"] = profile.get("education", [])  
    state["honors"] = profile.get("honors", [])
    state["volunteerExperiences"] = profile.get("volunteerExperiences", [])  # Apify field is 'volunteer'
    state["skills"] = profile.get("skills", [])
    state["experience"] = profile.get("experience", [])
    state["certifications"] = profile.get("certifications", [])
    state["summary"] = profile.get("summary", "")
    state["student"] = profile.get("student", False)
    state["companyName"] = profile.get("companyName", "")
    state["countryCode"] = profile.get("countryCode", "")

    # Initialize new fields
    state["messages"] = [
        SystemMessage(content="""You are a LinkedIn Career Coach. 
You analyze profiles, suggest improvements, recommend skills and certifications, and help users achieve target job roles.
Always evaluate if a tool should be called to answer the user query. If appropriate, call the relevant tool. 
Else, respond directly.""")
    ]

    state["suggested_summary"] = ""
    state["suggested_certifications"] = []
    state["suggested_skills"] = []
    state["analysis_profile"] = ""
    state["career_plan"] = ""
    state["skill_gap_analysis"] = ""
    state["Negative_Remarks"] = ""

    # Use occupation as target title (or modify if you have another logic)
    state["target_title"] = profile.get("occupation", "")

    # Optional: Generate job description
    if state["target_title"]:
        print("Generating job description for target title:", state["target_title"])
        jd_response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Generate a professional job description."),
            HumanMessage(content=job_description_generation_prompt.format(
                target_title=state["target_title"]
            )),
            HumanMessage(content=f"Generate job description for {state['target_title']}")
        ])
        state["messages"].append(AIMessage(content=jd_response.content))
        state["job_description"] = jd_response.content
    else:
        state["job_description"] = ""

    print("Initialization complete.")
    return state




def router(state: ProfileState) -> Intent:
    user_query = state["user_query"]

    classification_prompt = f"""
You are an intent classifier. Given the user input, classify it into one of the following actions:
{', '.join([i.value for i in Intent])}

User input: {user_query}

Return only the action name.
"""

    response = llm.invoke([
        SystemMessage(content=classification_prompt)
    ])

    raw_intent = response.content.strip().lower()

    # Match to enum safely
    for intent in Intent:
        if raw_intent == intent.value:
            print(f"Routing to: {intent.value}")
            return intent.value
    
    print("Routing to: general_response (fallback)")
    return Intent.GENERAL_RESPONSE.value


# ------------------ BUILDING THE GRAPH ------------------

graph = StateGraph(ProfileState)

# Register all nodes
graph.add_node("extract_and_update_job_title", extract_and_update_job_title)
graph.add_node("enhance_summary", enhance_summary)
graph.add_node("suggest_skills", suggest_skills)
graph.add_node("suggest_certifications", suggest_certifications)
graph.add_node("generate_job_description", generate_job_description)
graph.add_node("analyze_skill_gap", analyze_skill_gap)
graph.add_node("analyze_profile", analyze_profile)
graph.add_node("generate_career_plan", generate_career_plan)
graph.add_node("comprehensive_profile_analysis", comprehensive_profile_analysis)
graph.add_node("general_response", general_response)

# Entry point
graph.add_edge(START,"extract_and_update_job_title")

# Conditional routing
graph.add_conditional_edges(
    "extract_and_update_job_title",
    router,
    {
        "enhance_summary": "enhance_summary",
        "suggest_skills": "suggest_skills",
        "suggest_certifications": "suggest_certifications",
        "generate_job_description": "generate_job_description",
        "analyze_skill_gap": "analyze_skill_gap",
        "analyze_profile": "analyze_profile",
        "generate_career_plan": "generate_career_plan",
        "comprehensive_profile_analysis": "comprehensive_profile_analysis",
        "general_response": "general_response"
    }
)

career_graph = graph.compile(checkpointer=MemorySaver())