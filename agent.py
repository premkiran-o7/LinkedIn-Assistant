# agent.py

from langchain.agents import create_react_agent
from langchain.agents.executor import AgentExecutor
from nodes import (
    enhance_summary,
    suggest_skills,
    suggest_certifications,
    generate_job_description,
    analyze_skill_gap,
    analyze_profile,
    generate_career_plan,
    comprehensive_profile_analysis
)

def create_react_linkedin_agent(llm, verbose: bool = False) -> AgentExecutor:
    """
    Creates a ReAct-style agent that uses custom tools to help users optimize their LinkedIn presence.

    Args:
        llm: The initialized LLM (ChatLlama3, OpenAI, Claude, etc.)
        verbose: Whether to log reasoning steps.

    Returns:
        AgentExecutor instance ready to handle dynamic user queries.
    """
    tools = [
        enhance_summary,
        suggest_skills,
        suggest_certifications,
        generate_job_description,
        analyze_skill_gap,
        analyze_profile,
        generate_career_plan,
        comprehensive_profile_analysis,
    ]

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=None  # Optional: use default ReAct prompt or inject your own here
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)
