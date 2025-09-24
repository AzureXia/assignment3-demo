#!/usr/bin/env python3
"""
Example: How Assignment 4 can integrate with Assignment 3 Agent
Demonstrates the workflow for using Assignment 3 clinical data in Assignment 4 analysis
"""

import sys
import os
from pathlib import Path

# Add the Assignment 3 path to import the agent
# In real usage, adjust the path to point to your Assignment 3 directory
ASSIGNMENT3_PATH = "/Users/jacinda/amplify-api-course/assignment3/azure_xia"
sys.path.insert(0, ASSIGNMENT3_PATH)

try:
    from export_agent import ClinicalResearchAgent, get_clinical_data_for_agent
    print("✅ Successfully imported Assignment 3 Clinical Research Agent")
except ImportError as e:
    print(f"❌ Error importing Assignment 3 agent: {e}")
    print(f"Make sure the path is correct: {ASSIGNMENT3_PATH}")
    sys.exit(1)

def assignment4_workflow_example():
    """
    Example workflow showing how Assignment 4 can use Assignment 3 data
    """
    print("\n" + "="*60)
    print("Assignment 4 Integration Example")
    print("="*60)
    
    # Step 1: Initialize Assignment 3 agent
    print("\n1. Initializing Assignment 3 Clinical Research Agent...")
    clinical_agent = ClinicalResearchAgent(ASSIGNMENT3_PATH)
    
    # Step 2: Check if clinical data already exists
    print("\n2. Checking for existing clinical data...")
    status = clinical_agent.get_pipeline_status()
    
    if status["step3_extracted"]:
        print("✅ Clinical data already available!")
        stats = clinical_agent.get_summary_stats()
        print(f"   - {stats['extracted_papers']} papers with clinical data")
    else:
        print("🔄 Running core pipeline to generate clinical data...")
        
        # Step 3: Run core pipeline if needed
        result = clinical_agent.run_core_pipeline(
            keywords="depression OR anxiety OR bipolar disorder",
            start_year=2022,
            end_year=2024,
            sample_per_year=30  # Smaller sample for demo
        )
        
        if result["status"] == "success":
            print("✅ Core pipeline completed successfully!")
            print(f"   Output file: {result['step3_output']}")
        else:
            print(f"❌ Pipeline failed: {result['message']}")
            return None
    
    # Step 4: Get clinical data for Assignment 4
    print("\n3. Extracting clinical data for Assignment 4...")
    
    try:
        # Get the extracted clinical data
        clinical_df = clinical_agent.get_extracted_data()
        print(f"✅ Retrieved {len(clinical_df)} clinical records")
        
        # Show data structure
        print(f"\n📊 Data Structure for Assignment 4:")
        print(f"   Columns: {list(clinical_df.columns)}")
        print(f"   Key fields for population analysis:")
        print(f"   - population: {clinical_df['population'].notna().sum()} records")
        print(f"   - risk_factors: {clinical_df['risk_factors'].notna().sum()} records")
        print(f"   - symptoms: {clinical_df['symptoms'].notna().sum()} records")
        print(f"   - treatments: {clinical_df['treatments'].notna().sum()} records") 
        print(f"   - outcomes: {clinical_df['outcomes'].notna().sum()} records")
        
        # Step 5: Example Assignment 4 processing
        print(f"\n4. Assignment 4 Population Analysis (Example)...")
        
        # Extract unique populations for stratum analysis
        populations = []
        for pop in clinical_df['population'].dropna():
            if isinstance(pop, str):
                populations.extend([p.strip() for p in pop.split(',') if p.strip()])
        
        unique_populations = list(set(populations))
        print(f"   Found {len(unique_populations)} unique population types:")
        
        # Show top population types
        from collections import Counter
        pop_counts = Counter(populations)
        for pop, count in pop_counts.most_common(5):
            print(f"   - {pop}: {count} studies")
        
        # Export data in different formats for Assignment 4
        print(f"\n5. Exporting data for Assignment 4...")
        
        # Option 1: CSV file path (for file-based integration)
        csv_path = clinical_agent.export_data_for_agent("csv_path")
        print(f"   📄 CSV file: {csv_path}")
        
        # Option 2: JSON string (for API integration)
        json_data = clinical_agent.export_data_for_agent("json")
        print(f"   📋 JSON data: {len(json_data)} characters")
        
        # Option 3: Python dict (for direct integration)
        dict_data = clinical_agent.export_data_for_agent("dict")
        print(f"   🐍 Python dict: {len(dict_data)} records")
        
        return {
            "dataframe": clinical_df,
            "csv_path": csv_path,
            "json_data": json_data,
            "dict_data": dict_data,
            "populations": unique_populations
        }
        
    except Exception as e:
        print(f"❌ Error processing clinical data: {e}")
        return None

def assignment4_analysis_simulation(data):
    """
    Simulate Assignment 4 population-stratum analysis using Assignment 3 data
    """
    if not data:
        return
        
    print("\n" + "="*60)
    print("Assignment 4 Analysis Simulation")
    print("="*60)
    
    df = data["dataframe"]
    populations = data["populations"]
    
    print(f"\n🔬 Population-Stratum Analysis Simulation:")
    print(f"   Total clinical records: {len(df)}")
    print(f"   Population types identified: {len(populations)}")
    
    # Simulate stratum analysis
    strata = []
    for _, row in df.iterrows():
        if pd.notna(row.get('population')):
            strata.append({
                'pmid': row.get('pmid'),
                'population': row.get('population'),
                'risk_factors': row.get('risk_factors', 'Not specified'),
                'symptoms': row.get('symptoms', 'Not specified'),
                'treatment': row.get('treatments', 'Not specified'),
                'outcome': row.get('outcomes', 'Not specified')
            })
    
    print(f"   Analyzable strata: {len(strata)}")
    
    # Group by population type
    population_groups = {}
    for stratum in strata:
        pop_key = stratum['population'][:30] + "..." if len(stratum['population']) > 30 else stratum['population']
        if pop_key not in population_groups:
            population_groups[pop_key] = []
        population_groups[pop_key].append(stratum)
    
    print(f"\n📈 Population Groups for Analysis:")
    for pop_group, strata_list in list(population_groups.items())[:5]:
        print(f"   - {pop_group}: {len(strata_list)} strata")
    
    print(f"\n✅ Assignment 4 can now perform:")
    print(f"   - Population stratification analysis")
    print(f"   - Risk factor analysis by population stratum")
    print(f"   - Symptom patterns across populations")
    print(f"   - Treatment effectiveness by population")
    print(f"   - Outcome prediction modeling")
    print(f"   - Multi-dimensional stratum analysis")

if __name__ == "__main__":
    import pandas as pd
    
    print("Assignment 3 → Assignment 4 Integration Demo")
    print("This demonstrates how Assignment 4 can use Assignment 3 clinical data")
    
    # Run the integration workflow
    data = assignment4_workflow_example()
    
    # Simulate Assignment 4 analysis
    if data:
        assignment4_analysis_simulation(data)
        
        print(f"\n" + "="*60)
        print("Integration Complete!")
        print("="*60)
        print(f"✅ Assignment 3 clinical data is ready for Assignment 4")
        print(f"✅ Data formats exported: CSV, JSON, Python dict")
        print(f"✅ Population strata identified for analysis")
        print(f"\n🔗 Key Integration Point:")
        print(f"   Assignment 3 step3_extracted.csv → Assignment 4 input data")
    else:
        print(f"\n❌ Integration failed. Check the setup and try again.")