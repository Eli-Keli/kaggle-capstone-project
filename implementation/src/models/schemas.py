"""Pydantic schemas for the Accessible Services Navigator.

These schemas define the data structures passed between agents in the multi-agent pipeline.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class DisabilityType(str, Enum):
    """Types of disabilities supported by the system."""
    MOBILITY = "mobility"
    HEARING = "hearing"
    VISUAL = "visual"
    COGNITIVE = "cognitive"
    MIXED = "mixed"
    OTHER = "other"


class ServiceCategory(str, Enum):
    """Categories of services available."""
    CLINIC = "clinic"
    HOSPITAL = "hospital"
    NCPWD_OFFICE = "ncpwd_office"
    SOCIAL_SERVICE = "social_service"


class CostLevel(str, Enum):
    """Cost levels for services."""
    FREE = "free"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class SignageQuality(str, Enum):
    """Quality levels for visual signage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CrowdingLevel(str, Enum):
    """Crowding levels at facilities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserProfile(BaseModel):
    """User profile extracted from intake conversation."""
    
    disability_type: DisabilityType = Field(
        ..., 
        description="Primary disability type"
    )
    mobility_needs: Optional[str] = Field(
        None, 
        description="Specific mobility requirements (e.g., wheelchair, walker)"
    )
    communication_needs: Optional[str] = Field(
        None, 
        description="Communication preferences (e.g., sign language, SMS)"
    )
    preferred_subcounty: str = Field(
        ..., 
        description="Preferred subcounty in Nairobi (e.g., Embakasi East, Westlands)"
    )
    backup_subcounty: Optional[str] = Field(
        None, 
        description="Alternative subcounty if preferred is not available"
    )
    service_category: ServiceCategory = Field(
        ..., 
        description="Type of service needed"
    )
    additional_requirements: Optional[str] = Field(
        None, 
        description="Any other specific requirements or preferences"
    )
    language_preference: str = Field(
        default="English", 
        description="Preferred language for communication"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "disability_type": "mobility",
                "mobility_needs": "wheelchair user",
                "communication_needs": None,
                "preferred_subcounty": "Embakasi East",
                "backup_subcounty": "Embakasi West",
                "service_category": "clinic",
                "additional_requirements": "affordable, regular check-ups",
                "language_preference": "English"
            }
        }


class Facility(BaseModel):
    """Represents a healthcare or social service facility in Nairobi."""
    
    facility_id: str = Field(..., description="Unique facility identifier")
    facility_name: str = Field(..., description="Name of the facility")
    category: ServiceCategory = Field(..., description="Type of facility")
    subcounty: str = Field(..., description="Subcounty location")
    ward: str = Field(..., description="Ward location")
    neighbourhood_landmark: Optional[str] = Field(
        None, 
        description="Nearby landmark for easier location"
    )
    latitude: Optional[float] = Field(None, description="Geographic latitude")
    longitude: Optional[float] = Field(None, description="Geographic longitude")
    managing_agency: Optional[str] = Field(
        None, 
        description="Organization managing the facility"
    )
    services_offered: Optional[str] = Field(
        None, 
        description="List of services available"
    )
    
    # Accessibility features
    has_ramp: bool = Field(False, description="Has wheelchair ramp")
    has_elevator_or_step_free_entry: bool = Field(
        False, 
        description="Has elevator or step-free entry"
    )
    has_accessible_toilet: bool = Field(False, description="Has accessible toilet")
    has_sign_language_support: bool = Field(
        False, 
        description="Provides sign language interpretation"
    )
    supports_text_based_contact: bool = Field(
        False, 
        description="Supports SMS/WhatsApp communication"
    )
    visual_signage_quality: SignageQuality = Field(
        SignageQuality.LOW, 
        description="Quality of visual signage"
    )
    crowding_level: CrowdingLevel = Field(
        CrowdingLevel.MEDIUM, 
        description="Typical crowding level"
    )
    approx_cost_level: CostLevel = Field(
        CostLevel.LOW, 
        description="Approximate cost level"
    )
    
    # Accessibility scores (0-3, where 3 is best)
    mobility_score: int = Field(
        0, 
        ge=0, 
        le=3, 
        description="Mobility accessibility score"
    )
    hearing_score: int = Field(
        0, 
        ge=0, 
        le=3, 
        description="Hearing accessibility score"
    )
    visual_score: int = Field(
        0, 
        ge=0, 
        le=3, 
        description="Visual accessibility score"
    )
    
    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes")
    data_source: Optional[str] = Field(
        None, 
        description="Source of the data"
    )
    last_verified_date: Optional[str] = Field(
        None, 
        description="Date when data was last verified"
    )
    
    # Optional web enrichment
    web_snippet: Optional[str] = Field(
        None, 
        description="Short description from web search"
    )


class CandidateFacilities(BaseModel):
    """List of candidate facilities from search."""
    
    facilities: List[Facility] = Field(
        default_factory=list, 
        description="List of candidate facilities"
    )
    search_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadata about the search process"
    )
    
    @property
    def count(self) -> int:
        """Return number of facilities."""
        return len(self.facilities)


class ScoredFacility(BaseModel):
    """A facility with computed accessibility score."""
    
    facility: Facility = Field(..., description="The facility details")
    overall_score: float = Field(
        ..., 
        ge=0.0, 
        le=10.0, 
        description="Overall accessibility score"
    )
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict, 
        description="Detailed scoring breakdown"
    )
    justification: str = Field(
        ..., 
        description="Why this facility is suitable"
    )
    ranking: int = Field(..., ge=1, description="Ranking among candidates")


class ScoredFacilities(BaseModel):
    """List of scored and ranked facilities."""
    
    facilities: List[ScoredFacility] = Field(
        default_factory=list, 
        description="List of scored facilities"
    )
    scoring_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadata about scoring process"
    )
    
    @property
    def top_facilities(self) -> List[ScoredFacility]:
        """Return top 3 facilities."""
        return sorted(self.facilities, key=lambda x: x.overall_score, reverse=True)[:3]


class ContextSummary(BaseModel):
    """Compact summary of context for efficient agent handoff."""
    
    user_summary: str = Field(
        ..., 
        description="Compact summary of user profile and needs"
    )
    search_summary: str = Field(
        ..., 
        description="Summary of search results"
    )
    reasoning_summary: str = Field(
        ..., 
        description="Summary of reasoning and scoring"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, 
        description="Timestamp of summary creation"
    )


class ServicePlan(BaseModel):
    """Service plan stored in memory for future reference."""
    
    user_profile: UserProfile = Field(..., description="User profile")
    recommended_facilities: List[ScoredFacility] = Field(
        default_factory=list, 
        description="Recommended facilities"
    )
    context_summary: Optional[ContextSummary] = Field(
        None, 
        description="Context summary"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, 
        description="When the plan was created"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Session identifier"
    )
