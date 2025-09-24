import random, time, csv
from pathlib import Path
from tqdm import tqdm
from Bio import Entrez

def _fmt_date(pubdate: dict, fallback_year: int) -> str:
    y = pubdate.get("Year")
    m = pubdate.get("Month", "")
    d = pubdate.get("Day", "")
    if not y:
        y = str(fallback_year)
    parts = [y]
    if m: parts.append(m)
    if d: parts.append(d if len(d) == 2 else d)
    return "-".join(parts)

def retrieve_pubmed_sampled(keywords: str, start_year: int, end_year: int, sample_per_year: int, email: str, api_key: str, out_path: str):
    """
    For each year in [start_year, end_year], run ESearch → random sample (sample_per_year) → EFetch details,
    and write a CSV with EXACT columns: pmid,title,abstract,date,journal,publication_type,year.
    """
    if email:
        Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

    rows = []
    for year in range(start_year, end_year + 1):
        term = f'({keywords}) AND ("{year}/01/01"[PDAT] : "{year}/12/31"[PDAT])'
        handle = Entrez.esearch(db="pubmed", term=term, retmax=50000)
        rec = Entrez.read(handle)
        handle.close()
        pmids = rec.get("IdList", [])
        if not pmids:
            continue
        if len(pmids) > sample_per_year:
            import random as _r
            pmids = _r.sample(pmids, sample_per_year)

        batch = 200
        for i in tqdm(range(0, len(pmids), batch), desc=f"Year {year}: fetching"):
            sub = pmids[i:i+batch]
            h = Entrez.efetch(db="pubmed", id=sub, retmode="xml")
            data = Entrez.read(h)
            h.close()
            for art in data["PubmedArticle"]:
                mc = art.get("MedlineCitation", {})
                artinfo = mc.get("Article", {})
                title = artinfo.get("ArticleTitle", "")
                abstract = " ".join(artinfo.get("Abstract", {}).get("AbstractText", []))
                journal = (artinfo.get("Journal", {}).get("Title") or "")
                pubdate = artinfo.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                date_str = _fmt_date(pubdate, fallback_year=year)
                pmid = str(mc.get("PMID", ""))

                # Publication type: keep a concise text; if not available, default to "Journal Article"
                pt_list = mc.get("PublicationTypeList") or []
                pt_text = ";".join([str(x) for x in pt_list]).strip(";") or "Journal Article"

                rows.append({
                    "pmid": int(pmid) if pmid.isdigit() else pmid,
                    "title": title,
                    "abstract": abstract,
                    "date": date_str,
                    "journal": journal,
                    "publication_type": pt_text,
                    "year": int(pubdate.get("Year", year)) if str(pubdate.get("Year", year)).isdigit() else year,
                })
            time.sleep(0.34)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["pmid","title","abstract","date","journal","publication_type","year"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k,"") for k in fields})
    print(f"Wrote {out}")
