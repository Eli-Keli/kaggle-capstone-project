"""
Memory Manager for Accessible Services Navigator.

This module provides a high-level interface for managing user sessions,
profiles, and service plans using ADK's memory services.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime

from google.adk.memory import InMemorySessionService, InMemoryMemoryService

from ..models.schemas import UserProfile, ServicePlan


class MemoryManager:
    """
    Manages memory and session state for the agent system.
    
    This class wraps ADK's InMemorySessionService and InMemoryMemoryService
    to provide convenient methods for storing and retrieving user profiles
    and service plans.
    
    Attributes:
        session_service: ADK session service for managing conversation state
        memory_service: ADK memory service for long-term storage
    """
    
    def __init__(self):
        """Initialize the memory manager with ADK memory services."""
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        
    def create_session(self, user_id: str) -> str:
        """
        Create a new session for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            session_id: Unique identifier for the new session
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize session with metadata
        self.session_service.create_session(
            session_id=session_id,
            metadata={
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session metadata.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session metadata dictionary, or None if session doesn't exist
        """
        try:
            return self.session_service.get_session(session_id)
        except Exception:
            return None
    
    def save_profile(
        self,
        user_id: str,
        session_id: str,
        profile: UserProfile
    ) -> None:
        """
        Save user profile to both session and long-term memory.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Current session identifier
            profile: UserProfile object to store
        """
        # Convert Pydantic model to dict
        profile_dict = profile.model_dump()
        
        # Save to session (for current conversation)
        self.session_service.set_session_data(
            session_id=session_id,
            key="user_profile",
            value=profile_dict
        )
        
        # Save to long-term memory (for future sessions)
        self.memory_service.store(
            user_id=user_id,
            key="user_profile",
            value=profile_dict,
            metadata={
                "type": "user_profile",
                "session_id": session_id,
                "updated_at": datetime.now().isoformat()
            }
        )
    
    def get_profile(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[UserProfile]:
        """
        Retrieve user profile from session or long-term memory.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Optional session identifier to check first
            
        Returns:
            UserProfile object, or None if not found
        """
        profile_dict = None
        
        # Try session first (if provided)
        if session_id:
            try:
                profile_dict = self.session_service.get_session_data(
                    session_id=session_id,
                    key="user_profile"
                )
            except Exception:
                pass
        
        # Fall back to long-term memory
        if not profile_dict:
            try:
                profile_dict = self.memory_service.retrieve(
                    user_id=user_id,
                    key="user_profile"
                )
            except Exception:
                pass
        
        # Convert dict back to Pydantic model
        if profile_dict:
            return UserProfile(**profile_dict)
        
        return None
    
    def save_service_plan(
        self,
        user_id: str,
        session_id: str,
        service_plan: ServicePlan
    ) -> None:
        """
        Save service plan to both session and long-term memory.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Current session identifier
            service_plan: ServicePlan object to store
        """
        # Convert Pydantic model to dict
        plan_dict = service_plan.model_dump()
        
        # Save to session (for current conversation)
        self.session_service.set_session_data(
            session_id=session_id,
            key="service_plan",
            value=plan_dict
        )
        
        # Save to long-term memory (for history)
        # Use a timestamped key to keep multiple plans
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        memory_key = f"service_plan_{timestamp}"
        
        self.memory_service.store(
            user_id=user_id,
            key=memory_key,
            value=plan_dict,
            metadata={
                "type": "service_plan",
                "session_id": session_id,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def get_service_plan(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[ServicePlan]:
        """
        Retrieve the most recent service plan from session or memory.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Optional session identifier to check first
            
        Returns:
            ServicePlan object, or None if not found
        """
        plan_dict = None
        
        # Try session first (if provided)
        if session_id:
            try:
                plan_dict = self.session_service.get_session_data(
                    session_id=session_id,
                    key="service_plan"
                )
            except Exception:
                pass
        
        # Fall back to long-term memory (get most recent)
        if not plan_dict:
            try:
                # Get all service plans and find the most recent
                all_plans = self.memory_service.list_keys(
                    user_id=user_id,
                    key_prefix="service_plan_"
                )
                
                if all_plans:
                    # Sort by timestamp in key (descending)
                    latest_key = sorted(all_plans)[-1]
                    plan_dict = self.memory_service.retrieve(
                        user_id=user_id,
                        key=latest_key
                    )
            except Exception:
                pass
        
        # Convert dict back to Pydantic model
        if plan_dict:
            return ServicePlan(**plan_dict)
        
        return None
    
    def get_conversation_history(
        self,
        session_id: str
    ) -> list[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of conversation turns (messages)
        """
        try:
            return self.session_service.get_session_data(
                session_id=session_id,
                key="conversation_history"
            ) or []
        except Exception:
            return []
    
    def add_to_conversation_history(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            session_id: Session identifier
            role: Role of the speaker ("user" or "assistant")
            content: Message content
        """
        history = self.get_conversation_history(session_id)
        
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        self.session_service.set_session_data(
            session_id=session_id,
            key="conversation_history",
            value=history
        )
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear session data (but preserve long-term memory).
        
        Args:
            session_id: Session identifier to clear
        """
        try:
            self.session_service.delete_session(session_id)
        except Exception:
            pass
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get user's service plan history from long-term memory.
        
        Args:
            user_id: Unique identifier for the user
            limit: Maximum number of plans to return
            
        Returns:
            List of service plan dictionaries (most recent first)
        """
        try:
            all_plan_keys = self.memory_service.list_keys(
                user_id=user_id,
                key_prefix="service_plan_"
            )
            
            # Sort by timestamp (descending) and limit
            sorted_keys = sorted(all_plan_keys, reverse=True)[:limit]
            
            plans = []
            for key in sorted_keys:
                plan_dict = self.memory_service.retrieve(
                    user_id=user_id,
                    key=key
                )
                if plan_dict:
                    plans.append(plan_dict)
            
            return plans
        except Exception:
            return []
