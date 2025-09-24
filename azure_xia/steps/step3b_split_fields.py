"""
GPT Output Field Splitter for Clinical Depression/Anxiety Research
Extracts structured fields from the gpt_output column containing:
- Population
- Risk Factors  
- Treatments/Interventions
- Outcomes
"""

import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm

def _safe_text(x):
    return "" if pd.isna(x) else str(x)

class ClinicalFieldSplitter:
    """Splits the gpt_output field into structured clinical components."""
    
    def __init__(self):
        """Initialize the splitter with field patterns."""
        self.field_patterns = {
            'population': [
                r'(?i)(?:population|participants?|subjects?|cohort|demographic).*?(?:focus|in focus|studied|examined):?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|For|What|$)',
                r'(?i)\*\*(?:population|participants?|subjects?|cohort|demographic).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|For|What|$)',
                r'(?i)(?:who is the|population or demographic in focus).*?:?\s*[-]?\s*(.+?)(?=\n|\*\*|For|What|$)'
            ],
            'risk_factors': [
                r'(?i)(?:risk factors?|causes?|triggers?|predictors?).*?:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|Who|What|$)',
                r'(?i)\*\*(?:risk factors?|causes?|triggers?|predictors?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|Who|What|$)',
                r'(?i)(?:what does the article claim are the|causes, triggers, or risk factors).*?:?\s*[-]?\s*(.+?)(?=\n|\*\*|Who|What|$)'
            ],
            'treatments': [
                r'(?i)(?:treatments?|interventions?|therapies?|management|approaches?).*?:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|What|$)',
                r'(?i)\*\*(?:treatments?|interventions?|therapies?|management|approaches?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|What|$)',
                r'(?i)(?:what interventions or treatments).*?:?\s*[-]?\s*(.+?)(?=\n|\*\*|What|$)'
            ],
            'outcomes': [
                r'(?i)(?:outcomes?|results?|effects?|findings?|measured).*?:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|Explain|$)',
                r'(?i)\*\*(?:outcomes?|results?|effects?|findings?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|Explain|$)',
                r'(?i)(?:what outcomes or effects are measured).*?:?\s*[-]?\s*(.+?)(?=\n|\*\*|Explain|$)'
            ]
        }
    
    def extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field from GPT output text."""
        if not text or field_name not in self.field_patterns:
            return ""
        
        # Try each pattern for the field
        for pattern in self.field_patterns[field_name]:
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                extracted = match.group(1).strip()
                # Clean up the extracted text
                extracted = re.sub(r'\n+', ' ', extracted)
                extracted = re.sub(r'\s+', ' ', extracted)
                extracted = extracted.strip('- ')
                if extracted and len(extracted) > 5:  # Minimum meaningful length
                    return extracted
        
        return ""
    
    def extract_all_fields(self, gpt_output: str) -> dict:
        """Extract all fields from a single GPT output."""
        result = {}
        for field_name in self.field_patterns.keys():
            result[field_name] = self.extract_field(gpt_output, field_name)
        return result

def run_split_fields(input_csv: str, out_csv: str):
    """Split GPT output into structured fields."""
    df = pd.read_csv(input_csv)
    
    if 'gpt_output' not in df.columns:
        raise SystemExit(f"Missing required column 'gpt_output' in {input_csv}")
    
    splitter = ClinicalFieldSplitter()
    
    # Initialize new columns
    df["population"] = ""
    df["risk_factors"] = ""
    df["treatments"] = ""
    df["outcomes"] = ""
    
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Split fields"):
        gpt_output = _safe_text(row.get("gpt_output", ""))
        if gpt_output:
            fields = splitter.extract_all_fields(gpt_output)
            df.at[i, "population"] = fields.get("population", "")
            df.at[i, "risk_factors"] = fields.get("risk_factors", "")
            df.at[i, "treatments"] = fields.get("treatments", "")
            df.at[i, "outcomes"] = fields.get("outcomes", "")
    
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv}")