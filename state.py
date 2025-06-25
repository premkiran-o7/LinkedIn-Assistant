from typing_extensions import TypedDict
from typing import  Optional, Annotated, List, Dict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import enum

class Intent(enum.Enum):
    UPDATE_SUMMARY_OR_ABOUT_SECTION = "enhance_summary"
    SUGGEST_SKILLS = "suggest_skills"
    SUGGEST_CERTIFICATIONS = "suggest_certifications"
    GENERATE_JOB_DESCRIPTION = "generate_job_description"
    ANALYZE_SKILL_GAP = "analyze_skill_gap"
    ANALYZE_PROFILE = "analyze_profile"
    GENERATE_CAREER_PLAN = "generate_career_plan"
    GENERAL_RESPONSE = "general_response"
    ENHANCE_HEADLINE = "enhance_headline"
    ANALYZE_JOB_MATCH = "analyze_job_match"
    ANALYZE_PROFILE_ISSUES = "analyze_profile_issues"


class ProfileState(TypedDict, total=False):
    # Basic imported profile fields
    user_query: str
    name: str
    headline: str
    occupation: str
    education: str
    honors: str
    volunteerExperiences: str
    skills: str
    experience: str
    certifications: str
    courses: str
    summary: str
    student: str  # bool -> str
    companyName: str
    countryCode: str
    profileId: str
    publicIdentifier: str
    industryName: str
    geoLocationName: str
    geoCountryName: str
    followersCount: str  # int -> str
    connectionsCount: str  # int -> str
    languages: str

    # Optional job-related context
    job_description: str
    target_title: str

    # Analyzed/improved data
    suggested_summary: str
    suggested_certifications: str  # List[str] -> str
    suggested_skills: str          # List[str] -> str
    profile_issues: str
    profile_analysis: str
    career_plan: str
    skill_gap_analysis: str
    job_match_analysis: str

    messages: Annotated[List[BaseMessage], add_messages]