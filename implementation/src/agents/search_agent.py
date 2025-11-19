"""Search Agent - Searches and filters facilities based on user needs.

This agent is responsible for:
1. Receiving structured UserProfile from Intake Agent
2. Using DatasetSearchTool to filter facilities
3. Optionally using WebEnrichmentTool for additional context
4. Returning CandidateFacilities list
"""

from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

from src.tools.dataset_search import DatasetSearchTool
from src.tools.web_enrichment import WebEnrichmentTool


def create_search_agent(
    model_name: str = "gemini-2.5-flash-lite",
    temperature: float = 0.3,
    data_path: Optional[str] = None,
    enable_web_enrichment: bool = False,
) -> LlmAgent:
    """Create the Search Agent.
    
    Args:
        model_name: Gemini model to use
        temperature: Model temperature (lower for more deterministic search)
        data_path: Path to data directory
        enable_web_enrichment: Whether to enable web enrichment
        
    Returns:
        Configured LlmAgent for search
    """
    
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    # Initialize tools
    dataset_tool = DatasetSearchTool(data_path=data_path)
    web_tool = WebEnrichmentTool(enabled=enable_web_enrichment)
    
    # Create search function that the agent can call
    def search_facilities_tool(
        disability_type: str,
        preferred_subcounty: str,
        service_category: str,
        backup_subcounty: str = None,
        max_results: int = 10,
    ) -> str:
        """Search for facilities matching user requirements.
        
        Args:
            disability_type: Type of disability (mobility, hearing, visual, etc.)
            preferred_subcounty: Preferred location in Nairobi
            service_category: Type of service (clinic, hospital, ncpwd_office, social_service)
            backup_subcounty: Alternative location if preferred not available
            max_results: Maximum facilities to return
            
        Returns:
            JSON string with candidate facilities and metadata
        """
        from src.models.schemas import UserProfile, DisabilityType, ServiceCategory
        
        # Convert string inputs to enum types
        try:
            disability_enum = DisabilityType(disability_type.lower())
        except ValueError:
            disability_enum = DisabilityType.OTHER
        
        try:
            service_enum = ServiceCategory(service_category.lower())
        except ValueError:
            service_enum = ServiceCategory.CLINIC
        
        # Create user profile
        profile = UserProfile(
            disability_type=disability_enum,
            preferred_subcounty=preferred_subcounty,
            backup_subcounty=backup_subcounty,
            service_category=service_enum,
        )
        
        # Search facilities
        candidates = dataset_tool.search_facilities(
            user_profile=profile,
            max_results=max_results,
        )
        
        # Optionally enrich with web data
        if enable_web_enrichment and candidates.facilities:
            candidates.facilities = web_tool.enrich_facilities(
                candidates.facilities,
                max_facilities=3,
            )
        
        # Convert to JSON for agent
        return candidates.model_dump_json(indent=2)
    
    instruction = """
    You are a facility search specialist for the Accessible Services Navigator.
    Your role is to find the most suitable facilities based on user requirements.
    
    PROCESS:
    1. Receive a UserProfile (as JSON or natural language description)
    2. Extract key search parameters:
       - disability_type
       - preferred_subcounty
       - service_category
       - backup_subcounty (if provided)
    3. Call the search_facilities_tool with these parameters
    4. Return the CandidateFacilities results
    
    GUIDELINES:
    - Always call search_facilities_tool to get actual data
    - If search returns no results, try broadening the location (use backup_subcounty)
    - Preserve all facility details in your response
    - Note the search_metadata for context
    - Be prepared to search again if user refines requirements
    
    OUTPUT:
    Return the full CandidateFacilities JSON object received from the search tool,
    possibly with a brief natural language summary at the top.
    """
    
    agent = LlmAgent(
        model=Gemini(model=model_name, retry_options=retry_config, temperature=temperature),
        name="search_agent",
        description="Searches and filters facilities based on user profile and accessibility needs",
        instruction=instruction,
        tools=[search_facilities_tool],
    )
    
    return agent
