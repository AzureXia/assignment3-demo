#!/usr/bin/env python3
"""
Interactive Demo Visualization for Clinical Depression & Anxiety Knowledge Base Pipeline
Showcases the agent-based pipeline with real-time visualizations and statistics
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import os
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Clinical Research Pipeline Demo",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .pipeline-step {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .agent-status {
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        color: #2e8b57;
        font-weight: bold;
    }
    .optional-step {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load all pipeline output data"""
    data = {}
    try:
        # Load each step's data
        if os.path.exists("outputs/step1_retrieved.csv"):
            data['step1'] = pd.read_csv("outputs/step1_retrieved.csv")
        if os.path.exists("outputs/step2_filtered.csv"):
            data['step2'] = pd.read_csv("outputs/step2_filtered.csv")
        if os.path.exists("outputs/step3_extracted.csv"):
            data['step3'] = pd.read_csv("outputs/step3_extracted.csv")
        if os.path.exists("outputs/step3_split.csv"):
            data['step3_split'] = pd.read_csv("outputs/step3_split.csv")
        if os.path.exists("outputs/step4_qa.csv"):
            data['step4'] = pd.read_csv("outputs/step4_qa.csv")
        if os.path.exists("outputs/qa_bank.csv"):
            data['qa_bank'] = pd.read_csv("outputs/qa_bank.csv")
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return data

def create_pipeline_overview():
    """Create pipeline overview visualization"""
    # Pipeline steps - removed redundant title
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="pipeline-step">
            <h4>Step 1: Retrieve</h4>
            <p>Agent retrieves papers from PubMed using intelligent keyword matching</p>
            <div class="agent-status">Retrieval Agent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pipeline-step">
            <h4>Step 2: Classify</h4>
            <p>AI agent filters relevant depression/anxiety research</p>
            <div class="agent-status">Classification Agent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pipeline-step">
            <h4>Step 3: Extract</h4>
            <p>Schema extraction agent identifies key clinical data</p>
            <div class="agent-status">Extraction Agent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="pipeline-step optional-step">
            <h4>Optional Steps</h4>
            <p><strong>3b:</strong> Field splitting<br><strong>4:</strong> QA generation</p>
            <div class="agent-status">Optional Agents</div>
        </div>
        """, unsafe_allow_html=True)

def create_data_flow_viz(data):
    """Create data flow visualization"""
    if not data:
        return
    
    # Calculate data counts at each step
    counts = []
    steps = ['Retrieved', 'Filtered', 'Extracted', 'Split (Optional)', 'QA Generated (Optional)']
    
    counts.append(len(data.get('step1', [])))
    counts.append(len(data.get('step2', [])))
    counts.append(len(data.get('step3', [])))
    counts.append(len(data.get('step3_split', [])))
    counts.append(len(data.get('qa_bank', [])))
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y = steps,
        x = counts,
        textinfo = "value+percent initial",
        marker_color = ["#1f77b4", "#ff7f0e", "#2ca02c", "#ffc107", "#d62728"],
        connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}}
    ))
    
    fig.update_layout(
        title="Agent Pipeline Data Flow",
        height=500,
        font_size=14
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_metrics_dashboard(data):
    """Create key metrics dashboard"""
    if not data:
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'step1' in data:
            total_papers = len(data['step1'])
            st.metric("Papers Retrieved", f"{total_papers:,}")
    
    with col2:
        if 'step2' in data:
            filtered_papers = len(data['step2'])
            if 'step1' in data and len(data['step1']) > 0:
                filter_rate = (filtered_papers / len(data['step1']) * 100)
                st.metric("Relevant Papers", f"{filtered_papers:,}", f"{filter_rate:.1f}% pass rate")
            else:
                st.metric("Relevant Papers", f"{filtered_papers:,}")
    
    with col3:
        if 'step3' in data:
            extracted_papers = len(data['step3'])
            st.metric("Data Extracted", f"{extracted_papers:,}")
    
    with col4:
        if 'step3_split' in data:
            split_papers = len(data['step3_split'])
            st.metric("Fields Split", f"{split_papers:,}")
        else:
            st.metric("Fields Split", "0", "Optional step skipped")
    
    with col5:
        if 'qa_bank' in data:
            qa_pairs = len(data['qa_bank'])
            st.metric("QA Pairs", f"{qa_pairs:,}")
        else:
            st.metric("QA Pairs", "0", "Optional step skipped")

def create_temporal_analysis(data):
    """Create temporal analysis of research papers"""
    if 'step1' not in data:
        return
    
    df = data['step1'].copy()
    if 'year' not in df.columns:
        return
    
    # Year distribution
    year_counts = df['year'].value_counts().sort_index()
    
    fig = px.bar(
        x=year_counts.index,
        y=year_counts.values,
        title="Research Papers by Publication Year",
        labels={'x': 'Publication Year', 'y': 'Number of Papers'},
        color=year_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def create_journal_analysis(data):
    """Create journal distribution analysis with impact factor coloring"""
    if 'step1' not in data:
        return
    
    df = data['step1'].copy()
    if 'journal' not in df.columns:
        return
    
    # Top journals
    journal_counts = df['journal'].value_counts().head(10)
    
    # Approximate impact factors for common journals (for demo purposes)
    # In a real implementation, you'd fetch these from a database
    impact_factors = {
        'Nature': 69.5,
        'Science': 63.7,
        'Cell': 66.8,
        'The Lancet': 202.7,
        'New England Journal of Medicine': 176.1,
        'JAMA': 157.3,
        'Nature Medicine': 87.2,
        'Nature Neuroscience': 28.8,
        'Biological Psychiatry': 13.6,
        'American Journal of Psychiatry': 19.2,
        'Journal of Clinical Investigation': 19.4,
        'Proceedings of the National Academy of Sciences': 12.8,
        'PNAS': 12.8,
        'Nature Communications': 17.7,
        'PLOS ONE': 3.7,
        'Scientific Reports': 4.6,
        'Journal of Affective Disorders': 6.5,
        'Depression and Anxiety': 6.4,
        'Psychological Medicine': 5.9,
        'Journal of Psychiatric Research': 4.8,
        'Psychiatry Research': 2.5,
        'BMC Psychiatry': 4.3,
        'Frontiers in Psychiatry': 4.2,
        'International Journal of Mental Health': 2.1,
        'Journal of Mental Health': 3.4
    }
    
    # Map impact factors to journals (use average if not found)
    avg_impact_factor = 5.0  # Default for unknown journals
    journal_impact_factors = []
    
    for journal in journal_counts.index:
        # Try exact match first
        if journal in impact_factors:
            journal_impact_factors.append(impact_factors[journal])
        else:
            # Try partial matching for journals with similar names
            found_match = False
            for known_journal in impact_factors.keys():
                if known_journal.lower() in journal.lower() or journal.lower() in known_journal.lower():
                    journal_impact_factors.append(impact_factors[known_journal])
                    found_match = True
                    break
            if not found_match:
                journal_impact_factors.append(avg_impact_factor)
    
    fig = px.bar(
        x=journal_counts.values,
        y=journal_counts.index,
        orientation='h',
        title="Top 10 Journals in Dataset (Color = Impact Factor)",
        labels={'x': 'Number of Papers', 'y': 'Journal', 'color': 'Impact Factor'},
        color=journal_impact_factors,
        color_continuous_scale='RdYlBu_r',  # Red-Yellow-Blue (reversed, so red = high impact)
        hover_data={'Impact Factor': journal_impact_factors}
    )
    
    # Update color bar
    fig.update_layout(
        height=500, 
        showlegend=False,
        coloraxis_colorbar=dict(
            title="Impact Factor",
            title_side="right"
        )
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
                      "Papers: %{x}<br>" +
                      "Impact Factor: %{color:.1f}<br>" +
                      "<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    st.caption("Colors represent approximate impact factors: Red = High impact, Yellow = Medium impact, Blue = Lower impact")

def create_extraction_analysis(data):
    """Analyze extracted clinical data"""
    if 'step3' not in data:
        return
    
    df = data['step3'].copy()
    
    # Analyze extracted fields
    st.subheader("Clinical Data Extraction Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Population analysis
        if 'population' in df.columns:
            populations = []
            for pop in df['population'].dropna():
                if isinstance(pop, str) and pop.strip():
                    populations.extend([p.strip() for p in pop.split(',') if p.strip()])
            
            if populations:
                pop_counts = Counter(populations)
                top_pops = dict(pop_counts.most_common(8))
                
                fig = px.pie(
                    values=list(top_pops.values()),
                    names=list(top_pops.keys()),
                    title="Study Populations"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Treatment analysis
        if 'treatments' in df.columns:
            treatments = []
            for treat in df['treatments'].dropna():
                if isinstance(treat, str) and treat.strip():
                    treatments.extend([t.strip() for t in treat.split(',') if t.strip()])
            
            if treatments:
                treat_counts = Counter(treatments)
                top_treats = dict(treat_counts.most_common(8))
                
                fig = px.pie(
                    values=list(top_treats.values()),
                    names=list(top_treats.keys()),
                    title="Treatment Types"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

def create_qa_analysis(data):
    """Analyze generated QA pairs"""
    if 'qa_bank' not in data:
        st.warning("QA Generation was skipped (optional step)")
        return
    
    df = data['qa_bank'].copy()
    
    st.subheader("AI-Generated Knowledge Base")
    
    # Show sample QA pairs
    if len(df) > 0:
        st.write("### Sample Q&A Pairs Generated by AI Agent:")
        
        # Display 3 random QA pairs
        sample_qa = df.sample(min(5, len(df)))
        
        for idx, row in sample_qa.iterrows():
            with st.expander(f"Q: {row['qa_question'][:100]}..."):
                st.write("**Answer:**", row['qa_answer'])
                st.write("**Explanation:**", row['qa_explanation'])

def create_interactive_command_builder():
    """Interactive command builder for live demo"""
    st.subheader("Interactive Command Builder")
    st.write("Customize your pipeline parameters and generate the command to run:")
    
    # Create tabs for different pipeline types
    tab1, tab2, tab3 = st.tabs(["Core Pipeline", "Full Pipeline", "Individual Steps"])
    
    with tab1:
        st.write("**Build your core pipeline command (3 essential steps)**")
        
        col1, col2 = st.columns(2)
        with col1:
            keywords_core = st.text_input("Research Keywords", "depression OR anxiety", key="core_keywords")
            start_year_core = st.number_input("Start Year", 2020, 2024, 2020, key="core_start")
            end_year_core = st.number_input("End Year", 2020, 2024, 2024, key="core_end")
        
        with col2:
            sample_per_year_core = st.number_input("Samples per Year", 10, 500, 100, key="core_sample")
            start_from_core = st.selectbox("Start From Step", ["retrieve", "classify", "extract"], key="core_start_from")
        
        # Generate command
        core_cmd = f'python run.py core --keywords "{keywords_core}" --start-year {start_year_core} --end-year {end_year_core} --sample-per-year {sample_per_year_core}'
        if start_from_core != "retrieve":
            core_cmd += f' --start-from {start_from_core}'
        
        st.code(core_cmd, language="bash")
        
        if st.button("Copy Core Command", key="copy_core"):
            st.success("Command copied to clipboard! (manual copy from above)")
    
    with tab2:
        st.write("**Build your full pipeline command (all 5 steps with options)**")
        
        col1, col2 = st.columns(2)
        with col1:
            keywords_full = st.text_input("Research Keywords", "depression OR anxiety", key="full_keywords")
            start_year_full = st.number_input("Start Year", 2020, 2024, 2020, key="full_start")
            end_year_full = st.number_input("End Year", 2020, 2024, 2024, key="full_end")
            sample_per_year_full = st.number_input("Samples per Year", 10, 500, 100, key="full_sample")
        
        with col2:
            start_from_full = st.selectbox("Start From Step", ["retrieve", "classify", "extract"], key="full_start_from")
            skip_split = st.checkbox("Skip Split Step (3b)", key="skip_split")
            skip_qa = st.checkbox("Skip QA Step (4)", key="skip_qa")
        
        # Generate command
        full_cmd = f'python run.py pipeline --keywords "{keywords_full}" --start-year {start_year_full} --end-year {end_year_full} --sample-per-year {sample_per_year_full}'
        if start_from_full != "retrieve":
            full_cmd += f' --start-from {start_from_full}'
        if skip_split:
            full_cmd += ' --skip-split'
        if skip_qa:
            full_cmd += ' --skip-qa'
        
        st.code(full_cmd, language="bash")
        
        if st.button("Copy Full Command", key="copy_full"):
            st.success("Command copied to clipboard! (manual copy from above)")
    
    with tab3:
        st.write("**Run individual pipeline steps**")
        
        step_choice = st.selectbox("Choose Step", [
            "retrieve - Get papers from PubMed",
            "classify - Filter relevant papers", 
            "extract - Extract clinical data",
            "split - Split structured fields (optional)",
            "qa - Generate Q&A pairs (optional)"
        ])
        
        step_name = step_choice.split(" - ")[0]
        
        if step_name == "retrieve":
            col1, col2 = st.columns(2)
            with col1:
                keywords_indiv = st.text_input("Research Keywords", "depression OR anxiety", key="indiv_keywords")
                start_year_indiv = st.number_input("Start Year", 2020, 2024, 2020, key="indiv_start")
                end_year_indiv = st.number_input("End Year", 2020, 2024, 2024, key="indiv_end")
            with col2:
                sample_per_year_indiv = st.number_input("Samples per Year", 10, 500, 100, key="indiv_sample")
                output_file = st.text_input("Output File", "outputs/step1_retrieved.csv", key="indiv_output")
            
            indiv_cmd = f'python run.py retrieve --keywords "{keywords_indiv}" --start-year {start_year_indiv} --end-year {end_year_indiv} --sample-per-year {sample_per_year_indiv} --out {output_file}'
        else:
            # Set default input files based on step
            input_defaults = {
                'classify': 'outputs/step1_retrieved.csv',
                'extract': 'outputs/step2_filtered.csv', 
                'split': 'outputs/step3_extracted.csv',
                'qa': 'outputs/step3_extracted.csv'
            }
            output_defaults = {
                'classify': 'outputs/step2_filtered.csv',
                'extract': 'outputs/step3_extracted.csv',
                'split': 'outputs/step3_split.csv', 
                'qa': 'outputs/step4_qa.csv'
            }
            
            input_file = st.text_input("Input CSV File", input_defaults[step_name], key="indiv_input")
            output_file = st.text_input("Output File", output_defaults[step_name], key="indiv_output_other")
            
            indiv_cmd = f'python run.py {step_name} --input {input_file} --out {output_file}'
            if step_name == "qa":
                qa_bank = st.text_input("QA Bank File", "outputs/qa_bank.csv", key="qa_bank")
                indiv_cmd += f' --qa-bank {qa_bank}'
        
        st.code(indiv_cmd, language="bash")
        
        if st.button("Copy Individual Command", key="copy_indiv"):
            st.success("Command copied to clipboard! (manual copy from above)")

def create_pipeline_commands():
    """Show static pipeline command examples"""
    st.subheader("Example Commands")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Core Pipeline (3 Essential Steps)**")
        st.code("""
# retrieve → classify → extract
python run.py core \\
  --keywords "depression OR anxiety" \\
  --start-year 2020 \\
  --end-year 2024 \\
  --sample-per-year 100
        """, language="bash")
        
        st.write("**Full Pipeline (All 5 Steps)**")
        st.code("""
# All steps including optional split & QA
python run.py pipeline \\
  --keywords "depression OR anxiety" \\
  --start-year 2020 \\
  --end-year 2024
        """, language="bash")
    
    with col2:
        st.write("**Skip Optional Steps**")
        st.code("""
# Skip split step
python run.py pipeline --skip-split

# Skip both optional steps (same as core)
python run.py pipeline --skip-split --skip-qa
        """, language="bash")
        
        st.write("**Individual Steps**")
        st.code("""
python run.py extract --input outputs/step2_filtered.csv
python run.py qa --input outputs/step3_extracted.csv
        """, language="bash")

def create_agent_status():
    """Show agent processing status"""
    st.subheader("Agent Status Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Core Agents (Always Active)**")
        agents = [
            ("Retrieval Agent", "PubMed data collection", "Ready"),
            ("Classification Agent", "Relevance filtering", "Ready"),
            ("Extraction Agent", "Clinical data parsing", "Ready")
        ]
        
        for name, desc, status in agents:
            st.write(f"**{name}**")
            st.write(f"*{desc}*")
            st.write(f"`{status}`")
            st.write("---")
    
    with col2:
        st.write("**Optional Agents (User Configurable)**")
        optional_agents = [
            ("Split Agent", "Field structuring", "Optional"),
            ("QA Agent", "Knowledge base generation", "Optional")
        ]
        
        for name, desc, status in optional_agents:
            st.write(f"**{name}**")
            st.write(f"*{desc}*")
            st.write(f"`{status}`")
            st.write("---")
    
    with col3:
        st.write("**Pipeline Configuration**")
        st.write("**Flexibility Features:**")
        st.write("• Skip optional steps")
        st.write("• Start from any step")
        st.write("• Individual step execution")
        st.write("• Custom parameters")

def create_agent_integration():
    """Show agent integration and export capabilities"""
    st.subheader("Agent Integration & Export")
    
    st.write("This pipeline is designed as an **exportable agent** for integration with other AI systems.")
    
    # Integration overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Integration Workflow**")
        st.markdown("""
        1. **Assignment 3 Agent** (this pipeline):
           - Retrieves papers from PubMed
           - Filters for clinical relevance
           - Extracts structured clinical data
           - Outputs: `step3_extracted.csv`
        
        2. **Assignment 4 Agent** (population analysis):
           - Imports Assignment 3 clinical data
           - Performs population-stratum analysis
           - Uses clinical data for advanced analytics
        """)
    
    with col2:
        st.write("**Key Integration Point**")
        st.info("The `step3_extracted.csv` output becomes the input data for Assignment 4 population analysis.")
        
        st.write("**Data Format**")
        st.write("Exported data contains:")
        st.write("• `pmid` - Paper identifier")
        st.write("• `title` - Paper title")
        st.write("• `abstract` - Paper abstract")
        st.write("• `population` - Study population")
        st.write("• `risk_factors` - Risk factors identified")
        st.write("• `treatments` - Treatment methods")
        st.write("• `outcomes` - Clinical outcomes")
        st.write("• `symptoms` - Symptoms described")
    
    # Code examples
    st.write("**Integration Code Examples**")
    
    tab1, tab2, tab3 = st.tabs(["Quick Integration", "Assignment 4 Usage", "Advanced Export"])
    
    with tab1:
        st.write("**Basic Agent Usage:**")
        st.code("""
from export_agent import ClinicalResearchAgent

# Initialize the agent
agent = ClinicalResearchAgent()

# Run core pipeline (outputs clinical data)
result = agent.run_core_pipeline(
    keywords="bipolar disorder",
    start_year=2022,
    end_year=2024,
    sample_per_year=50
)

# Get extracted clinical data
clinical_data = agent.get_extracted_data()
print(f"Retrieved {len(clinical_data)} clinical records")
        """, language="python")
    
    with tab2:
        st.write("**Assignment 4 Integration:**")
        st.code("""
# Assignment 4 agent imports Assignment 3
from assignment3.azure_xia.export_agent import get_clinical_data_for_agent

# Get clinical research data
clinical_df = get_clinical_data_for_agent("/path/to/assignment3/azure_xia/")

# Perfect input for population-stratum analysis!
populations = clinical_df['population'].unique()
risk_factors = clinical_df['risk_factors'].unique()
symptoms = clinical_df['symptoms'].unique()
treatments = clinical_df['treatments'].unique()
outcomes = clinical_df['outcomes'].unique()

# Assignment 4 population-stratum analysis with all required fields
for population in populations:
    subset = clinical_df[clinical_df['population'] == population]
    # Analyze risk factors, symptoms, treatments, outcomes by population...
        """, language="python")
    
    with tab3:
        st.write("**Export in Multiple Formats:**")
        st.code("""
# Export for different integration needs
agent = ClinicalResearchAgent()

# Option 1: CSV file path (for file-based integration)
csv_path = agent.export_data_for_agent("csv_path")

# Option 2: JSON string (for API integration)
json_data = agent.export_data_for_agent("json")

# Option 3: Python dict (for direct integration)
dict_data = agent.export_data_for_agent("dict")

# Check pipeline status
status = agent.get_pipeline_status()
stats = agent.get_summary_stats()
        """, language="python")
    
    # Available methods
    st.write("**Available Agent Methods**")
    
    methods = [
        ("run_core_pipeline()", "Run 3 essential steps, outputs clinical data"),
        ("run_full_pipeline()", "Run all 5 steps with optional controls"),
        ("get_extracted_data()", "Get step3 clinical data (main output for other agents)"),
        ("get_qa_bank()", "Get generated Q&A knowledge base"),
        ("export_data_for_agent()", "Export in various formats (JSON, dict, CSV path)"),
        ("get_pipeline_status()", "Check which outputs are available"),
        ("get_summary_stats()", "Get processing statistics")
    ]
    
    for method, description in methods:
        st.write(f"• **`{method}`** - {description}")
    
    # Integration benefits
    st.write("**Integration Benefits**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Reusability**")
        st.write("• Single agent, multiple consumers")
        st.write("• Standardized data output")
        st.write("• Consistent processing")
    
    with col2:
        st.write("**Flexibility**")
        st.write("• Multiple export formats")
        st.write("• Configurable parameters")
        st.write("• Optional step control")
    
    with col3:
        st.write("**Scalability**")
        st.write("• Programmatic execution")
        st.write("• Batch processing support")
        st.write("• API integration ready")

def main():
    """Main application"""
    
    # Sidebar with unified demo controls
    st.sidebar.title("Clinical Research Pipeline")
    
    # Demo mode selector
    demo_mode = st.sidebar.radio(
        "Demo Mode",
        ["Visualization Dashboard", "Interactive Runner"],
        help="Switch between visualization mode and live pipeline execution"
    )
    
    if demo_mode == "Interactive Runner":
        # Redirect to interactive runner
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
        <h2>Interactive Pipeline Runner</h2>
        <p>To access the interactive pipeline runner with live execution capabilities, please run:</p>
        <code>streamlit run demo_interactive_runner.py</code>
        <p>Or use the launcher script and select option 2</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Load data for visualization mode
    data = load_data()
    
    st.sidebar.markdown("---")
    
    # Sidebar stats
    st.sidebar.subheader("Quick Stats")
    if data:
        if 'step1' in data:
            st.sidebar.metric("Total Papers", len(data['step1']))
        if 'qa_bank' in data:
            st.sidebar.metric("QA Pairs", len(data['qa_bank']))
        if 'step3_split' in data:
            st.sidebar.metric("Split Fields", len(data['step3_split']))
        else:
            st.sidebar.write("Split Step: Skipped")
    
    # Navigation
    demo_section = st.sidebar.selectbox(
        "Choose Section",
        ["Pipeline Overview", "Interactive Commands", "Commands & Usage", "Agent Status",
         "Agent Integration", "Temporal Analysis", "Journal Analysis", "Knowledge Base"]
    )
    
    # Main header
    st.markdown('<div class="main-header">Clinical Research Knowledge Base Pipeline</div>', unsafe_allow_html=True)
    
    # Main content
    if demo_section == "Pipeline Overview":
        create_pipeline_overview()
        create_metrics_dashboard(data)
        create_data_flow_viz(data)
    
    elif demo_section == "Interactive Commands":
        create_interactive_command_builder()
    
    elif demo_section == "Commands & Usage":
        create_pipeline_commands()
    
    elif demo_section == "Agent Status":
        create_agent_status()
    
    elif demo_section == "Agent Integration":
        create_agent_integration()
    
    elif demo_section == "Temporal Analysis":
        create_temporal_analysis(data)
    
    elif demo_section == "Journal Analysis":
        create_journal_analysis(data)
    
    elif demo_section == "Knowledge Base":
        create_qa_analysis(data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        Powered by Multi-Agent AI Pipeline | Clinical Depression & Anxiety Research<br>
        <strong>Flexible Architecture:</strong> Core + Optional Agents | User-Configurable Steps
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()