import json, re
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from agents.amplify_client import AmplifyClient

# ---------- helpers ----------
def _safe_text(x):
    return "" if pd.isna(x) else str(x)

def _first_json_obj(s: str):
    """Find and load the first balanced {...} object inside a string."""
    if not isinstance(s, str):
        try:
            s = json.dumps(s)
        except Exception:
            s = str(s)
    # strip code fences if present
    if s.strip().startswith("```"):
        s = "\n".join(line for line in s.splitlines() if not line.strip().startswith("```"))

    start = s.find("{")
    while start != -1:
        depth = 0
        for i, ch in enumerate(s[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    segment = s[start:i+1]
                    try:
                        return json.loads(segment)
                    except Exception:
                        break
        start = s.find("{", start + 1)
    return None

def _parse_llm_json(resp: str, wanted_keys: tuple) -> dict:
    """
    Unwrap nested responses and return the first dict containing any of wanted_keys.
    Handles strings-with-JSON, dict/list wrappers, and nested 'data.text' shapes.
    """
    def _find(obj):
        if isinstance(obj, dict):
            if any(k in obj for k in wanted_keys):
                return obj
            for v in obj.values():
                hit = _find(v)
                if hit: return hit
        elif isinstance(obj, list):
            for v in obj:
                hit = _find(v)
                if hit: return hit
        elif isinstance(obj, str):
            inner = _first_json_obj(obj)
            if inner:
                hit = _find(inner)
                if hit: return hit
        return None

    outer = _first_json_obj(resp)
    if outer:
        hit = _find(outer)
        if hit: return hit
    hit = _find(resp)
    return hit or {}

# ---------- prompts (high-quality chain-of-thought extraction) ----------
SYSTEM = (
    "You are an AI assistant that reads an abstract about depression or anxiety. "
    "Your goal is to extract key cause/effect relationships (risk factors), identify the population studied, "
    "and highlight any relevant interventions (treatments), and outcomes."
)

USER_TMPL = """Specifically:
1. Summarize the main findings:
   - For depression/anxiety, what does the article claim are the causes, triggers, or risk factors?
   - Who is the population or demographic in focus (e.g. adolescents, older adults, postpartum, etc.)?
   - What interventions or treatments are mentioned, if any?
   - What outcomes or effects are measured?
2. Explain your reasoning step by step in a chain-of-thought style, so it's clear how you arrived at your summary.
3. If the abstract does not mention some parts (e.g., no specific population or intervention), just say so.

Here is the abstract:
\"\"\"{abstract}\"\"\"

Please provide a short structured summary, then provide your reasoning step by step as a chain of thought."""

REQUIRED_COLS = ["pmid","title","abstract","date","journal","publication_type","year","classification"]

# ---------- core ----------
def extract_row(client: AmplifyClient, row):
    pmid     = _safe_text(row.get("pmid",""))
    title    = _safe_text(row.get("title",""))
    abstract = _safe_text(row.get("abstract",""))[:6000]

    # High-quality chain-of-thought extraction (like your original prompt)
    resp = client.chat(
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":USER_TMPL.format(abstract=abstract)}],
        temperature=0.2, max_tokens=800
    )
    
    # Store the full GPT response instead of trying to parse it into simple keywords
    return {"gpt_output": resp}

def run_extract_schema(input_csv: str, out_csv: str):
    df = pd.read_csv(input_csv)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            raise SystemExit(f"Missing required column '{c}' in {input_csv}")

    client = AmplifyClient()
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Extract"):
        data = extract_row(client, row)
        df.at[i, "gpt_output"] = data.get("gpt_output","")

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv}")
