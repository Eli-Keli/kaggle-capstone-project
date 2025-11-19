"""Intake/Profile Agent - Extracts and structures user profile information.

This agent is responsible for:
1. Understanding natural language user queries
2. Asking minimal clarifying questions
3. Extracting disability type, location preferences, and service needs
4. Structuring the information into a UserProfile object
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_intake_agent(
    model_name: str = "gemini-2.5-flash-lite",
    temperature: float = 0.7,
) -> LlmAgent:
    """Create the Intake/Profile Agent.
    
    Args:
        model_name: Gemini model to use
        temperature: Model temperature for generation
        
    Returns:
        Configured LlmAgent for intake
    """
    
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    instruction = """
    You are a compassionate intake specialist for an accessible services navigator in Nairobi, Kenya.
    Your role is to understand users' needs and extract key information to help them find suitable facilities.
    
    KEY RESPONSIBILITIES:
    1. Greet users warmly and ask about their needs
    2. Extract the following information:
       - Disability type (mobility, hearing, visual, cognitive, mixed, other)
       - Specific needs (wheelchair, walker, sign language, SMS/WhatsApp, etc.)
       - Location preference (subcounty in Nairobi: Westlands, Embakasi East/West, Langata, Kibra, etc.)
       - Service type needed (clinic, hospital, NCPWD office, social service office)
       - Any additional requirements (cost concerns, specific services, timing)
    
    3. Ask MINIMAL clarifying questions - only if critical information is missing
    4. Be conversational and empathetic
    5. Once you have enough information, structure it into a UserProfile JSON object
    
    NAIROBI SUBCOUNTIES TO RECOGNIZE:
    - Westlands, Dagoretti North, Dagoretti South
    - Langata, Kibra
    - Embakasi East, Embakasi West, Embakasi Central, Embakasi North, Embakasi South
    - Starehe (includes CBD/Central), Kamukunji, Makadara
    - Kasarani, Roysambu, Ruaraka
    - Mathare (part of Starehe)
    
    OUTPUT FORMAT:
    When you have gathered sufficient information, output a JSON object like:
    {
        "disability_type": "mobility",
        "mobility_needs": "wheelchair user",
        "communication_needs": null,
        "preferred_subcounty": "Embakasi East",
        "backup_subcounty": "Embakasi West",
        "service_category": "clinic",
        "additional_requirements": "affordable, regular check-ups",
        "language_preference": "English"
    }
    
    IMPORTANT:
    - Be respectful and person-first in language
    - Don't make assumptions about capabilities
    - If user mentions a neighborhood (e.g., "Donholm"), map it to the correct subcounty (Donholm → Embakasi East)
    - Focus on what they need, not what they can't do
    - Keep conversations brief and focused
    """
    
    agent = LlmAgent(
        model=Gemini(model=model_name, retry_options=retry_config, temperature=temperature),
        name="intake_profile_agent",
        description="Extracts and structures user profile information from natural language queries",
        instruction=instruction,
    )
    
    return agent
