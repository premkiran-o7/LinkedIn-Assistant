from typing_extensions import TypedDict
from typing import  Optional, Annotated, List, Dict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import enum

class Intent(enum.Enum):
    UPDATE_SUMMARY_SECTION = "enhance_summary"
    SUGGEST_SKILLS = "suggest_skills"
    SUGGEST_CERTIFICATIONS = "suggest_certifications"
    GENERATE_JOB_DESCRIPTION = "generate_job_description"
    ANALYZE_SKILL_GAP = "analyze_skill_gap"
    ANALYZE_PROFILE = "analyze_profile"
    GENERATE_CAREER_PLAN = "generate_career_plan"
    GENERAL_RESPONSE = "general_response"
    ENHANCE_HEADLINE = "enhance_headline"


class ProfileState(TypedDict, total=False):
    # Basic imported profile fields
    user_query : str
    name: str
    headline: str
    occupation: str
    education: List[Dict]
    honors: List[Dict]
    volunteerExperiences: List[Dict]
    skills: List[str]
    experience: List[Dict]
    certifications: List[Dict]
    courses: List[Dict]
    summary: str
    about: str
    student : bool
    companyName : str
    countryCode: str
    profileId: str
    publicIdentifier: str
    industryName: str
    geoLocationName: str
    geoCountryName: str
    followersCount: int
    connectionsCount: int
    languages: List[Dict]

    # Optional job-related context
    job_description: str
    target_title: str

    # Analyzed/improved data
    suggested_summary: str 
    suggested_certifications: List[str]
    suggested_skills: List[str]
    Negative_Remarks: str
    analysis_profile: str
    career_plan: str
    skill_gap_analysis: str

    messages: Annotated[List[BaseMessage], add_messages] 
