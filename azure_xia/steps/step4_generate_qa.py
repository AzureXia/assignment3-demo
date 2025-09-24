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
    """Unwrap nested responses and return the first dict containing any of wanted_keys."""
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

# ---------- prompts (CDA-oriented, strict JSON) ----------
SYSTEM = (
    "You are a board-certified psychiatrist who writes exam questions."
)

USER_TMPL = """ABSTRACT
--------
{abstract}

TASK
----
Create **one** stand-alone short-answer question a licensed psychiatrist 
should be able to answer **without seeing the abstract**, yet whose
correct answer is fully grounded in the abstract's content.

Constraints
• Topic must involve clinical depression disorders or clinical anxiety disorders. 
• Difficulty level ≥ "hard" (non-trivial clinical reasoning).
• Do **not** refer to "this passage", "the abstract", authors, journal,
  year, tables, or figures. 
• The question must be solvable solely from this abstract.

Output JSON **exactly** in this schema:
{{
  "type": "sa",
  "question": "...?",
  "answer": "≤50-word key answer",
  "explanation": "≤50-word justification grounded in the abstract"
}}"""

REQUIRED_COLS = ["pmid","title","abstract","date","journal","publication_type","year","classification"]

# ---------- core ----------
def run_generate_qa(input_csv: str, out_csv: str, qa_bank_csv: str):
    df = pd.read_csv(input_csv)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            raise SystemExit(f"Missing required column '{c}' in {input_csv}")

    client = AmplifyClient()
    df["qa_type"] = "sa"
    df["qa_question"] = ""
    df["qa_answer"] = ""
    df["qa_explanation"] = ""

    bank_rows = []  # QA-only export (no pmid)

    for i, row in tqdm(df.iterrows(), total=len(df), desc="QA"):
        pmid     = _safe_text(row.get("pmid",""))
        title    = _safe_text(row.get("title",""))
        abstract = _safe_text(row.get("abstract",""))[:6000]

        # Attempt 1
        resp = client.chat(
            messages=[{"role":"system","content":SYSTEM},
                      {"role":"user","content":USER_TMPL.format(abstract=abstract)}],
            temperature=0.5, max_tokens=800
        )
        data = _parse_llm_json(resp, wanted_keys=("type","question","answer","explanation"))

        # Attempt 2 (force-JSON) if needed
        if not data:
            resp2 = client.chat(
                messages=[
                    {"role":"system","content":"Return ONLY JSON with keys type,question,answer,explanation."},
                    {"role":"user","content":f"Abstract: {abstract[:2000]}"}],
                temperature=0, max_tokens=400
            )
            data = _parse_llm_json(resp2, wanted_keys=("type","question","answer","explanation")) or {}

        q = data.get("question",""); a = data.get("answer",""); e = data.get("explanation","")
        df.at[i, "qa_question"]    = q
        df.at[i, "qa_answer"]      = a
        df.at[i, "qa_explanation"] = e

        if q:
            bank_rows.append({
                "qa_type": "sa",
                "qa_question": q,
                "qa_answer": a,
                "qa_explanation": e
            })

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    if bank_rows:
        pd.DataFrame(bank_rows, columns=["qa_type","qa_question","qa_answer","qa_explanation"]).to_csv(qa_bank_csv, index=False)

    print(f"Wrote {out_csv}")
    print(f"Wrote {qa_bank_csv}")
