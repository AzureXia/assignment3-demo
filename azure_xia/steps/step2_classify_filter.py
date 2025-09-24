import re, json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from agents.amplify_client import AmplifyClient

# --- helpers ---------------------------------------------------------------

def _safe_text(x):
    return "" if pd.isna(x) else str(x)

import re, json

def _parse_llm_json(resp: str, wanted_keys: tuple) -> dict:
    """
    Find the FIRST JSON object in the response. If the top-level object doesn't
    contain the wanted keys, recursively search nested dict/list/string fields,
    including strings that themselves contain JSON (e.g., data.text = "{...}").
    Returns {} if nothing usable is found.
    """
    if not isinstance(resp, str):
        try:
            resp = json.dumps(resp)
        except Exception:
            resp = str(resp)

    def _first_json_obj(s: str):
        s = s.strip()
        if s.startswith("```"):
            s = "\n".join(line for line in s.splitlines() if not line.strip().startswith("```"))
        m = re.search(r"\{.*\}", s, re.S)
        return json.loads(m.group(0)) if m else None

    def _find(obj):
        # Direct hit
        if isinstance(obj, dict):
            # Have what we want?
            if any(k in obj for k in wanted_keys):
                return obj
            # Search children
            for v in obj.values():
                res = _find(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for v in obj:
                res = _find(v)
                if res:
                    return res
        elif isinstance(obj, str):
            inner = _first_json_obj(obj)
            if inner:
                res = _find(inner)
                if res:
                    return res
        return None

    # start with outer JSON if present; otherwise scan the raw text
    outer = _first_json_obj(resp)
    if outer:
        found = _find(outer)
        if found:
            return found
    found = _find(resp)
    return found or {}

# def _parse_json_any(s: str) -> dict:
#     """
#     Extract the first {...} JSON object from a string (handles code fences and extra text).
#     Raises ValueError if no JSON object found.
#     """
#     s = (s or "").strip()
#     # strip code fences if present
#     if s.startswith("```"):
#         s = "\n".join(line for line in s.splitlines() if not line.strip().startswith("```"))
#     m = re.search(r"\{.*\}", s, re.S)
#     if not m:
#         raise ValueError("no JSON object found")
#     return json.loads(m.group(0))

def _coerce_label_from_text(s: str) -> str:
    """Fallback: pull YES/NO/UNCERTAIN from messy text."""
    s = (s or "").lower()
    m = re.search(r'\b(label)\b[^a-z0-9]*(yes|no|uncertain)\b', s)
    if m:
        return m.group(2).upper()
    # Soft fallback: if it clearly says it's relevant / not relevant
    if "yes" in s or "relevant" in s:
        return "YES"
    if "no" in s or "irrelevant" in s:
        return "NO"
    return "UNCERTAIN"

# --- prompts ---------------------------------------------------------------
# --- CDA-focused prompts  ---

SYSTEM = (
    "You are an AI assistant that determines whether an abstract truly focuses "
    "on clinical depression/anxiety research. You should answer \"YES\", \"NO\", or \"UNCERTAIN\"."
)

USER_TMPL = """Instruction:
1. Read the provided abstract carefully.
2. Decide if it primarily discusses depression or anxiety in a medical or clinical sense.
3. If you are not certain or the abstract is borderline, answer "UNCERTAIN".
4. Otherwise, answer YES or NO strictly.

Examples:
Example 1
Abstract: "We investigate a novel antidepressant in patients with major depressive disorder..."
Gold Answer: YES

Example 2
Abstract: "We analyze ways to store carbon in soil to mitigate climate change..."
Gold Answer: NO

Example 3
Abstract: "Exploring the link between anxiety symptoms and cortisol levels in adolescents..."
Gold Answer: YES

Now classify this new article:
Abstract: "{abstract}"
PMID: {pmid}
Title: {title}
Final answer (YES/NO/UNCERTAIN):"""

REQUIRED_COLS = ["pmid","title","abstract","date","journal","publication_type","year"]

# --- core ------------------------------------------------------------------

KEYWORDS = re.compile(r"\b(depress|anxiet|mdd|gad|panic|phobia)\b", re.I)

def classify_row(client: AmplifyClient, row, topic: str):
    pmid     = _safe_text(row.get("pmid", ""))
    title    = _safe_text(row.get("title", ""))
    abstract = _safe_text(row.get("abstract", ""))[:6000]

    # 1) main CDA prompt
    user = USER_TMPL.format(pmid=pmid, title=title, abstract=abstract)
    resp = client.chat(
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":user}],
        temperature=0.1, max_tokens=160
    )

    # try to extract YES/NO/UNCERTAIN from response
    try:
        label = resp.strip().upper()
        if "YES" in label:
            label = "YES"
        elif "NO" in label:
            label = "NO"
        elif "UNCERTAIN" in label:
            label = "UNCERTAIN"
        else:
            label = ""
    except Exception:
        label = ""

    # 2) force-JSON retry if needed
    if label not in ("YES","NO","UNCERTAIN"):
        resp2 = client.chat(
            messages=[
                {"role":"system","content":"Return only YES, NO, or UNCERTAIN."},
                {"role":"user","content":f"Title: {title}\nAbstract: {abstract[:2000]}"}],
            temperature=0, max_tokens=80
        )
        try:
            label = resp2.strip().upper()
            if "YES" in label:
                label = "YES"
            elif "NO" in label:
                label = "NO"  
            elif "UNCERTAIN" in label:
                label = "UNCERTAIN"
        except Exception:
            pass

    # 3) last-resort heuristic so you don't end up with all UNCERTAIN
    if label not in ("YES","NO","UNCERTAIN"):
        text = f"{title} {abstract}".lower()
        label = "YES" if KEYWORDS.search(text) else "NO"

    return label

def run_classify_filter(input_csv: str, out_csv: str,
                        topic: str = "clinical depression OR clinical anxiety",
                        prompt_pack: str = "generic"):   # prompt_pack accepted for compatibility
    df = pd.read_csv(input_csv)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            raise SystemExit(f"Missing required column '{c}' in {input_csv}")

    df["classification"] = ""

    client = AmplifyClient()
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Classify"):
        label = classify_row(client, row, topic)
        df.at[i, "classification"] = label

    kept = df[df["classification"] == "YES"].copy()

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    kept.to_csv(out_csv, index=False)

    # Helpful summary in console
    counts = df["classification"].value_counts(dropna=False).to_dict()
    print(f"Wrote {out_csv}  (kept {len(kept)} of {len(df)})")
    print("Classify breakdown:", counts)
