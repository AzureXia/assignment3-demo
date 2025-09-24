# Clinical Depression & Anxiety Knowledge Base Pipeline

## 🎯 INTERACTIVE DEMO AVAILABLE

### 🚀 Quick Demo (Recommended)
**One-command setup and launch:**
```bash
./quick_demo_setup.sh
```
- **30 seconds**: Auto-setup environment and requirements
- **2-5 minutes**: Optional sample data generation
- **Instant launch**: Choose your demo mode

### 🎛️ Manual Demo Launch
**Standard demo launcher:**
```bash
./run_demo.sh
```
Choose from:
1. **Visualization Dashboard** - Charts, insights, and command builder
2. **Interactive Runner** - Live pipeline execution with custom parameters  
3. **Unified Demo** - Single interface with both modes (recommended)

---

**Rename this folder** to `assignment3/<firstname_lastname>/` (lowercase with underscores) and submit on your personal branch.
All prompting uses the **Amplify API (4o-mini)**. Retrieval uses PubMed (Entrez).

This pipeline is **optimized for clinical depression and anxiety research**, with carefully designed prompts containing few-shot examples and expert-level clinical reasoning. While it can process other topics, the prompts are specifically tuned for depression/anxiety literature.

## Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Required: your course API key (example shows the amp-v1 prefix)
echo 'AMPLIFY_API_KEY=YOUR_KEY' >> .env

# Required: your course Amplify Chat Completions endpoint (from the course PDF guide)
echo 'AMPLIFY_API_URL=https://<your-amplify-endpoint>/chat/completions' >> .env

# Optional: model (keep 4o-mini to stay within quotas)
echo 'AMPLIFY_MODEL=4o-mini' >> .env

# Optional: auth header name (defaults to x-api-key). If your gateway uses Authorization:
# echo 'AMPLIFY_HEADER_NAME=Authorization' >> .env
```

> This project defaults to `x-api-key: <YOUR_KEY>` for authentication. If your gateway requires `Authorization: Bearer <key>`, set `AMPLIFY_HEADER_NAME=Authorization` in `.env`. You do **not** need to modify code.

---

## Inputs & Outputs (CSV for every step; you can replace inputs)
Each step writes an explicit CSV. You may swap in your own file for any step as long as it contains the minimum required columns.

| Step | Default Input | Default Output | Minimum Required Columns |
|---|---|---|---|
| **Step 1 — Retrieve** | *(none)* | `outputs/step1_retrieved.csv` | `pmid,title,abstract,date,journal,publication_type,year` |
| **Step 2 — Classify/Filter** | `outputs/step1_retrieved.csv` | `outputs/step2_filtered.csv` | Same as Step 1 **plus** `classification` |
| **Step 3 — Extract (schema)** | `outputs/step2_filtered.csv` | `outputs/step3_extracted.csv` | Same as Step 2 **plus** `population,risk_factor,symptom,treatment,outcome` |
| **Step 4 — Per-article QA** | `outputs/step3_extracted.csv` | `outputs/step4_qa.csv`, `outputs/qa_bank.csv` | Same as Step 3 **plus** `qa_type,qa_question,qa_answer,qa_explanation` |

---

## Quick Demo Options

### Option 1: Quick Commands (Recommended)
**Core pipeline (3 essential steps):**
```bash
# Core: retrieve → classify → extract
python run.py core --keywords "depression OR anxiety" --start-year 2020 --end-year 2024 --sample-per-year 100
```

**Full pipeline (all 5 steps with control):**
```bash
# Full pipeline (all steps including optional split & QA)
python run.py pipeline --keywords "depression OR anxiety" --start-year 2020 --end-year 2024 --sample-per-year 100

# Skip optional steps
python run.py pipeline --skip-split --skip-qa

# Start from a specific step (if you have existing CSVs)
python run.py pipeline --start-from classify --skip-split
python run.py pipeline --start-from extract --skip-qa
```

### Option 2: Step-by-Step Control
**Step 1 — Retrieve** (user controls the keywords/time range/sample size)
```bash
python run.py retrieve   --keywords "depression OR anxiety"   --start-year 2020   --end-year 2024   --sample-per-year 100
```
Output: `outputs/step1_retrieved.csv` with columns exactly: `pmid,title,abstract,date,journal,publication_type,year`.

**Step 2 — Classify/Filter** (Amplify; strict JSON)
```bash
python run.py classify --input outputs/step1_retrieved.csv
```
Output: `outputs/step2_filtered.csv` (keeps `classification == YES`).

**Step 3 — Extract (schema fields)** (Amplify; strict JSON)
```bash
python run.py extract --input outputs/step2_filtered.csv
```
Output: `outputs/step3_extracted.csv` (adds `population,risk_factor,symptom,treatment,outcome`).

**Step 3b — Split fields** [OPTIONAL] (Post-processing)
```bash
python run.py split --input outputs/step3_extracted.csv
```
Output: `outputs/step3_split.csv` (processes structured field output).

**Step 4 — Per-article QA** [OPTIONAL] (Amplify; strict JSON)
```bash
python run.py qa --input outputs/step3_extracted.csv
```
Outputs: `outputs/step4_qa.csv` (adds `qa_type,qa_question,qa_answer,qa_explanation`) and `outputs/qa_bank.csv` (QA-only export).

---

## 🔗 Agent Integration & Export

**This pipeline is designed to be used as an exportable agent by other AI systems (e.g., Assignment 4 models).**

### Quick Integration
```python
from export_agent import ClinicalResearchAgent, get_clinical_data_for_agent

# Initialize the agent
agent = ClinicalResearchAgent()

# Run core pipeline (outputs step3_extracted.csv for other agents)
result = agent.run_core_pipeline(
    keywords="bipolar disorder",
    start_year=2022, 
    end_year=2024,
    sample_per_year=50
)

# Get extracted clinical data for integration
clinical_data = agent.get_extracted_data()  # Returns pandas DataFrame
json_data = agent.export_data_for_agent("json")  # For API integration
```

### For Assignment 4 Integration
```python
# Assignment 4 agent can call this agent:
from assignment3.azure_xia.export_agent import get_clinical_data_for_agent

# Get clinical research data
clinical_df = get_clinical_data_for_agent("/path/to/assignment3/azure_xia/")

# The DataFrame contains columns: pmid, title, abstract, population, 
# risk_factors, symptoms, treatments, outcomes, classification
# Perfect input for Assignment 4 population-stratum analysis!
```

### Available Agent Methods
- `run_core_pipeline()` - Run 3 essential steps, outputs clinical data
- `run_full_pipeline()` - Run all 5 steps with optional controls  
- `get_extracted_data()` - Get step3 clinical data (main output for other agents)
- `get_qa_bank()` - Get generated Q&A knowledge base
- `export_data_for_agent()` - Export in various formats (JSON, dict, CSV path)
- `get_pipeline_status()` - Check which outputs are available
- `get_summary_stats()` - Get processing statistics

### Integration Workflow
1. **Assignment 3 Agent** (this pipeline): 
   - Retrieves papers from PubMed
   - Filters for relevance  
   - Extracts clinical data (population, risk_factors, symptoms, treatments, outcomes)
   - Outputs: `step3_extracted.csv`

2. **Assignment 4 Agent** (your population analysis):
   - Imports Assignment 3 extracted data
   - Performs population-stratum analysis
   - Uses clinical data for advanced analytics

**Key Integration Point**: The `step3_extracted.csv` output from Assignment 3 becomes the input data for Assignment 4 population analysis.

---

## Cost/Time Tips
- If you already have CSVs for any steps, start from Step 2/3/4 using `--input` to save time and API budget.
- Prompts return compact JSON with low temperature using **4o-mini**.
- Start with a smaller subset (e.g., fewer rows) to validate the pipeline before scaling up.
