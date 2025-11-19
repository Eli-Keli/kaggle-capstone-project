# Accessible Services Navigator (Nairobi)

> A multi-agent ADK system that helps persons with disabilities in Nairobi find accessible clinics and social services.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4)](https://google.github.io/adk-docs/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Development](#development)
- [Evaluation](#evaluation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The **Accessible Services Navigator** is a capstone project demonstrating practical multi-agent design using Google's Agent Development Kit (ADK). It addresses a real-world problem: helping persons with disabilities (PWDs) in Nairobi find healthcare and social services that match their accessibility needs.

### Problem Statement

PWDs in Nairobi face:
- **Fragmented information** across multiple sources
- **Accessibility uncertainty** - listings rarely specify ramps, lifts, or sign-language support
- **Bureaucratic navigation challenges** with inconsistent requirements
- **High cognitive burden** of cross-checking multiple sources

### Solution

A focused, **Nairobi-only MVP** that:
- Unifies curated facility data with accessibility annotations
- Uses multi-agent orchestration for intelligent search and reasoning
- Provides clear, actionable recommendations
- Remembers user preferences across sessions

## ✨ Features

### Multi-Agent System
- **Intake/Profile Agent**: Extracts user needs from natural language
- **Search Agent**: Filters facilities by location, service type, and accessibility
- **Reasoning/Summary Agent**: Scores facilities with accessibility-aware logic
- **Recommendation Agent**: Generates user-facing recommendations

### Custom Tools
- **DatasetSearchTool**: Filters 25+ Nairobi facilities with accessibility metadata
- **WebEnrichmentTool**: Optional web search for additional context

### Memory & Context Management
- Session-based conversation memory
- Long-term user profile and preference storage
- Context compaction for efficient agent handoffs

### Observability & Evaluation
- ADK logging plugins for tool calls and agent traces
- 10+ Nairobi-specific test scenarios
- Failure analysis framework

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────┐
│ Intake/Profile      │ → Extract disability type, location, service needs
│ Agent               │ → Store to UserProfile
└─────────────────────┘
    ↓ UserProfile
┌─────────────────────┐
│ Search Agent        │ → Call DatasetSearchTool
│                     │ → Optional WebEnrichmentTool
└─────────────────────┘ → Return CandidateFacilities
    ↓ CandidateFacilities
┌─────────────────────┐
│ Reasoning/Summary   │ → Score each facility
│ Agent               │ → Generate justifications
└─────────────────────┘ → Create ContextSummary
    ↓ ScoredFacilities + ContextSummary
┌─────────────────────┐
│ Recommendation      │ → Generate user-facing text
│ Agent               │ → Save ServicePlan to memory
└─────────────────────┘
    ↓
Final Recommendation
```

### Key Design Patterns

- **Multi-agent orchestration** with clear handoffs
- **Structured data schemas** using Pydantic
- **Context compaction** to maintain small token budgets
- **Tool-based architecture** for modularity
- **Memory layers** for session and long-term storage

## 📁 Project Structure

```
implementation/
├── src/
│   ├── agents/              # Four core agents
│   │   ├── intake_agent.py
│   │   ├── search_agent.py
│   │   ├── reasoning_agent.py
│   │   └── recommendation_agent.py
│   ├── tools/               # Custom tools
│   │   ├── dataset_search.py
│   │   └── web_enrichment.py
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   ├── memory/              # Memory management
│   │   └── memory_manager.py
│   ├── utils/               # Utilities
│   │   └── logging_config.py
│   ├── orchestrator.py      # Agent orchestration
│   └── demo.py              # Interactive CLI demo
├── data/                    # Curated datasets
│   ├── nairobi_clinics.csv
│   └── nairobi_social_services.csv
├── tests/                   # Test scenarios
│   └── evaluation/
│       ├── test_scenarios.yaml
│       └── run_evaluation.py
├── notebooks/               # Educational Kaggle notebooks
│   ├── 01_dataset_creation.ipynb
│   ├── 02_agent_development.ipynb
│   ├── 03_full_system_demo.ipynb
│   └── 04_evaluation_analysis.ipynb
├── config/                  # Configuration
│   └── config.yaml
├── logs/                    # Agent traces
├── docs/                    # Documentation
├── requirements.txt
├── .env.template
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Google API Key (for Gemini models)
- Optional: Google Cloud Project (for deployment)

### Installation

1. **Clone the repository**

```bash
cd "Capstone Project/implementation"
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

### Configuration

Edit `.env` file:

```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id  # Optional, for deployment
GOOGLE_GENAI_USE_VERTEXAI=0           # 0 for AI Studio, 1 for Vertex AI
ENABLE_WEB_ENRICHMENT=false           # Set to true for web search
```

## 💻 Usage

### Interactive CLI Demo

Run the interactive demo to test the system locally:

```bash
python src/demo.py
```

Example interaction:

```
👤 You: I use a wheelchair and live in Embakasi. I need an affordable clinic for check-ups.

🤖 Assistant: I found several accessible clinics in Embakasi East that work well for wheelchair users...

**1. Embakasi Health Centre** (Embakasi East, Embakasi Central)
- 📍 Near Donholm Market
- ♿ Accessibility: Ramp available, accessible toilet
- 🏥 Services: General consultation, immunization, family planning
- 💰 Free (County facility)
...
```

### Python API Usage

```python
from src.agents import (
    create_intake_agent,
    create_search_agent,
    create_reasoning_agent,
    create_recommendation_agent
)

# Create agents
intake_agent = create_intake_agent()
search_agent = create_search_agent()
reasoning_agent = create_reasoning_agent()
recommendation_agent = create_recommendation_agent()

# Use orchestrator
from src.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(
    intake_agent=intake_agent,
    search_agent=search_agent,
    reasoning_agent=reasoning_agent,
    recommendation_agent=recommendation_agent,
)

# Process user query
result = await orchestrator.process_query(
    user_id="user_123",
    query="I need an accessible clinic in Westlands"
)
```

### Dataset Search Tool (Standalone)

```python
from src.tools import DatasetSearchTool
from src.models import UserProfile, DisabilityType, ServiceCategory

tool = DatasetSearchTool()

profile = UserProfile(
    disability_type=DisabilityType.MOBILITY,
    preferred_subcounty="Embakasi East",
    service_category=ServiceCategory.CLINIC,
)

candidates = tool.search_facilities(profile, max_results=5)
print(f"Found {candidates.count} facilities")
```

## 🛠️ Development

### Running Tests

```bash
# Run evaluation scenarios
python tests/evaluation/run_evaluation.py

# Run with detailed output
python tests/evaluation/run_evaluation.py --verbose

# Run specific scenario
python tests/evaluation/run_evaluation.py --scenario wheelchair_embakasi
```

### Adding New Facilities

1. Edit `data/nairobi_clinics.csv` or `data/nairobi_social_services.csv`
2. Follow the schema in `src/models/schemas.py`
3. Ensure all required fields are populated
4. Verify data with:

```python
from src.tools import DatasetSearchTool
tool = DatasetSearchTool()
print(f"Loaded {len(tool.all_facilities_df)} facilities")
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
```

## 📊 Evaluation

### Test Scenarios

10 Nairobi-specific scenarios covering:
- Different disability types (mobility, hearing, visual)
- Various subcounties (Embakasi, Westlands, Langata, etc.)
- Different service needs (clinics, NCPWD offices, social services)
- Cost sensitivities and special requirements

### Success Criteria

For each scenario:
- ✅ Service relevance (correct location/service type)
- ✅ Accessibility alignment (relevant features mentioned)
- ✅ Data consistency (no contradictions)
- ✅ Clarity and brevity (understandable, concise)
- ✅ Tool usage (appropriate tool calls)

### Running Evaluation

```bash
cd tests/evaluation
python run_evaluation.py
```

Results saved to `tests/evaluation/results/`

## 🚀 Deployment

### Local Testing

Already covered in [Usage](#usage) section.

### Deploy to Vertex AI Agent Engine

1. **Prepare deployment configuration**

```bash
# Already created: .agent_engine_config.json
```

2. **Set Google Cloud credentials**

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Deploy using ADK CLI**

```bash
adk deploy agent_engine \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  src/ \
  --agent_engine_config_file=.agent_engine_config.json
```

4. **Test deployed agent**

See `notebooks/03_full_system_demo.ipynb` for examples.

### Cost Management

- Agent Engine offers a **monthly free tier**
- Delete agents when not in use to avoid charges
- Monitor usage in [Google Cloud Console](https://console.cloud.google.com/vertex-ai/agents)

```bash
# Delete deployed agent
adk delete agent_engine --resource-name=RESOURCE_NAME
```

## 📚 Educational Notebooks

Four Jupyter notebooks for Kaggle:

1. **01_dataset_creation.ipynb**: Data curation process and schema design
2. **02_agent_development.ipynb**: Step-by-step agent creation
3. **03_full_system_demo.ipynb**: End-to-end workflow demo
4. **04_evaluation_analysis.ipynb**: Test results and failure analysis

Located in `notebooks/` directory.

## 🤝 Contributing

This is a capstone project for educational purposes. However, suggestions and improvements are welcome!

### Areas for Contribution

- Additional Nairobi facilities with verified accessibility data
- More test scenarios
- Improved scoring algorithms
- Better web enrichment integration
- Swahili language support
- Mobile app interface

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK Team** for the Agent Development Kit
- **Kaggle** for hosting the 5-Day AI Agents course
- **NCPWD (National Council for Persons with Disabilities)** for accessibility advocacy
- **Nairobi County Government** for public health facility information

## 📞 Contact

For questions about this project:
- Open an issue on GitHub
- Join the [Kaggle Discord](https://discord.com/invite/kaggle)

---

**Built with ❤️ for an inclusive Nairobi**

*Part of the Kaggle 5-Day AI Agents Intensive Course Capstone Project*
