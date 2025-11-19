# 🚀 Quick Start Guide

Get the Accessible Services Navigator running in 5 minutes!

## Prerequisites

- Python 3.10+
- Google API Key ([Get one here](https://aistudio.google.com/app/api-keys))

## Installation

```bash
# Navigate to implementation directory
cd "Capstone Project/implementation"

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

## Test the Dataset Tool

```python
# Test that datasets load correctly
python -c "from src.tools import DatasetSearchTool; tool = DatasetSearchTool(); print(f'✅ Loaded {len(tool.all_facilities_df)} facilities')"
```

Expected output:
```
✅ Loaded 15 clinics and 10 social services
✅ Loaded 25 facilities
```

## Test an Agent

```python
# Test the intake agent
from src.agents import create_intake_agent

agent = create_intake_agent()
print(f"✅ Agent created: {agent.name}")
```

## Next Steps

1. **Complete the orchestrator** - See `PROGRESS.md` for next implementation tasks
2. **Build the demo CLI** - Interactive testing interface
3. **Create evaluation scenarios** - Test the full pipeline
4. **Develop notebooks** - Educational content for Kaggle

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

Ready to build? Start with the orchestrator! 🚀
