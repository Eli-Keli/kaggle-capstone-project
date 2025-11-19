"""
Evaluation Runner for Accessible Services Navigator.

This script runs test scenarios from test_scenarios.yaml and evaluates
the agent system's performance against success criteria.
"""

import asyncio
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import box

# Add parent directory to path to import src modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator import AgentOrchestrator
from src.models.schemas import DisabilityType, ServiceCategory


console = Console()


class EvaluationRunner:
    """
    Runs evaluation scenarios and checks success criteria.
    
    This class loads test scenarios, executes them through the orchestrator,
    and evaluates results against expected outcomes.
    """
    
    def __init__(self, scenarios_file: str = "test_scenarios.yaml"):
        """
        Initialize the evaluation runner.
        
        Args:
            scenarios_file: Path to YAML file with test scenarios
        """
        self.scenarios_file = Path(__file__).parent / scenarios_file
        self.orchestrator = AgentOrchestrator(log_level="WARNING", enable_logging=False)
        self.results: List[Dict[str, Any]] = []
    
    def load_scenarios(self) -> List[Dict[str, Any]]:
        """
        Load test scenarios from YAML file.
        
        Returns:
            List of scenario dictionaries
        """
        with open(self.scenarios_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data.get('scenarios', [])
    
    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test scenario.
        
        Args:
            scenario: Scenario dictionary from YAML
            
        Returns:
            Result dictionary with success/failure and details
        """
        scenario_id = scenario['id']
        query = scenario['query']
        expected = scenario['expected_outcomes']
        success_criteria = scenario['success_criteria']
        
        console.print(f"\n[cyan]Running: {scenario['name']}[/cyan]")
        console.print(f"[dim]Query: {query}[/dim]")
        
        try:
            # Run through orchestrator
            result = await self.orchestrator.process_query(
                user_id=f"eval_user_{scenario_id}",
                query=query
            )
            
            # Evaluate result
            checks = self._evaluate_result(result, expected, success_criteria)
            
            passed = all(check['passed'] for check in checks)
            
            return {
                'scenario_id': scenario_id,
                'name': scenario['name'],
                'passed': passed,
                'checks': checks,
                'recommendation': result['recommendation_text'],
                'metadata': result['metadata']
            }
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return {
                'scenario_id': scenario_id,
                'name': scenario['name'],
                'passed': False,
                'checks': [{'criterion': 'Execution', 'passed': False, 'details': str(e)}],
                'recommendation': None,
                'metadata': None
            }
    
    def _evaluate_result(
        self,
        result: Dict[str, Any],
        expected: Dict[str, Any],
        success_criteria: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate result against expected outcomes and success criteria.
        
        Args:
            result: Result from orchestrator
            expected: Expected outcomes from scenario
            success_criteria: List of success criteria to check
            
        Returns:
            List of check results
        """
        checks = []
        service_plan = result.get('service_plan')
        recommendation = result.get('recommendation_text', '').lower()
        
        # Check 1: Service plan exists
        checks.append({
            'criterion': 'Service plan generated',
            'passed': service_plan is not None,
            'details': 'Service plan created' if service_plan else 'No service plan'
        })
        
        if not service_plan:
            return checks
        
        # Check 2: Disability type matches
        profile = service_plan.user_profile
        expected_disability = expected.get('disability_type')
        if expected_disability:
            passed = profile.disability_type.value == expected_disability
            checks.append({
                'criterion': 'Disability type extracted',
                'passed': passed,
                'details': f"Expected: {expected_disability}, Got: {profile.disability_type.value}"
            })
        
        # Check 3: Location matches
        expected_subcounty = expected.get('preferred_subcounty')
        if expected_subcounty:
            passed = profile.preferred_subcounty and expected_subcounty.lower() in profile.preferred_subcounty.lower()
            checks.append({
                'criterion': 'Location extracted',
                'passed': passed,
                'details': f"Expected: {expected_subcounty}, Got: {profile.preferred_subcounty}"
            })
        
        # Check 4: Service category matches
        expected_category = expected.get('service_category')
        if expected_category:
            passed = profile.service_category.value == expected_category
            checks.append({
                'criterion': 'Service category extracted',
                'passed': passed,
                'details': f"Expected: {expected_category}, Got: {profile.service_category.value}"
            })
        
        # Check 5: Facilities recommended
        facilities = service_plan.recommended_facilities
        checks.append({
            'criterion': 'Facilities recommended',
            'passed': len(facilities) > 0,
            'details': f"{len(facilities)} facilities recommended"
        })
        
        # Check 6: Must-have features mentioned
        must_have_features = expected.get('must_have_features', [])
        for feature in must_have_features:
            feature_mentioned = feature.lower() in recommendation
            checks.append({
                'criterion': f'Feature mentioned: {feature}',
                'passed': feature_mentioned,
                'details': 'Mentioned' if feature_mentioned else 'Not mentioned'
            })
        
        # Check 7: Success criteria (text-based checks)
        for criterion in success_criteria:
            # Simple keyword check - in production, use more sophisticated NLP
            keywords = criterion.lower().split()
            passed = any(keyword in recommendation for keyword in keywords if len(keyword) > 3)
            checks.append({
                'criterion': criterion,
                'passed': passed,
                'details': 'Found' if passed else 'Not found'
            })
        
        return checks
    
    async def run_all_scenarios(self):
        """Run all scenarios and collect results."""
        scenarios = self.load_scenarios()
        
        console.print(f"\n[bold cyan]Running {len(scenarios)} evaluation scenarios...[/bold cyan]\n")
        
        for scenario in track(scenarios, description="Evaluating..."):
            result = await self.run_scenario(scenario)
            self.results.append(result)
            
            # Brief status
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            console.print(f"{status} - {result['name']}")
    
    def display_summary(self):
        """Display evaluation summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        console.print("\n" + "="*70)
        console.print(f"[bold cyan]Evaluation Summary[/bold cyan]")
        console.print("="*70 + "\n")
        
        # Summary stats
        summary_table = Table(box=box.SIMPLE)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white", justify="right")
        
        summary_table.add_row("Total Scenarios", str(total))
        summary_table.add_row("Passed", f"[green]{passed}[/green]")
        summary_table.add_row("Failed", f"[red]{failed}[/red]")
        summary_table.add_row("Success Rate", f"{(passed/total)*100:.1f}%")
        
        console.print(summary_table)
        console.print()
        
        # Detailed results
        if failed > 0:
            console.print("[bold red]Failed Scenarios:[/bold red]\n")
            
            for result in self.results:
                if not result['passed']:
                    console.print(f"[red]❌ {result['name']}[/red]")
                    
                    failed_checks = [c for c in result['checks'] if not c['passed']]
                    for check in failed_checks:
                        console.print(f"  - {check['criterion']}: {check['details']}")
                    console.print()
    
    def save_results(self, output_file: str = "evaluation_results.json"):
        """
        Save evaluation results to JSON file.
        
        Args:
            output_file: Path to output file
        """
        output_path = Path(__file__).parent / "results" / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        # Prepare results for JSON serialization
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'total_scenarios': len(self.results),
            'passed': sum(1 for r in self.results if r['passed']),
            'failed': sum(1 for r in self.results if not r['passed']),
            'scenarios': []
        }
        
        for result in self.results:
            scenario_data = {
                'id': result['scenario_id'],
                'name': result['name'],
                'passed': result['passed'],
                'checks': result['checks'],
                'metadata': result.get('metadata')
            }
            results_data['scenarios'].append(scenario_data)
        
        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        console.print(f"\n[green]✅ Results saved to: {output_path}[/green]")


async def main():
    """Main entry point for evaluation runner."""
    runner = EvaluationRunner()
    
    await runner.run_all_scenarios()
    runner.display_summary()
    runner.save_results()


if __name__ == "__main__":
    asyncio.run(main())
