"""
Interactive CLI Demo for Accessible Services Navigator.

This module provides a Rich terminal interface for testing the agent system
locally. Users can have multi-turn conversations and see memory in action.
"""

import asyncio
import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from .orchestrator import AgentOrchestrator
from .models.schemas import ServicePlan


console = Console()


class InteractiveCLI:
    """
    Interactive command-line interface for the agent system.
    
    This class provides a conversational interface with:
    - Rich text formatting
    - Multi-turn conversations
    - Memory demonstration
    - Error handling
    """
    
    def __init__(self):
        """Initialize the CLI with orchestrator."""
        self.orchestrator = AgentOrchestrator(log_level="INFO", enable_logging=True)
        self.current_session_id: Optional[str] = None
        self.current_user_id: Optional[str] = None
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        welcome_text = """
# 🏥 Accessible Services Navigator (Nairobi)

Welcome! I help persons with disabilities find accessible healthcare and social services in Nairobi.

**How it works:**
1. Tell me about your accessibility needs and what service you're looking for
2. I'll search our curated database of facilities
3. You'll get personalized recommendations with accessibility details

**Example queries:**
- "I use a wheelchair and need an affordable clinic in Embakasi"
- "I'm deaf and need to visit the NCPWD office in CBD"
- "I'm looking for accessible social services in Westlands for my elderly parent who has mobility issues"

**Commands:**
- Type your query to start
- Type `history` to see your service plan history
- Type `session` to view current session info
- Type `help` for more information
- Type `quit` or `exit` to end
        """
        
        console.print(Panel(Markdown(welcome_text), border_style="green"))
    
    def display_help(self):
        """Display help information."""
        help_text = """
# Help

**Available Commands:**
- `history` - View your service plan history
- `session` - View current session information
- `help` - Display this help message
- `quit` or `exit` - Exit the application

**Query Examples:**
- Wheelchair user seeking clinic in Embakasi East
- Deaf person needing NCPWD office with sign language support
- Blind person looking for accessible health center in Westlands
- Parent seeking child-friendly accessible clinic in Langata

**Nairobi Subcounties Covered:**
Embakasi East, Embakasi West, Westlands, Kibra, Langata, Starehe (CBD), 
Kasarani, Roysambu, Makadara, Dagoretti North

**Service Types:**
- Clinics and hospitals
- NCPWD offices
- Social services and protection offices
        """
        
        console.print(Panel(Markdown(help_text), border_style="blue"))
    
    async def run(self):
        """Run the interactive CLI loop."""
        self.display_welcome()
        
        # Get user ID (in real app, this would be authentication)
        self.current_user_id = Prompt.ask(
            "\n[bold cyan]Enter your user ID[/bold cyan]",
            default="demo_user"
        )
        
        console.print(f"\n✅ Logged in as: [bold]{self.current_user_id}[/bold]\n")
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if not user_input.strip():
                    continue
                
                # Handle commands
                command = user_input.strip().lower()
                
                if command in ["quit", "exit"]:
                    console.print("\n👋 [yellow]Thank you for using Accessible Services Navigator![/yellow]")
                    break
                
                elif command == "help":
                    self.display_help()
                    continue
                
                elif command == "history":
                    self.display_history()
                    continue
                
                elif command == "session":
                    self.display_session_info()
                    continue
                
                # Process query through agent pipeline
                console.print("\n[dim]🤖 Processing your query...[/dim]")
                
                result = await self.orchestrator.process_query(
                    user_id=self.current_user_id,
                    query=user_input,
                    session_id=self.current_session_id
                )
                
                # Update session ID
                self.current_session_id = result["session_id"]
                
                # Display recommendation
                self.display_recommendation(
                    result["recommendation_text"],
                    result["service_plan"],
                    result["metadata"]
                )
                
            except KeyboardInterrupt:
                console.print("\n\n👋 [yellow]Goodbye![/yellow]")
                break
            
            except Exception as e:
                console.print(f"\n[red]❌ Error: {str(e)}[/red]")
                console.print("[dim]Please try rephrasing your query or type 'help' for guidance.[/dim]")
    
    def display_recommendation(
        self,
        recommendation_text: str,
        service_plan: Optional[ServicePlan],
        metadata: dict
    ):
        """
        Display the recommendation with formatting.
        
        Args:
            recommendation_text: User-facing recommendation text
            service_plan: ServicePlan object (if available)
            metadata: Processing metadata
        """
        # Display main recommendation
        console.print("\n[bold cyan]🤖 Assistant:[/bold cyan]")
        console.print(Panel(
            Markdown(recommendation_text),
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Display timing information (debug mode)
        if os.getenv("DEBUG") == "true":
            timing_table = Table(title="⏱️ Processing Times", box=box.SIMPLE)
            timing_table.add_column("Stage", style="cyan")
            timing_table.add_column("Duration (ms)", style="green", justify="right")
            
            for stage, duration in metadata.get("timings", {}).items():
                timing_table.add_row(
                    stage.replace("_", " ").title(),
                    f"{duration:.2f}"
                )
            
            console.print("\n", timing_table)
    
    def display_history(self):
        """Display user's service plan history."""
        if not self.current_user_id:
            console.print("[yellow]No active user session[/yellow]")
            return
        
        history = self.orchestrator.memory_manager.get_user_history(
            self.current_user_id,
            limit=5
        )
        
        if not history:
            console.print("\n[yellow]No service plan history found[/yellow]")
            return
        
        console.print("\n[bold cyan]📋 Your Service Plan History[/bold cyan]\n")
        
        for i, plan_data in enumerate(history, 1):
            profile = plan_data.get("user_profile", {})
            facilities = plan_data.get("recommended_facilities", [])
            
            console.print(f"[bold]{i}. Plan from {plan_data.get('context_summary', {}).get('created_at', 'N/A')}[/bold]")
            console.print(f"   Disability Type: {profile.get('disability_type')}")
            console.print(f"   Location: {profile.get('preferred_subcounty')}")
            console.print(f"   Facilities Recommended: {len(facilities)}")
            console.print()
    
    def display_session_info(self):
        """Display current session information."""
        if not self.current_session_id:
            console.print("\n[yellow]No active session[/yellow]")
            return
        
        summary = self.orchestrator.get_session_summary(self.current_session_id)
        
        if not summary:
            console.print("\n[yellow]Session not found[/yellow]")
            return
        
        console.print("\n[bold cyan]📊 Current Session Info[/bold cyan]\n")
        
        # Session details
        info_table = Table(box=box.SIMPLE)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Session ID", summary["session_id"])
        info_table.add_row("User ID", summary["user_id"])
        
        if summary.get("profile"):
            profile = summary["profile"]
            info_table.add_row("Disability Type", profile.disability_type.value)
            info_table.add_row("Location", profile.preferred_subcounty or "N/A")
            info_table.add_row("Service Type", profile.service_category.value)
        
        console.print(info_table)
        
        # Conversation history
        history = summary.get("conversation_history", [])
        if history:
            console.print(f"\n[bold]Conversation Turns:[/bold] {len(history)}")


def main():
    """Main entry point for the CLI demo."""
    cli = InteractiveCLI()
    
    try:
        asyncio.run(cli.run())
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    main()
