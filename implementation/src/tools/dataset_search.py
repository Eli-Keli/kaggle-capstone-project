"""Dataset search tool for filtering and ranking Nairobi facilities.

This tool searches the curated dataset of facilities based on user requirements
such as location, service type, and accessibility features.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from src.models.schemas import (
    Facility,
    UserProfile,
    CandidateFacilities,
    ServiceCategory,
    DisabilityType,
)


class DatasetSearchTool:
    """Tool for searching and filtering facilities from the curated dataset."""

    def __init__(self, data_path: Optional[str] = None):
        """Initialize the dataset search tool.
        
        Args:
            data_path: Path to the data directory. Defaults to implementation/data/
        """
        if data_path is None:
            # Default to the data directory
            base_path = Path(__file__).parent.parent.parent / "data"
            data_path = str(base_path)
        
        self.data_path = Path(data_path)
        self.clinics_df: Optional[pd.DataFrame] = None
        self.social_services_df: Optional[pd.DataFrame] = None
        self.all_facilities_df: Optional[pd.DataFrame] = None
        
        self._load_datasets()

    def _load_datasets(self) -> None:
        """Load the CSV datasets into memory."""
        try:
            clinics_path = self.data_path / "nairobi_clinics.csv"
            social_services_path = self.data_path / "nairobi_social_services.csv"
            
            if clinics_path.exists():
                self.clinics_df = pd.read_csv(clinics_path)
            else:
                print(f"Warning: Clinics dataset not found at {clinics_path}")
                self.clinics_df = pd.DataFrame()
            
            if social_services_path.exists():
                self.social_services_df = pd.read_csv(social_services_path)
            else:
                print(f"Warning: Social services dataset not found at {social_services_path}")
                self.social_services_df = pd.DataFrame()
            
            # Combine datasets
            self.all_facilities_df = pd.concat(
                [self.clinics_df, self.social_services_df], 
                ignore_index=True
            )
            
            print(f"✅ Loaded {len(self.clinics_df)} clinics and {len(self.social_services_df)} social services")
            
        except Exception as e:
            print(f"❌ Error loading datasets: {e}")
            self.clinics_df = pd.DataFrame()
            self.social_services_df = pd.DataFrame()
            self.all_facilities_df = pd.DataFrame()

    def search_facilities(
        self,
        user_profile: UserProfile,
        max_results: int = 10,
    ) -> CandidateFacilities:
        """Search for facilities matching the user profile.
        
        Args:
            user_profile: The user's profile with preferences and needs
            max_results: Maximum number of facilities to return
            
        Returns:
            CandidateFacilities object with matching facilities
        """
        if self.all_facilities_df is None or self.all_facilities_df.empty:
            return CandidateFacilities(
                facilities=[],
                search_metadata={
                    "error": "No dataset loaded",
                    "total_facilities": 0,
                }
            )
        
        # Start with all facilities
        df = self.all_facilities_df.copy()
        
        # Filter by service category
        category_map = {
            ServiceCategory.CLINIC: "clinic",
            ServiceCategory.HOSPITAL: "hospital",
            ServiceCategory.NCPWD_OFFICE: "ncpwd_office",
            ServiceCategory.SOCIAL_SERVICE: "social_service",
        }
        category_value = category_map.get(user_profile.service_category)
        if category_value:
            df = df[df["category"] == category_value]
        
        # Filter by preferred subcounty (case-insensitive)
        primary_matches = df[
            df["subcounty"].str.lower() == user_profile.preferred_subcounty.lower()
        ]
        
        # If backup subcounty is provided, also get those matches
        backup_matches = pd.DataFrame()
        if user_profile.backup_subcounty:
            backup_matches = df[
                df["subcounty"].str.lower() == user_profile.backup_subcounty.lower()
            ]
        
        # Combine primary and backup matches
        location_matches = pd.concat([primary_matches, backup_matches]).drop_duplicates()
        
        # If no location matches, broaden search to all in category
        if location_matches.empty:
            location_matches = df
        
        # Score facilities based on disability type
        location_matches = self._score_facilities(location_matches, user_profile)
        
        # Sort by accessibility score (descending)
        location_matches = location_matches.sort_values(
            by="computed_accessibility_score", 
            ascending=False
        )
        
        # Limit results
        location_matches = location_matches.head(max_results)
        
        # Convert to Facility objects
        facilities = []
        for _, row in location_matches.iterrows():
            facility = self._row_to_facility(row)
            facilities.append(facility)
        
        # Prepare metadata
        search_metadata = {
            "total_in_dataset": len(self.all_facilities_df),
            "matched_category": len(df),
            "matched_location": len(location_matches),
            "returned_count": len(facilities),
            "search_criteria": {
                "service_category": user_profile.service_category.value,
                "preferred_subcounty": user_profile.preferred_subcounty,
                "disability_type": user_profile.disability_type.value,
            }
        }
        
        return CandidateFacilities(
            facilities=facilities,
            search_metadata=search_metadata
        )

    def _score_facilities(
        self, 
        df: pd.DataFrame, 
        user_profile: UserProfile
    ) -> pd.DataFrame:
        """Score facilities based on disability-specific accessibility.
        
        Args:
            df: DataFrame of facilities
            user_profile: User's profile with disability type
            
        Returns:
            DataFrame with computed_accessibility_score column
        """
        # Use existing scores from dataset
        disability_score_map = {
            DisabilityType.MOBILITY: "mobility_score",
            DisabilityType.HEARING: "hearing_score",
            DisabilityType.VISUAL: "visual_score",
            DisabilityType.COGNITIVE: "mobility_score",  # Use mobility as proxy
            DisabilityType.MIXED: "mobility_score",  # Use mobility as proxy
            DisabilityType.OTHER: "mobility_score",  # Use mobility as proxy
        }
        
        score_column = disability_score_map.get(
            user_profile.disability_type, 
            "mobility_score"
        )
        
        # Ensure the column exists and has numeric values
        if score_column in df.columns:
            df["computed_accessibility_score"] = pd.to_numeric(
                df[score_column], 
                errors="coerce"
            ).fillna(0)
        else:
            df["computed_accessibility_score"] = 0
        
        # Boost score for free/low cost if not specified otherwise
        if "approx_cost_level" in df.columns:
            cost_boost = df["approx_cost_level"].apply(
                lambda x: 0.5 if x in ["free", "low"] else 0
            )
            df["computed_accessibility_score"] = df["computed_accessibility_score"] + cost_boost
        
        return df

    def _row_to_facility(self, row: pd.Series) -> Facility:
        """Convert a DataFrame row to a Facility object.
        
        Args:
            row: A row from the facilities DataFrame
            
        Returns:
            Facility object
        """
        return Facility(
            facility_id=str(row.get("facility_id", "")),
            facility_name=str(row.get("facility_name", "")),
            category=ServiceCategory(row.get("category", "clinic")),
            subcounty=str(row.get("subcounty", "")),
            ward=str(row.get("ward", "")),
            neighbourhood_landmark=str(row.get("neighbourhood_landmark")) if pd.notna(row.get("neighbourhood_landmark")) else None,
            latitude=float(row.get("latitude")) if pd.notna(row.get("latitude")) else None,
            longitude=float(row.get("longitude")) if pd.notna(row.get("longitude")) else None,
            managing_agency=str(row.get("managing_agency")) if pd.notna(row.get("managing_agency")) else None,
            services_offered=str(row.get("services_offered")) if pd.notna(row.get("services_offered")) else None,
            has_ramp=bool(row.get("has_ramp", False)),
            has_elevator_or_step_free_entry=bool(row.get("has_elevator_or_step_free_entry", False)),
            has_accessible_toilet=bool(row.get("has_accessible_toilet", False)),
            has_sign_language_support=bool(row.get("has_sign_language_support", False)),
            supports_text_based_contact=bool(row.get("supports_text_based_contact", False)),
            visual_signage_quality=str(row.get("visual_signage_quality", "low")),
            crowding_level=str(row.get("crowding_level", "medium")),
            approx_cost_level=str(row.get("approx_cost_level", "low")),
            mobility_score=int(row.get("mobility_score", 0)),
            hearing_score=int(row.get("hearing_score", 0)),
            visual_score=int(row.get("visual_score", 0)),
            notes=str(row.get("notes")) if pd.notna(row.get("notes")) else None,
            data_source=str(row.get("data_source")) if pd.notna(row.get("data_source")) else None,
            last_verified_date=str(row.get("last_verified_date")) if pd.notna(row.get("last_verified_date")) else None,
        )

    def get_facility_by_id(self, facility_id: str) -> Optional[Facility]:
        """Get a specific facility by its ID.
        
        Args:
            facility_id: The facility's unique identifier
            
        Returns:
            Facility object if found, None otherwise
        """
        if self.all_facilities_df is None or self.all_facilities_df.empty:
            return None
        
        matches = self.all_facilities_df[
            self.all_facilities_df["facility_id"] == facility_id
        ]
        
        if matches.empty:
            return None
        
        return self._row_to_facility(matches.iloc[0])
