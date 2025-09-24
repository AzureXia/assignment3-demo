import argparse
# from steps.step1_retrieve_pubmed import retrieve_pubmed_sampled
from steps.step2_classify_filter import run_classify_filter
from steps.step3_extract_schema import run_extract_schema
from steps.step3b_split_fields import run_split_fields
from steps.step4_generate_qa import run_generate_qa

def main():
    p = argparse.ArgumentParser(description="KB Pipeline — retrieve → classify → extract → [optional: split/QA]")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Add core pipeline command (essential 3 steps)
    p_core = sub.add_parser("core", help="Run core pipeline (retrieve → classify → extract)")
    p_core.add_argument("--keywords", default="clinical depression OR anxiety", help="Query keywords (default: 'clinical depression OR anxiety')")
    p_core.add_argument("--start-year", type=int, default=2020, help="Start year (default 2020)")
    p_core.add_argument("--end-year", type=int, default=2024, help="End year (default 2024)")
    p_core.add_argument("--sample-per-year", type=int, default=100, help="Random sample count per year (default 100)")
    p_core.add_argument("--email", default="", help="Entrez email (optional)")
    p_core.add_argument("--api-key", dest="entrez_api_key", default=None, help="Entrez API key (optional)")
    p_core.add_argument("--start-from", choices=["retrieve", "classify", "extract"], default="retrieve", help="Start pipeline from this step")

    # Add full pipeline command (all 5 steps with optional control)
    p_full = sub.add_parser("pipeline", help="Run full pipeline with optional steps (all 5 steps)")
    p_full.add_argument("--keywords", default="clinical depression OR anxiety", help="Query keywords (default: 'clinical depression OR anxiety')")
    p_full.add_argument("--start-year", type=int, default=2020, help="Start year (default 2020)")
    p_full.add_argument("--end-year", type=int, default=2024, help="End year (default 2024)")
    p_full.add_argument("--sample-per-year", type=int, default=100, help="Random sample count per year (default 100)")
    p_full.add_argument("--email", default="", help="Entrez email (optional)")
    p_full.add_argument("--api-key", dest="entrez_api_key", default=None, help="Entrez API key (optional)")
    p_full.add_argument("--skip-split", action="store_true", help="Skip the split step (step3b)")
    p_full.add_argument("--skip-qa", action="store_true", help="Skip the QA generation step (step4)")
    p_full.add_argument("--start-from", choices=["retrieve", "classify", "extract"], default="retrieve", help="Start pipeline from this step")

    p1 = sub.add_parser("retrieve", help="Retrieve PubMed by year with per-year sampling")
    p1.add_argument("--keywords", default="clinical depression OR anxiety", help="Query keywords (default: 'clinical depression OR anxiety')")
    p1.add_argument("--start-year", type=int, default=2020, help="Start year (default 2020)")
    p1.add_argument("--end-year", type=int, default=2024, help="End year (default 2024)")
    p1.add_argument("--sample-per-year", type=int, default=100, help="Random sample count per year (default 100)")
    p1.add_argument("--email", default="", help="Entrez email (optional)")
    p1.add_argument("--api-key", dest="entrez_api_key", default=None, help="Entrez API key (optional)")
    p1.add_argument("--out", default="outputs/step1_retrieved.csv")

    p2 = sub.add_parser("classify", help="Classify and filter (Amplify)")
    p2.add_argument("--input", required=True, help="Input CSV (defaults to Step 1 output)")
    p2.add_argument("--out", default="outputs/step2_filtered.csv")

    p3 = sub.add_parser("extract", help="Extract schema fields (Amplify)")
    p3.add_argument("--input", required=True, help="Input CSV (defaults to Step 2 output)")
    p3.add_argument("--out", default="outputs/step3_extracted.csv")

    p3b = sub.add_parser("split", help="[OPTIONAL] Split GPT output into structured fields")
    p3b.add_argument("--input", required=True, help="Input CSV with gpt_output column")
    p3b.add_argument("--out", default="outputs/step3_split.csv")

    p4 = sub.add_parser("qa", help="[OPTIONAL] Generate one QA per abstract (Amplify)")
    p4.add_argument("--input", required=True, help="Input CSV (defaults to Step 3 output)")
    p4.add_argument("--out", default="outputs/step4_qa.csv")
    p4.add_argument("--qa-bank", default="outputs/qa_bank.csv")

    args = p.parse_args()

    if args.cmd == "core":
        print("🔄 Starting core pipeline (3 essential steps)...")
        
        # Step 1: Retrieve (if starting from retrieve)
        if args.start_from == "retrieve":
            print("📚 Step 1: Retrieving papers from PubMed...")
            from steps.step1_retrieve_pubmed import retrieve_pubmed_sampled
            retrieve_pubmed_sampled(args.keywords, args.start_year, args.end_year, args.sample_per_year, args.email, args.entrez_api_key, "outputs/step1_retrieved.csv")
            current_input = "outputs/step1_retrieved.csv"
        elif args.start_from == "classify":
            current_input = "outputs/step1_retrieved.csv"
        elif args.start_from == "extract":
            current_input = "outputs/step2_filtered.csv"
        
        # Step 2: Classify (if starting from retrieve or classify)
        if args.start_from in ["retrieve", "classify"]:
            print("🔍 Step 2: Classifying and filtering papers...")
            run_classify_filter(current_input, "outputs/step2_filtered.csv")
            current_input = "outputs/step2_filtered.csv"
        
        # Step 3: Extract (always run for core pipeline)
        print("📊 Step 3: Extracting clinical data...")
        run_extract_schema(current_input, "outputs/step3_extracted.csv")
        
        print("✅ Core pipeline completed! (3 steps)")
        print("💡 To run optional steps: python run.py split/qa --input outputs/step3_extracted.csv")
        
    elif args.cmd == "pipeline":
        print("🔄 Starting full pipeline (all 5 steps with optional control)...")
        
        # Step 1: Retrieve (if starting from retrieve)
        if args.start_from == "retrieve":
            print("📚 Step 1: Retrieving papers from PubMed...")
            from steps.step1_retrieve_pubmed import retrieve_pubmed_sampled
            retrieve_pubmed_sampled(args.keywords, args.start_year, args.end_year, args.sample_per_year, args.email, args.entrez_api_key, "outputs/step1_retrieved.csv")
            current_input = "outputs/step1_retrieved.csv"
        elif args.start_from == "classify":
            current_input = "outputs/step1_retrieved.csv"
        elif args.start_from == "extract":
            current_input = "outputs/step2_filtered.csv"
        
        # Step 2: Classify (if starting from retrieve or classify)
        if args.start_from in ["retrieve", "classify"]:
            print("🔍 Step 2: Classifying and filtering papers...")
            run_classify_filter(current_input, "outputs/step2_filtered.csv")
            current_input = "outputs/step2_filtered.csv"
        
        # Step 3: Extract (always run if pipeline command is used)
        print("📊 Step 3: Extracting clinical data...")
        run_extract_schema(current_input, "outputs/step3_extracted.csv")
        current_input = "outputs/step3_extracted.csv"
        
        # Step 3b: Split (optional)
        if not args.skip_split:
            print("✂️  Step 3b: Splitting structured fields...")
            run_split_fields(current_input, "outputs/step3_split.csv")
            current_input = "outputs/step3_split.csv"
        else:
            print("⏭️  Skipping Step 3b (split)")
        
        # Step 4: QA Generation (optional)
        if not args.skip_qa:
            print("❓ Step 4: Generating Q&A pairs...")
            run_generate_qa(current_input, "outputs/step4_qa.csv", "outputs/qa_bank.csv")
        else:
            print("⏭️  Skipping Step 4 (QA generation)")
        
        print("✅ Pipeline completed!")
        
    elif args.cmd == "retrieve":
        from steps.step1_retrieve_pubmed import retrieve_pubmed_sampled
        retrieve_pubmed_sampled(args.keywords, args.start_year, args.end_year, args.sample_per_year, args.email, args.entrez_api_key, args.out)
    elif args.cmd == "classify":
        run_classify_filter(args.input, args.out)
    elif args.cmd == "extract":
        run_extract_schema(args.input, args.out)
    elif args.cmd == "split":
        run_split_fields(args.input, args.out)
    elif args.cmd == "qa":
        run_generate_qa(args.input, args.out, args.qa_bank)

if __name__ == "__main__":
    main()
