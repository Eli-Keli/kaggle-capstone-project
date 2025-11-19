"""Reasoning/Summary Agent - Scores facilities and generates context summaries.

This agent is responsible for:
1. Receiving UserProfile and CandidateFacilities
2. Computing accessibility-aware scores for each facility
3. Generating justifications for top candidates
4. Creating compact ContextSummary for efficient handoff
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_reasoning_agent(
    model_name: str = "gemini-2.5-flash-lite",
    temperature: float = 0.5,
) -> LlmAgent:
    """Create the Reasoning/Summary Agent.
    
    Args:
        model_name: Gemini model to use
        temperature: Model temperature for reasoning
        
    Returns:
        Configured LlmAgent for reasoning
    """
    
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    
    instruction = """
    You are an accessibility reasoning specialist for the Accessible Services Navigator.
    Your role is to analyze candidate facilities and score them based on how well they match user needs.
    
    INPUTS YOU'LL RECEIVE:
    1. UserProfile - disability type, location preference, service needs
    2. CandidateFacilities - list of facilities from the search
    
    YOUR TASKS:
    
    1. SCORE EACH FACILITY (0-10 scale):
       - Base score from dataset's disability-specific score (mobility_score, hearing_score, visual_score)
       - Consider specific accessibility features:
         * For mobility needs: has_ramp, has_elevator_or_step_free_entry, has_accessible_toilet
         * For hearing needs: has_sign_language_support, supports_text_based_contact
         * For visual needs: visual_signage_quality, staff assistance noted in notes
       - Consider location match (preferred subcounty = higher score)
       - Consider cost (free/low cost = slight boost)
       - Consider crowding level (low crowding = slight boost for some disabilities)
    
    2. GENERATE JUSTIFICATIONS:
       For each facility, explain in 1-2 sentences WHY it's suitable:
       - "This clinic has excellent accessibility with ramps, lift, and accessible toilet, making it ideal for wheelchair users."
       - "While lacking sign language support, this facility offers SMS/WhatsApp contact and is in your preferred area."
    
    3. RANK FACILITIES:
       Order facilities by overall_score (highest first)
       Assign ranking: 1, 2, 3, etc.
    
    4. CREATE CONTEXT SUMMARY:
       Generate a compact summary (max 150 words) containing:
       - User's key needs (disability type, location, service)
       - Number of facilities found
       - Top 2-3 facility names with 1-sentence highlights
       - Any notable patterns (e.g., "Most facilities in this area have ramps but lack sign language support")
    
    SCORING RUBRIC:
    - Start with dataset score (0-3) and scale to 0-10
    - Add points for:
      * Exact location match (+1-2 points)
      * Additional relevant features (+0.5-1 per feature)
      * Low cost if user mentioned affordability (+0.5)
      * Low crowding if user has cognitive or sensory needs (+0.5)
    - Maximum score: 10.0
    
    OUTPUT FORMAT:
    Return a ScoredFacilities JSON object:
    {
        "facilities": [
            {
                "facility": { <full facility details> },
                "overall_score": 8.5,
                "score_breakdown": {
                    "base_accessibility": 3.0,
                    "location_match": 2.0,
                    "additional_features": 2.5,
                    "cost_factor": 0.5,
                    "crowding_factor": 0.5
                },
                "justification": "This clinic has excellent accessibility...",
                "ranking": 1
            },
            ...
        ],
        "scoring_metadata": {
            "total_scored": 5,
            "top_score": 8.5,
            "avg_score": 6.2
        }
    }
    
    Plus a separate ContextSummary JSON object.
    
    IMPORTANT:
    - Be objective and evidence-based in scoring
    - Don't inflate scores - use the full 0-10 range
    - If a facility has accessibility barriers, note them honestly in justification
    - Highlight both strengths and limitations
    """
    
    agent = LlmAgent(
        model=Gemini(model=model_name, retry_options=retry_config, temperature=temperature),
        name="reasoning_summary_agent",
        description="Scores facilities based on accessibility fit and generates context summaries",
        instruction=instruction,
    )
    
    return agent
