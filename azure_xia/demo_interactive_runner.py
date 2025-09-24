#!/usr/bin/env python3
"""
Advanced Interactive Demo with Live Pipeline Execution
Allows users to customize parameters and run the pipeline directly from the interface
"""

import streamlit as st
import subprocess
import os
import pandas as pd
import time
from datetime import datetime
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="Interactive Clinical Research Pipeline",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

def run_pipeline_command(cmd, output_queue):
    """Run pipeline command in background thread"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=".")
        output_queue.put({"type": "success", "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
    except Exception as e:
        output_queue.put({"type": "error", "message": str(e)})

def create_live_pipeline_runner():
    """Interactive pipeline runner with live execution"""
    st.title("Live Pipeline Runner")
    st.write("Customize parameters and run the pipeline directly from this interface!")
    
    # Create tabs for different execution modes
    tab1, tab2 = st.tabs(["Quick Run", "Advanced Configuration"])
    
    with tab1:
        st.subheader("Quick Pipeline Execution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pipeline_type = st.radio(
                "Pipeline Type",
                ["core", "pipeline"],
                help="Core = 3 steps (retrieve→classify→extract), Pipeline = all 5 steps"
            )
            
            keywords = st.text_input(
                "Research Keywords",
                "depression OR anxiety",
                help="Enter keywords to search for research papers"
            )
            
        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                start_year = st.number_input("Start Year", 2020, 2024, 2022)
                sample_size = st.number_input("Samples/Year", 10, 200, 50)
            with col2b:
                end_year = st.number_input("End Year", 2020, 2024, 2024)
        
        # Optional settings for pipeline
        if pipeline_type == "pipeline":
            st.write("**Optional Step Control:**")
            col3a, col3b = st.columns(2)
            with col3a:
                skip_split = st.checkbox("Skip Split Step (3b)")
            with col3b:
                skip_qa = st.checkbox("Skip QA Step (4)")
        
        # Build command
        cmd = f'python run.py {pipeline_type} --keywords "{keywords}" --start-year {start_year} --end-year {end_year} --sample-per-year {sample_size}'
        
        if pipeline_type == "pipeline":
            if skip_split:
                cmd += ' --skip-split'
            if skip_qa:
                cmd += ' --skip-qa'
        
        st.write("**Generated Command:**")
        st.code(cmd, language="bash")
        
        # Execution section
        col4, col5 = st.columns([1, 3])
        
        with col4:
            if st.button("Run Pipeline", type="primary", key="run_quick"):
                st.session_state.running = True
                st.session_state.output_queue = queue.Queue()
                st.session_state.thread = threading.Thread(
                    target=run_pipeline_command,
                    args=(cmd, st.session_state.output_queue)
                )
                st.session_state.thread.start()
                st.rerun()
        
        with col5:
            if st.button("Copy Command"):
                st.success("Command ready to copy from above!")
    
    with tab2:
        st.subheader("Advanced Pipeline Configuration")
        
        # Individual step controls
        st.write("**Step-by-Step Execution:**")
        
        steps = {
            "retrieve": {"name": "Step 1: Retrieve", "desc": "Get papers from PubMed"},
            "classify": {"name": "Step 2: Classify", "desc": "Filter relevant papers"},
            "extract": {"name": "Step 3: Extract", "desc": "Extract clinical data"},
            "split": {"name": "Step 3b: Split", "desc": "Split structured fields (optional)"},
            "qa": {"name": "Step 4: QA", "desc": "Generate Q&A pairs (optional)"}
        }
        
        for step_key, step_info in steps.items():
            with st.expander(f"{step_info['name']} - {step_info['desc']}"):
                if step_key == "retrieve":
                    col1, col2 = st.columns(2)
                    with col1:
                        kw = st.text_input("Keywords", "depression OR anxiety", key=f"{step_key}_kw")
                        sy = st.number_input("Start Year", 2020, 2024, 2022, key=f"{step_key}_sy")
                    with col2:
                        ey = st.number_input("End Year", 2020, 2024, 2024, key=f"{step_key}_ey")
                        ss = st.number_input("Samples/Year", 10, 200, 50, key=f"{step_key}_ss")
                    
                    step_cmd = f'python run.py retrieve --keywords "{kw}" --start-year {sy} --end-year {ey} --sample-per-year {ss}'
                else:
                    input_file = st.text_input("Input File", f"outputs/step{'1_retrieved' if step_key == 'classify' else '2_filtered' if step_key == 'extract' else '3_extracted'}.csv", key=f"{step_key}_input")
                    step_cmd = f'python run.py {step_key} --input {input_file}'
                
                st.code(step_cmd, language="bash")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"Run {step_info['name']}", key=f"run_{step_key}"):
                        st.session_state.running = True
                        st.session_state.output_queue = queue.Queue()
                        st.session_state.thread = threading.Thread(
                            target=run_pipeline_command,
                            args=(step_cmd, st.session_state.output_queue)
                        )
                        st.session_state.thread.start()
                        st.rerun()
    
    # Output section
    if hasattr(st.session_state, 'running') and st.session_state.running:
        st.subheader("Pipeline Output")
        
        output_container = st.empty()
        
        # Check if thread is still running
        if st.session_state.thread.is_alive():
            output_container.info("Pipeline is running... Please wait.")
            time.sleep(1)
            st.rerun()
        else:
            # Thread finished, get results
            try:
                result = st.session_state.output_queue.get_nowait()
                st.session_state.running = False
                
                if result["type"] == "success":
                    if result["returncode"] == 0:
                        st.success("Pipeline completed successfully!")
                        if result["stdout"]:
                            st.text_area("Output:", result["stdout"], height=200)
                    else:
                        st.error("Pipeline failed!")
                        if result["stderr"]:
                            st.text_area("Error:", result["stderr"], height=100)
                else:
                    st.error(f"Execution error: {result['message']}")
            except queue.Empty:
                output_container.info("Processing...")
                time.sleep(1)
                st.rerun()

def create_results_viewer():
    """View pipeline results"""
    st.title("Pipeline Results")
    
    # Check for output files
    output_files = {
        "Step 1 - Retrieved": "outputs/step1_retrieved.csv",
        "Step 2 - Filtered": "outputs/step2_filtered.csv", 
        "Step 3 - Extracted": "outputs/step3_extracted.csv",
        "Step 3b - Split": "outputs/step3_split.csv",
        "Step 4 - QA": "outputs/step4_qa.csv",
        "QA Bank": "outputs/qa_bank.csv"
    }
    
    available_files = {name: path for name, path in output_files.items() if os.path.exists(path)}
    
    if not available_files:
        st.warning("No pipeline outputs found. Run the pipeline first!")
        return
    
    # File selector
    selected_file = st.selectbox("Choose Output File", list(available_files.keys()))
    
    if selected_file:
        file_path = available_files[selected_file]
        
        try:
            df = pd.read_csv(file_path)
            
            # File info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                file_size = os.path.getsize(file_path) / 1024  # KB
                st.metric("File Size", f"{file_size:.1f} KB")
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full CSV",
                data=csv,
                file_name=os.path.basename(file_path),
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.title("Interactive Pipeline")
    
    page = st.sidebar.selectbox(
        "Choose Page",
        ["Pipeline Runner", "Results Viewer", "Help"]
    )
    
    if page == "Pipeline Runner":
        create_live_pipeline_runner()
    elif page == "Results Viewer":
        create_results_viewer()
    elif page == "Help":
        st.title("Help & Documentation")
        
        st.markdown("""
        ## How to Use
        
        ### Pipeline Runner
        - **Quick Run**: Configure basic parameters and run core or full pipeline
        - **Advanced Configuration**: Run individual steps with custom settings
        
        ### Results Viewer
        - View and download pipeline outputs
        - Preview data from each processing step
        
        ## Pipeline Types
        
        ### Core Pipeline (`python run.py core`)
        - **3 Steps**: retrieve → classify → extract
        - **Fast**: Essential processing only
        - **Use for**: Quick analysis, testing, basic research
        
        ### Full Pipeline (`python run.py pipeline`)
        - **5 Steps**: retrieve → classify → extract → split → QA
        - **Complete**: All processing including optional steps
        - **Use for**: Full analysis, knowledge base generation
        
        ## Output Files
        - `step1_retrieved.csv` - Raw papers from PubMed
        - `step2_filtered.csv` - Relevant papers only
        - `step3_extracted.csv` - Clinical data extracted
        - `step3_split.csv` - Structured field splits (optional)
        - `step4_qa.csv` - Papers with Q&A pairs (optional)
        - `qa_bank.csv` - Pure Q&A knowledge base (optional)
        
        ## Notes
        - Pipeline execution happens in the background
        - Large datasets may take several minutes
        - Check Results Viewer for outputs after completion
        """)

if __name__ == "__main__":
    main()