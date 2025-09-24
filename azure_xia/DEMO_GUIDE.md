# 🧠 Clinical Research Pipeline Demo Guide

## Overview
This interactive demo showcases your multi-agent clinical research pipeline with optional steps and flexible execution modes. Perfect for presentations and audience demonstrations.

## Quick Start

### Option 1: One-Command Launch
```bash
./run_demo.sh
```

### Option 2: Manual Launch
```bash
pip install -r requirements_demo.txt
streamlit run demo_visualization.py
```

## Demo Features

### 🤖 Multi-Agent Architecture
- **Core Agents**: Retrieval, Classification, Extraction (always active)
- **Optional Agents**: Split, QA Generation (user-configurable)
- **Flexible Pipeline**: Skip optional steps, start from any point

### 📊 Interactive Visualizations
1. **Pipeline Overview**: Shows agent workflow and status
2. **Data Flow**: Funnel chart of processing stages
3. **Commands & Usage**: Live command examples
4. **Agent Status**: Real-time agent dashboard
5. **Temporal Analysis**: Research trends over time
6. **Journal Analysis**: Publication source distribution
7. **Clinical Extraction**: Extracted clinical data insights
8. **Knowledge Base**: AI-generated Q&A pairs

### 💻 Live Pipeline Commands
The demo shows actual commands audiences can run:

```bash
# Core pipeline (3 essential steps)
python run.py core --keywords "depression OR anxiety"

# Full pipeline (all 5 steps)
python run.py pipeline --keywords "depression OR anxiety"

# Skip optional steps
python run.py pipeline --skip-split --skip-qa

# Start from specific step
python run.py pipeline --start-from classify
```

## Presentation Tips

### For Technical Audiences
- Show the **Agent Status** section to highlight multi-agent architecture
- Demonstrate **Commands & Usage** for implementation details
- Walk through **Data Flow** to explain processing efficiency

### For Clinical/Research Audiences
- Focus on **Clinical Extraction** and **Knowledge Base** sections
- Show **Temporal Analysis** and **Journal Analysis** for research insights
- Highlight the flexibility of optional QA generation

### For Business/Demo Audiences
- Start with **Pipeline Overview** for the big picture
- Show **Data Flow** metrics and processing efficiency
- Demonstrate **Knowledge Base** as the end product

## Key Demo Points

### 🎯 Flexible Architecture
- **Core Steps**: Always essential (retrieve → classify → extract)
- **Optional Steps**: User choice (split, QA generation)
- **Smart Execution**: Can start from any step, skip steps as needed

### 🤖 Agent-Based Design
- Each step is handled by a specialized AI agent
- Agents work independently but coordinate data flow
- Optional agents can be activated/deactivated by user preference

### 📈 Real Data
- Uses actual clinical research papers from PubMed
- Shows real extraction results and generated Q&A pairs
- Demonstrates actual processing volumes and efficiency

## Demo Data
The visualization automatically loads existing pipeline outputs:
- `outputs/step1_retrieved.csv` - Retrieved papers
- `outputs/step2_filtered.csv` - Filtered relevant papers  
- `outputs/step3_extracted.csv` - Extracted clinical data
- `outputs/step3_split.csv` - Split fields (if generated)
- `outputs/qa_bank.csv` - Generated Q&A pairs (if generated)

## Troubleshooting

### No Data Showing?
Run the pipeline first to generate demo data:
```bash
# Quick demo data (3 steps)
python run.py core --keywords "depression OR anxiety" --sample-per-year 50

# Complete demo data (5 steps)
python run.py pipeline --keywords "depression OR anxiety" --sample-per-year 50
```

### Missing Visualizations?
Install demo requirements:
```bash
pip install -r requirements_demo.txt
```

### Demo Won't Start?
Check Python environment and run:
```bash
streamlit --version
python demo_visualization.py
```

## Customization

### Change Demo Data
Run pipeline with different parameters:
```bash
# Core pipeline for quick demo data
python run.py core --keywords "your keywords" --start-year 2020 --end-year 2024

# Full pipeline for complete demo
python run.py pipeline --keywords "your keywords" --start-year 2020 --end-year 2024
```

### Modify Visualizations
Edit `demo_visualization.py` to customize:
- Color schemes
- Chart types  
- Metrics displayed
- Sample sizes

---

**🎯 Perfect for showcasing your clinical research AI agent system!**