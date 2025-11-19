"""
Agent Orchestrator for Accessible Services Navigator.

This module coordinates the multi-agent pipeline:
1. Intake Agent: Extract user needs → UserProfile
2. Search Agent: Find facilities → CandidateFacilities
3. Reasoning Agent: Score facilities → ScoredFacilities
4. Recommendation Agent: Generate recommendations → ServicePlan

The orchestrator manages data flow, error handling, and memory persistence.
"""

import time
from typing import Optional, Dict, Any

from .agents import (
    create_intake_agent,
    create_search_agent,
    create_reasoning_agent,
    create_recommendation_agent
)
from .memory import MemoryManager
from .utils import setup_logging, get_logger
from .models.schemas import (
    UserProfile,
    CandidateFacilities,
    ScoredFacilities,
    ServicePlan
)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent pipeline for service recommendations.
    
    This class coordinates the flow of data between four specialized agents,
    manages memory persistence, and handles errors gracefully.
    
    Attributes:
        intake_agent: Agent for extracting user needs
        search_agent: Agent for finding facilities
        reasoning_agent: Agent for scoring facilities
        recommendation_agent: Agent for generating recommendations
        memory_manager: Memory service for persistence
        logger: Structured logger instance
    """
    
    def __init__(
        self,
        log_level: str = "INFO",
        enable_logging: bool = True
    ):
        """
        Initialize the orchestrator with all agents and services.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable_logging: Whether to enable logging
        """
        # Set up logging
        if enable_logging:
            setup_logging(log_level=log_level)
        self.logger = get_logger(__name__)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager()
        
        # Create agents
        self.logger.info("Initializing agents")
        self.intake_agent = create_intake_agent()
        self.search_agent = create_search_agent()
        self.reasoning_agent = create_reasoning_agent()
        self.recommendation_agent = create_recommendation_agent()
        
        self.logger.info("Orchestrator initialized successfully")
    
    async def process_query(
        self,
        user_id: str,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the entire agent pipeline.
        
        Args:
            user_id: Unique identifier for the user
            query: User's natural language query
            session_id: Optional existing session ID (creates new if None)
            
        Returns:
            Dictionary containing:
            - recommendation_text: User-facing recommendation
            - service_plan: ServicePlan object
            - session_id: Session identifier
            - metadata: Processing metadata (timings, etc.)
        """
        # Create or use existing session
        if not session_id:
            session_id = self.memory_manager.create_session(user_id)
            self.logger.info("Created new session", session_id=session_id, user_id=user_id)
        
        # Add user query to conversation history
        self.memory_manager.add_to_conversation_history(
            session_id=session_id,
            role="user",
            content=query
        )
        
        metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "timings": {}
        }
        
        try:
            # Step 1: Intake Agent - Extract user needs
            self.logger.info("Step 1: Invoking Intake Agent", session_id=session_id)
            start_time = time.time()
            
            user_profile = await self._invoke_intake_agent(query, session_id)
            
            metadata["timings"]["intake_agent_ms"] = (time.time() - start_time) * 1000
            self.logger.info(
                "Intake Agent completed",
                session_id=session_id,
                duration_ms=metadata["timings"]["intake_agent_ms"],
                disability_type=user_profile.disability_type.value,
                subcounty=user_profile.preferred_subcounty
            )
            
            # Save profile to memory
            self.memory_manager.save_profile(user_id, session_id, user_profile)
            
            # Step 2: Search Agent - Find facilities
            self.logger.info("Step 2: Invoking Search Agent", session_id=session_id)
            start_time = time.time()
            
            candidates = await self._invoke_search_agent(user_profile, session_id)
            
            metadata["timings"]["search_agent_ms"] = (time.time() - start_time) * 1000
            self.logger.info(
                "Search Agent completed",
                session_id=session_id,
                duration_ms=metadata["timings"]["search_agent_ms"],
                candidate_count=candidates.count
            )
            
            # Check if any facilities found
            if candidates.count == 0:
                return self._handle_no_results(session_id, user_profile, metadata)
            
            # Step 3: Reasoning Agent - Score facilities
            self.logger.info("Step 3: Invoking Reasoning Agent", session_id=session_id)
            start_time = time.time()
            
            scored_facilities = await self._invoke_reasoning_agent(
                user_profile,
                candidates,
                session_id
            )
            
            metadata["timings"]["reasoning_agent_ms"] = (time.time() - start_time) * 1000
            self.logger.info(
                "Reasoning Agent completed",
                session_id=session_id,
                duration_ms=metadata["timings"]["reasoning_agent_ms"],
                scored_count=len(scored_facilities.scored_facilities)
            )
            
            # Step 4: Recommendation Agent - Generate user-facing output
            self.logger.info("Step 4: Invoking Recommendation Agent", session_id=session_id)
            start_time = time.time()
            
            result = await self._invoke_recommendation_agent(
                user_profile,
                scored_facilities,
                session_id
            )
            
            metadata["timings"]["recommendation_agent_ms"] = (time.time() - start_time) * 1000
            self.logger.info(
                "Recommendation Agent completed",
                session_id=session_id,
                duration_ms=metadata["timings"]["recommendation_agent_ms"]
            )
            
            # Save service plan to memory
            self.memory_manager.save_service_plan(
                user_id,
                session_id,
                result["service_plan"]
            )
            
            # Add assistant response to conversation history
            self.memory_manager.add_to_conversation_history(
                session_id=session_id,
                role="assistant",
                content=result["recommendation_text"]
            )
            
            # Calculate total time
            metadata["timings"]["total_ms"] = sum(metadata["timings"].values())
            
            self.logger.info(
                "Pipeline completed successfully",
                session_id=session_id,
                total_duration_ms=metadata["timings"]["total_ms"]
            )
            
            return {
                "recommendation_text": result["recommendation_text"],
                "service_plan": result["service_plan"],
                "session_id": session_id,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(
                "Pipeline error",
                session_id=session_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise
    
    async def _invoke_intake_agent(
        self,
        query: str,
        session_id: str
    ) -> UserProfile:
        """
        Invoke the Intake Agent to extract user needs.
        
        Args:
            query: User's natural language query
            session_id: Current session identifier
            
        Returns:
            UserProfile object with extracted information
        """
        # Call the intake agent
        response = await self.intake_agent.run(query)
        
        # Parse response into UserProfile
        # The agent is instructed to return JSON matching UserProfile schema
        try:
            import json
            profile_data = json.loads(response.text)
            return UserProfile(**profile_data)
        except Exception as e:
            self.logger.error(
                "Failed to parse intake agent response",
                session_id=session_id,
                error=str(e),
                response=response.text
            )
            raise ValueError(f"Intake agent returned invalid format: {e}")
    
    async def _invoke_search_agent(
        self,
        user_profile: UserProfile,
        session_id: str
    ) -> CandidateFacilities:
        """
        Invoke the Search Agent to find facilities.
        
        Args:
            user_profile: UserProfile from intake agent
            session_id: Current session identifier
            
        Returns:
            CandidateFacilities object with search results
        """
        # Prepare input for search agent
        profile_json = user_profile.model_dump_json()
        
        # Call the search agent
        response = await self.search_agent.run(profile_json)
        
        # Parse response into CandidateFacilities
        try:
            import json
            candidates_data = json.loads(response.text)
            return CandidateFacilities(**candidates_data)
        except Exception as e:
            self.logger.error(
                "Failed to parse search agent response",
                session_id=session_id,
                error=str(e),
                response=response.text
            )
            raise ValueError(f"Search agent returned invalid format: {e}")
    
    async def _invoke_reasoning_agent(
        self,
        user_profile: UserProfile,
        candidates: CandidateFacilities,
        session_id: str
    ) -> ScoredFacilities:
        """
        Invoke the Reasoning Agent to score facilities.
        
        Args:
            user_profile: UserProfile from intake agent
            candidates: CandidateFacilities from search agent
            session_id: Current session identifier
            
        Returns:
            ScoredFacilities object with scored and ranked facilities
        """
        # Prepare input for reasoning agent
        input_data = {
            "user_profile": user_profile.model_dump(),
            "candidates": candidates.model_dump()
        }
        
        import json
        input_json = json.dumps(input_data)
        
        # Call the reasoning agent
        response = await self.reasoning_agent.run(input_json)
        
        # Parse response into ScoredFacilities
        try:
            scored_data = json.loads(response.text)
            return ScoredFacilities(**scored_data)
        except Exception as e:
            self.logger.error(
                "Failed to parse reasoning agent response",
                session_id=session_id,
                error=str(e),
                response=response.text
            )
            raise ValueError(f"Reasoning agent returned invalid format: {e}")
    
    async def _invoke_recommendation_agent(
        self,
        user_profile: UserProfile,
        scored_facilities: ScoredFacilities,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Invoke the Recommendation Agent to generate user-facing output.
        
        Args:
            user_profile: UserProfile from intake agent
            scored_facilities: ScoredFacilities from reasoning agent
            session_id: Current session identifier
            
        Returns:
            Dictionary with recommendation_text and service_plan
        """
        # Prepare input for recommendation agent
        input_data = {
            "user_profile": user_profile.model_dump(),
            "scored_facilities": scored_facilities.model_dump()
        }
        
        import json
        input_json = json.dumps(input_data)
        
        # Call the recommendation agent
        response = await self.recommendation_agent.run(input_json)
        
        # Parse response
        # Expected format: markdown text followed by ServicePlan JSON
        try:
            response_text = response.text
            
            # Split on a delimiter or parse structured output
            # For now, assume agent returns: "RECOMMENDATION_TEXT\n---JSON---\n{json}"
            if "---JSON---" in response_text:
                parts = response_text.split("---JSON---")
                recommendation_text = parts[0].strip()
                service_plan_json = parts[1].strip()
                service_plan_data = json.loads(service_plan_json)
            else:
                # Fallback: treat entire response as recommendation text
                # and construct ServicePlan manually
                recommendation_text = response_text
                service_plan_data = {
                    "user_profile": user_profile.model_dump(),
                    "recommended_facilities": [
                        sf.model_dump() for sf in scored_facilities.scored_facilities[:3]
                    ],
                    "context_summary": scored_facilities.context_summary.model_dump()
                }
            
            service_plan = ServicePlan(**service_plan_data)
            
            return {
                "recommendation_text": recommendation_text,
                "service_plan": service_plan
            }
        except Exception as e:
            self.logger.error(
                "Failed to parse recommendation agent response",
                session_id=session_id,
                error=str(e),
                response=response.text
            )
            raise ValueError(f"Recommendation agent returned invalid format: {e}")
    
    def _handle_no_results(
        self,
        session_id: str,
        user_profile: UserProfile,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle case when no facilities are found.
        
        Args:
            session_id: Current session identifier
            user_profile: User's profile
            metadata: Processing metadata
            
        Returns:
            Response dictionary with helpful message
        """
        self.logger.warning(
            "No facilities found",
            session_id=session_id,
            disability_type=user_profile.disability_type.value,
            subcounty=user_profile.preferred_subcounty
        )
        
        no_results_message = f"""
I couldn't find any {user_profile.service_category.value} facilities in {user_profile.preferred_subcounty} 
that match your accessibility needs for {user_profile.disability_type.value} support.

Here are some suggestions:

1. **Try a nearby subcounty**: Consider expanding your search to neighboring areas like Westlands, Embakasi, or Starehe.

2. **Contact NCPWD**: The National Council for Persons with Disabilities (Upper Hill Office) can provide 
   updated information about accessible facilities: +254 20 273 9189

3. **Check with County Health**: Nairobi County Health Department may have information about recent 
   accessibility improvements: +254 20 272 1404

Would you like me to search in a different area or service type?
"""
        
        return {
            "recommendation_text": no_results_message.strip(),
            "service_plan": None,
            "session_id": session_id,
            "metadata": metadata
        }
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a session including profile and plan.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session summary, or None if session not found
        """
        session = self.memory_manager.get_session(session_id)
        
        if not session:
            return None
        
        user_id = session.get("metadata", {}).get("user_id")
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "profile": self.memory_manager.get_profile(user_id, session_id),
            "service_plan": self.memory_manager.get_service_plan(user_id, session_id),
            "conversation_history": self.memory_manager.get_conversation_history(session_id)
        }
