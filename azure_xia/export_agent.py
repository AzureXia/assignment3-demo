#!/usr/bin/env python3
"""
Exportable Clinical Research Pipeline Agent
Provides programmatic interface for integration with other agents/systems
"""

import os
import sys
import subprocess
import pandas as pd
from typing import Dict, List, Optional, Union
import json
from pathlib import Path

class ClinicalResearchAgent:
    """
    Exportable agent for clinical depression and anxiety research pipeline.
    Designed for integration with other AI agents and systems.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the Clinical Research Agent
        
        Args:
            base_path: Path to the agent directory. If None, uses current directory.
        """
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.outputs_dir = self.base_path / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)
        
    def run_core_pipeline(self, 
                         keywords: str = "depression OR anxiety",
                         start_year: int = 2020,
                         end_year: int = 2024,
                         sample_per_year: int = 100,
                         start_from: str = "retrieve") -> Dict[str, str]:
        """
        Run the core pipeline (retrieve → classify → extract)
        
        Args:
            keywords: Research keywords to search for
            start_year: Start year for paper retrieval
            end_year: End year for paper retrieval  
            sample_per_year: Number of papers to sample per year
            start_from: Step to start from ('retrieve', 'classify', 'extract')
            
        Returns:
            Dict with status and output file paths
        """
        try:
            cmd = [
                sys.executable, "run.py", "core",
                "--keywords", keywords,
                "--start-year", str(start_year),
                "--end-year", str(end_year),
                "--sample-per-year", str(sample_per_year),
                "--start-from", start_from
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.base_path,
                capture_output=True, 
                text=True, 
                check=True
            )
            
            return {
                "status": "success",
                "message": "Core pipeline completed successfully",
                "step1_output": str(self.outputs_dir / "step1_retrieved.csv"),
                "step2_output": str(self.outputs_dir / "step2_filtered.csv"),
                "step3_output": str(self.outputs_dir / "step3_extracted.csv"),
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Pipeline failed: {e}",
                "stdout": e.stdout,
                "stderr": e.stderr
            }
            
    def run_full_pipeline(self,
                         keywords: str = "depression OR anxiety", 
                         start_year: int = 2020,
                         end_year: int = 2024,
                         sample_per_year: int = 100,
                         skip_split: bool = False,
                         skip_qa: bool = False,
                         start_from: str = "retrieve") -> Dict[str, str]:
        """
        Run the full pipeline with optional steps
        
        Args:
            keywords: Research keywords to search for
            start_year: Start year for paper retrieval
            end_year: End year for paper retrieval
            sample_per_year: Number of papers to sample per year
            skip_split: Whether to skip the split step
            skip_qa: Whether to skip the QA generation step
            start_from: Step to start from ('retrieve', 'classify', 'extract')
            
        Returns:
            Dict with status and output file paths
        """
        try:
            cmd = [
                sys.executable, "run.py", "pipeline",
                "--keywords", keywords,
                "--start-year", str(start_year),
                "--end-year", str(end_year), 
                "--sample-per-year", str(sample_per_year),
                "--start-from", start_from
            ]
            
            if skip_split:
                cmd.append("--skip-split")
            if skip_qa:
                cmd.append("--skip-qa")
                
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            output_files = {
                "status": "success",
                "message": "Full pipeline completed successfully",
                "step1_output": str(self.outputs_dir / "step1_retrieved.csv"),
                "step2_output": str(self.outputs_dir / "step2_filtered.csv"), 
                "step3_output": str(self.outputs_dir / "step3_extracted.csv"),
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Add optional outputs if they exist
            if not skip_split and (self.outputs_dir / "step3_split.csv").exists():
                output_files["step3b_output"] = str(self.outputs_dir / "step3_split.csv")
                
            if not skip_qa:
                if (self.outputs_dir / "step4_qa.csv").exists():
                    output_files["step4_output"] = str(self.outputs_dir / "step4_qa.csv")
                if (self.outputs_dir / "qa_bank.csv").exists():
                    output_files["qa_bank_output"] = str(self.outputs_dir / "qa_bank.csv")
                    
            return output_files
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Pipeline failed: {e}",
                "stdout": e.stdout,
                "stderr": e.stderr
            }
    
    def get_extracted_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Get the extracted clinical data (Step 3 output)
        This is the main output for integration with other agents
        
        Args:
            file_path: Custom path to extracted data file. If None, uses default step3 output.
            
        Returns:
            DataFrame with extracted clinical data
        """
        if file_path is None:
            file_path = self.outputs_dir / "step3_extracted.csv"
        else:
            file_path = Path(file_path)
            
        if not file_path.exists():
            raise FileNotFoundError(f"Extracted data file not found: {file_path}")
            
        return pd.read_csv(file_path)
    
    def get_qa_bank(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Get the generated Q&A knowledge base
        
        Args:
            file_path: Custom path to QA bank file. If None, uses default output.
            
        Returns:
            DataFrame with Q&A pairs
        """
        if file_path is None:
            file_path = self.outputs_dir / "qa_bank.csv"
        else:
            file_path = Path(file_path)
            
        if not file_path.exists():
            raise FileNotFoundError(f"QA bank file not found: {file_path}")
            
        return pd.read_csv(file_path)
    
    def get_pipeline_status(self) -> Dict[str, bool]:
        """
        Check which pipeline outputs are available
        
        Returns:
            Dict indicating which output files exist
        """
        return {
            "step1_retrieved": (self.outputs_dir / "step1_retrieved.csv").exists(),
            "step2_filtered": (self.outputs_dir / "step2_filtered.csv").exists(),
            "step3_extracted": (self.outputs_dir / "step3_extracted.csv").exists(),
            "step3_split": (self.outputs_dir / "step3_split.csv").exists(),
            "step4_qa": (self.outputs_dir / "step4_qa.csv").exists(),
            "qa_bank": (self.outputs_dir / "qa_bank.csv").exists()
        }
    
    def export_data_for_agent(self, output_format: str = "json") -> Union[str, Dict]:
        """
        Export extracted clinical data in format suitable for other agents
        
        Args:
            output_format: Format for export ('json', 'dict', 'csv_path')
            
        Returns:
            Exported data in requested format
        """
        try:
            df = self.get_extracted_data()
            
            if output_format == "json":
                return df.to_json(orient="records")
            elif output_format == "dict":
                return df.to_dict(orient="records")
            elif output_format == "csv_path":
                return str(self.outputs_dir / "step3_extracted.csv")
            else:
                raise ValueError(f"Unsupported format: {output_format}")
                
        except FileNotFoundError:
            return None
    
    def get_summary_stats(self) -> Dict[str, int]:
        """
        Get summary statistics for the current pipeline outputs
        
        Returns:
            Dict with counts for each pipeline step
        """
        stats = {}
        
        for step, filename in [
            ("retrieved_papers", "step1_retrieved.csv"),
            ("filtered_papers", "step2_filtered.csv"), 
            ("extracted_papers", "step3_extracted.csv"),
            ("split_fields", "step3_split.csv"),
            ("qa_pairs", "qa_bank.csv")
        ]:
            file_path = self.outputs_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    stats[step] = len(df)
                except:
                    stats[step] = 0
            else:
                stats[step] = 0
                
        return stats

# Convenience functions for direct usage
def run_clinical_research_pipeline(keywords: str = "depression OR anxiety",
                                 start_year: int = 2020,
                                 end_year: int = 2024,
                                 sample_per_year: int = 100,
                                 mode: str = "core") -> Dict[str, str]:
    """
    Convenience function to run the clinical research pipeline
    
    Args:
        keywords: Research keywords
        start_year: Start year for search
        end_year: End year for search  
        sample_per_year: Papers per year to sample
        mode: 'core' for 3 steps, 'full' for all steps
        
    Returns:
        Pipeline execution results
    """
    agent = ClinicalResearchAgent()
    
    if mode == "core":
        return agent.run_core_pipeline(keywords, start_year, end_year, sample_per_year)
    elif mode == "full":
        return agent.run_full_pipeline(keywords, start_year, end_year, sample_per_year)
    else:
        raise ValueError("Mode must be 'core' or 'full'")

def get_clinical_data_for_agent(base_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Convenience function to get extracted clinical data for other agents
    
    Args:
        base_path: Path to the clinical research agent directory
        
    Returns:
        DataFrame with extracted clinical data, or None if not available
    """
    try:
        agent = ClinicalResearchAgent(base_path)
        return agent.get_extracted_data()
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    # Example usage
    agent = ClinicalResearchAgent()
    
    # Run core pipeline
    result = agent.run_core_pipeline(
        keywords="bipolar disorder",
        start_year=2022,
        end_year=2024,
        sample_per_year=50
    )
    
    print("Pipeline Result:", result)
    
    # Get extracted data
    if result["status"] == "success":
        data = agent.get_extracted_data()
        print(f"Extracted {len(data)} papers with clinical data")
        
        # Export for other agents
        json_data = agent.export_data_for_agent("json")
        print("Data exported for integration")
        
        # Get summary
        stats = agent.get_summary_stats()
        print("Pipeline stats:", stats)