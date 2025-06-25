from llm import llm
from state import ProfileState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json

from prompts import (
    enhance_summary_prompt,
    suggest_skills_prompt,
    suggest_certifications_prompt,
    job_description_generation_prompt,
    skill_gap_analysis_prompt,
    profile_issues_prompt,
    career_path_prompt,
    profile_analysis_prompt,
    extraction_prompt,
    general_response_prompt,
    enhance_headline_prompt,
    job_match_analysis_prompt
)



def general_response(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            HumanMessage(content=general_response_prompt.format(**state))
        ])
        content = response.content
    except Exception as e:
        content = f"Error: {str(e)}"
    state["messages"].append(AIMessage(content=content))
    return state


def extract_and_update_job_title(state: ProfileState) -> ProfileState:
    user_query = state["user_query"]
    
    
    try:
        response = llm.invoke([
            *state["messages"],
            HumanMessage(content=extraction_prompt.format(
                user_query=state.get("user_query", "Please provide more details about your request."),
                target_title=state.get("target_title", ""),
            )),
        ])

        extracted_title = response.content.strip()
        content = response.content
    except Exception as e:
        content = f"Error: {str(e)}"
        state["messages"].append(AIMessage(content=content))
        return state
    
    
       
    # Compare with existing title
    existing_title = state.get("target_title", "").lower()
    
    if extracted_title.lower() != existing_title and extracted_title.lower() != "none":
        print(f"Updated job title from '{existing_title}' to '{extracted_title}'")
        state["target_title"] = extracted_title
        try:
            jd_response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Generate a professional job description."),
            HumanMessage(content=job_description_generation_prompt.format(
                target_title=extracted_title
            )),
            HumanMessage(content=f"Generate job description for {extracted_title}")
            ])
            state["messages"].append(AIMessage(content=jd_response.content))
            state["job_description"] = jd_response.content
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Error generating job description: {str(e)}"))

    else:
        print("Job title remains unchanged")  # Optional: clear previous JD if title changes

    return state


# ✅ Enhance Summary Node
def enhance_summary(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Enhance LinkedIn summary based on target role."),
            HumanMessage(content=enhance_summary_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Please optimize my summary"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["suggested_summary"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error enhancing summary: {str(e)}"))
    return state

# ✅ Suggest Skills Node
def suggest_skills(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Suggest skills based on job description and profile."),
            HumanMessage(content=suggest_skills_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Suggest skills"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["suggested_skills"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error suggesting skills: {str(e)}"))
    return state

# ✅ Suggest Certifications Node
def suggest_certifications(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Suggest certifications to boost profile credibility."),
            HumanMessage(content=suggest_certifications_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Suggest certifications"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["suggested_certifications"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error suggesting certifications: {str(e)}"))
    return state

# ✅ Generate Job Description Node
def generate_job_description(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Generate a professional job description."),
            HumanMessage(content=job_description_generation_prompt.format(
                target_title=state.get("target_title", "")
            )),
            HumanMessage(content=f"Generate job description for {state.get('target_title', '')}")
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["job_description"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error generating job description: {str(e)}"))
    return state

# ✅ Skill Gap Analysis Node
def analyze_skill_gap(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Perform skill gap analysis."),
            HumanMessage(content=skill_gap_analysis_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Analyze skill gap"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["skill_gap_analysis"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error analyzing skill gap: {str(e)}"))
    return state
    
def analyze_profile_issues(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Analyze profile issues."),
            HumanMessage(content=profile_issues_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Analyze issues with profile"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["profile_issues"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error analyzing issues with profile gap: {str(e)}"))
    return state
    

# ✅ Profile Audit Node
def analyze_profile(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Analyze the LinkedIn profile."),
            HumanMessage(content=profile_analysis_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Analyze the LinkedIn profile."))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["profile_analysis"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error auditing profile: {str(e)}"))
        state["profile_analysis"] = f"Error: {str(e)}"
    return state


# ✅ Career Plan Generator Node
def generate_career_plan(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Generate career roadmap."),
            HumanMessage(content=career_path_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Create career path"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["career_plan"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error generating career plan: {str(e)}"))
    return state

# ✅ Full Profile Analysis Node
def analyze_job_match(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            HumanMessage(content=job_match_analysis_prompt.format(**state))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["job_match_analysis"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error conducting profile analysis: {str(e)}"))
    
    return state

# ✅ Enhance Headline Node
def enhance_headline(state: ProfileState) -> ProfileState:
    try:
        response = llm.invoke([
            *state["messages"],
            SystemMessage(content="Enhance LinkedIn headline based on target role."),
            HumanMessage(content=enhance_headline_prompt.format(**state)),
            HumanMessage(content=state.get("user_query", "Please optimize my headline"))
        ])
        state["messages"].append(AIMessage(content=response.content))
        state["headline"] = response.content
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error enhancing headline: {str(e)}"))
    return state



