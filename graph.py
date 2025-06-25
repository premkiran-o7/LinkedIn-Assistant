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
    analyze_job_match,
    general_response,
    extract_and_update_job_title,
    enhance_headline,
    analyze_profile_issues,
    suggest_courses
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

    # # Fetch scraped profile data
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        raise ValueError("No profile data returned from Apify.")

    # For testing, let's use a local JSON file instead of Apify
    # with open("profile.json", "r") as f:
    #     items = json.load(f)
    profile = items[0] 

    # Map Apify profile fields to your state with conversion
    state["name"] = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
    state["headline"] = profile.get("headline", "")
    state["occupation"] = profile.get("occupation", "")
    state["education"] = json.dumps(profile.get("educations", []))  
    state["volunteerExperiences"] = json.dumps(profile.get("volunteerExperiences", []))
    state["skills"] = ", ".join(profile.get("skills", []))
    state["experience"] = json.dumps(profile.get("positions", []))
    state["certifications"] = json.dumps(profile.get("certifications", []))
    state["honors"] = json.dumps(profile.get("honors", []))
    state["courses"] = json.dumps(profile.get("courses", []))
    state["summary"] = profile.get("summary", "")
    state["student"] = str(profile.get("student", False))
    state["companyName"] = profile.get("companyName", "")
    state["countryCode"] = profile.get("countryCode", "")
    state["profileId"] = profile.get("profileId", "")
    state["publicIdentifier"] = profile.get("publicIdentifier", "")
    state["industryName"] = profile.get("industryName", "")
    state["geoLocationName"] = profile.get("geoLocationName", "")
    state["geoCountryName"] = profile.get("geoCountryName", "")
    state["followersCount"] = str(profile.get("followersCount", 0))
    state["connectionsCount"] = str(profile.get("connectionsCount", 0))
    state["languages"] = json.dumps(profile.get("languages", []))

    # Initialize new fields
    state["messages"] = [
        SystemMessage(content="""You are a LinkedIn Career Coach. 
You analyze profiles, suggest improvements, recommend skills and certifications, and help users achieve target job roles.
Always evaluate if a tool should be called to answer the user query. If appropriate, call the relevant tool. 
Else, respond directly.""")
    ]

    state["suggested_summary"] = ""
    state["suggested_certifications"] = ""
    state["suggested_skills"] = ""
    state["analysis_profile"] = ""
    state["career_plan"] = ""
    state["skill_gap_analysis"] = ""
    state["job_match_analysis"] = ""
    state["profile_issues"] = ""
    state["suggested_courses"] = ""

    # Use occupation as target title (or modify if you have another logic)
    state["target_title"] = state["occupation"]

    # Optional: Generate job description
    if state["target_title"]:
        print("Generating job description for target title:", state["target_title"])
        jd_response = llm.invoke([
            *state["messages"],
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
# Instruction
You are an expert intent classifier. Given a user's input, identify the most appropriate action from the list below. 
Each action represents a possible user intent for improving or analyzing a LinkedIn profile.

# Action List
{', '.join([intent.name for intent in Intent])}

# Guidelines
- Read the user input carefully.
- Choose only **one** intent from the list.
- If the input doesn't clearly match any intent, choose `GENERAL_RESPONSE`.

# User Input
{user_query}

# Response Format
Only return one of the following enum names:
{', '.join([intent.name for intent in Intent])}
"""


    try:
        response = llm.invoke([
            HumanMessage(content=classification_prompt)
        ])

        raw_intent = response.content.strip().lower()

        # Match to enum safely
        for intent in Intent:
            if raw_intent == intent.name:
                print(f"Routing to: {intent.value}")
                return intent.value

    except Exception as e:
        print("Routing to: general_response (fallback)")
        return Intent.GENERAL_RESPONSE.value
    
    print("Intent unrecognized — fallback to general_response")
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
graph.add_node("analyze_job_match", analyze_job_match
)
graph.add_node("enhance_headline", enhance_headline)
graph.add_node("general_response", general_response)
graph.add_node("analyze_profile_issues", analyze_profile_issues)
graph.add_node("suggest_courses", suggest_courses)

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
        "analyze_job_match": "analyze_job_match",
        "enhance_headline": "enhance_headline",
        "general_response": "general_response",
        "analyze_profile_issues": "analyze_profile_issues",
        "suggest_courses": "suggest_courses"
    }
)

career_graph = graph.compile(checkpointer=MemorySaver())