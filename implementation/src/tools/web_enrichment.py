"""Web enrichment tool for fetching additional facility information.

This tool wraps ADK's google_search to fetch short descriptions or recent
information about facilities. It's optional and configurable for deterministic testing.
"""

import os
from typing import List, Dict, Any, Optional

from src.models.schemas import Facility


class WebEnrichmentTool:
    """Tool for enriching facility data with web search results."""

    def __init__(self, enabled: bool = None):
        """Initialize the web enrichment tool.
        
        Args:
            enabled: Whether web enrichment is enabled. If None, reads from environment.
        """
        if enabled is None:
            # Read from environment variable
            enabled = os.getenv("ENABLE_WEB_ENRICHMENT", "false").lower() == "true"
        
        self.enabled = enabled
        
        if not self.enabled:
            print("ℹ️  Web enrichment is disabled (deterministic mode)")

    def enrich_facilities(
        self,
        facilities: List[Facility],
        max_facilities: int = 3,
    ) -> List[Facility]:
        """Enrich facilities with web search snippets.
        
        Args:
            facilities: List of facilities to enrich
            max_facilities: Maximum number of facilities to enrich
            
        Returns:
            List of facilities with web_snippet field populated
        """
        if not self.enabled:
            # Return facilities unchanged
            return facilities
        
        # Limit to max_facilities
        facilities_to_enrich = facilities[:max_facilities]
        
        enriched = []
        for facility in facilities_to_enrich:
            try:
                snippet = self._fetch_snippet(facility)
                facility.web_snippet = snippet
            except Exception as e:
                print(f"Warning: Failed to enrich {facility.facility_name}: {e}")
                facility.web_snippet = None
            
            enriched.append(facility)
        
        # Add remaining facilities without enrichment
        enriched.extend(facilities[max_facilities:])
        
        return enriched

    def _fetch_snippet(self, facility: Facility) -> Optional[str]:
        """Fetch a short web snippet for a facility.
        
        Args:
            facility: The facility to search for
            
        Returns:
            Short description snippet or None
        """
        # Construct search query
        query = f"{facility.facility_name} {facility.subcounty} Nairobi"
        
        # TODO: Implement actual web search using ADK's google_search
        # For now, return a placeholder
        # This would be implemented when ADK is available:
        # from google.adk.tools import google_search
        # results = google_search(query, num_results=1)
        # return results[0]['snippet'] if results else None
        
        # Placeholder implementation
        return f"Information about {facility.facility_name} in {facility.subcounty}"

    def search_facility_info(
        self,
        facility_name: str,
        location: str,
        num_results: int = 1
    ) -> List[Dict[str, str]]:
        """Search for general information about a facility.
        
        Args:
            facility_name: Name of the facility
            location: Location (subcounty or ward)
            num_results: Number of search results to return
            
        Returns:
            List of search result dictionaries with 'title', 'snippet', 'url'
        """
        if not self.enabled:
            return []
        
        query = f"{facility_name} {location} Nairobi Kenya"
        
        # TODO: Implement with ADK google_search when available
        # Placeholder for now
        return [
            {
                "title": f"Results for {facility_name}",
                "snippet": f"Information about {facility_name} in {location}",
                "url": "https://example.com"
            }
        ]
