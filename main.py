import os
import glob
import time
from dotenv import load_dotenv

from extractors.pdf_parser import extract_text_from_pdf
from services.llm_service import parse_invoice_with_llm
from pipelines.data_cleaner import flatten_invoices_to_dataframe, export_to_excel

def main():
    # Load environment variables (GEMINI_API_KEY)
    load_dotenv()
    
    input_dir = "data/raw_pdfs"
    output_dir = "data/output"
    error_log = "data/errors.txt"
    output_excel = os.path.join(output_dir, "cleaned_invoices.xlsx")
    
    # Get all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {input_dir}. Please add some files and try again.")
        return
        
    print(f"Found {len(pdf_files)} PDFs to process.")
    
    parsed_invoices = []
    errors = []
    
    try:
        for idx, pdf_path in enumerate(pdf_files, 1):
            filename = os.path.basename(pdf_path)
            print(f"[{idx}/{len(pdf_files)}] Processing {filename}...")
            
            try:
                # 1. Extract raw text
                raw_text = extract_text_from_pdf(pdf_path)
                
                if not raw_text.strip():
                    raise ValueError("Extracted text is empty. PDF might be a scanned image without OCR.")
                    
                # 2. Parse text with LLM
                invoice = parse_invoice_with_llm(raw_text)

                # Skip invoices where critical fields are missing (corrupt/blank PDFs)
                if not invoice.order_id or not invoice.customer_name:
                    raise ValueError(
                        f"Parsed invoice is missing critical fields (order_id={invoice.order_id}, "
                        f"customer_name={invoice.customer_name}). PDF may be corrupt or blank."
                    )

                parsed_invoices.append(invoice)
                
                # (15 requests per minute limit on free tier)
                time.sleep(4)
                
            except Exception as e:
                error_msg = f"Failed to process {filename}: {str(e)}"
                print(f"ERROR: {error_msg}")
                errors.append(error_msg)
                
                # Log error immediately
                with open(error_log, "a") as f:
                    f.write(f"{error_msg}\n")
    except KeyboardInterrupt:
        print("\n\n[!] Process manually interrupted by user (Ctrl+C). Saving progress so far...")
                
    # 3. Clean, flatten and export
    if parsed_invoices:
        print(f"\nSuccessfully parsed {len(parsed_invoices)} invoices. Exporting to Excel...")
        df = flatten_invoices_to_dataframe(parsed_invoices)
        export_to_excel(df, output_excel)
    else:
        print("\nNo invoices were successfully parsed.")
        
    if errors:
        print(f"\nEncountered {len(errors)} errors. Check {error_log} for details.")

if __name__ == "__main__":
    main()
