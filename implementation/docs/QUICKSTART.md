# 🚀 Quick Start Guide

Get the Accessible Services Navigator running locally!

**Note**: This project is 80% complete. Phase 1-4 are done (agents, tools, notebooks). Phase 5 (local testing) is next.

## Prerequisites

- Python 3.10+
- Google API Key ([Get one here](https://aistudio.google.com/app/api-keys))

## Installation

Navigate to implementation directory
```bash
cd "Capstone Project/implementation"
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

```bash
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Copy environment template

```bash
cp .env.template .env
```
Edit .env and add your API key
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

## Test the Dataset Tool

Test that datasets load correctly

```python
python -c "from src.tools import DatasetSearchTool; tool = DatasetSearchTool(); print(f'✅ Loaded {len(tool.all_facilities_df)} facilities')"
```

Expected output:
```
✅ Loaded 15 clinics and 10 social services
✅ Loaded 25 facilities
```

## Test an Agent

Test the intake agent

```python
from src.agents import create_intake_agent

agent = create_intake_agent()
print(f"✅ Agent created: {agent.name}")
```

Test the reasoning agent

```python
from src.agents import create_reasoning_agent
agent = create_reasoning_agent()
print(f"✅ Agent created: {agent.name}")
```

Test the recommendation agent

```python
from src.agents import create_recommendation_agent
agent = create_recommendation_agent()
print(f"✅ Agent created: {agent.name}")
```

Test the search agent

```python
from src.agents import create_search_agent
agent = create_search_agent()
print(f"✅ Agent created: {agent.name}")
```
## Run the Orchestrator
Run the full multi-agent system

```bash
python src/orchestrator.py
```

You will be prompted to enter user details. 

Example input:
```
Enter disability type (mobility, visual, hearing, cognitive): mobility
Enter preferred sub-county (e.g., Embakasi East): Embakasi East
Enter service category (clinic, social_service): clinic
```

Expected output:
```
🏆 Top Recommended Facilities:
1. Facility A - Score: 92.5
2. Facility B - Score: 88.0
3. Facility C - Score: 85.5
```

## Common Issues

### Import Errors
If you see "Import could not be resolved" warnings, install dependencies:
```bash
pip install -r requirements.txt
```

### API Key Issues
Make sure your `.env` file has:
```bash
GOOGLE_API_KEY=your_actual_key_here
```

### Dataset Not Found
Ensure you're running from the `implementation/` directory:
```bash
pwd  # Should end with .../implementation
```

## Project Structure

```
implementation/
├── src/               # Source code
│   ├── agents/        # ✅ Four agents
│   ├── tools/         # ✅ Custom tools
│   └── models/        # ✅ Data schemas
├── data/              # ✅ 25 facilities
├── config/            # ✅ Configuration
└── README.md          # Full documentation
```

## Resources

- **Full Documentation**: `README.md`
- **Progress Report**: `PROGRESS.md`
- **Configuration Guide**: `config/config.yaml`
- **Data Schema**: `src/models/schemas.py`

---

Happy navigating accessible services in Nairobi! 🚀
