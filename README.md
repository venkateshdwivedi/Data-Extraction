# 📄 PDF to Excel Extraction Pipeline

An intelligent, production-grade batch pipeline that extracts structured data from invoice PDFs and exports it to a clean Excel spreadsheet — powered by **Groq AI** and **Llama/GPT inference**.

---
## Features

- **Batch Processing** — Processes hundreds of PDF invoices in a single run
- **AI-Powered Extraction** — Uses Groq's `openai/gpt-oss-20b` model to intelligently parse unstructured invoice text into structured data
- **Strict Schema Enforcement** — Pydantic models guarantee every output row has the correct fields and data types
- **Rate Limit Resilient** — Exponential backoff retry logic (via `tenacity`) handles API rate limits automatically
- **Fault Tolerant** — A single corrupt or blank PDF never crashes the batch; errors are logged to `data/errors.txt` and processing continues
- **Safe Interruption** — Press `Ctrl+C` at any time to safely stop the run and save all progress collected so far to Excel

---

##  Architecture

```
PDF File
   │
   ▼
┌─────────────────────────┐
│   pdf_parser.py         │  pdfplumber extracts raw text from all pages
│   (extractors/)         │
└──────────┬──────────────┘
           │  raw text string
           ▼
┌─────────────────────────┐
│   llm_service.py        │  Groq API (openai/gpt-oss-20b)
│   (services/)           │  System prompt + Pydantic JSON schema
│                         │  → returns structured JSON
└──────────┬──────────────┘
           │  validated Invoice object (Pydantic)
           ▼
┌─────────────────────────┐
│   data_cleaner.py       │  Flattens nested line items into rows
│   (pipelines/)          │  Normalizes dates and data types
└──────────┬──────────────┘
           │  pandas DataFrame
           ▼
    cleaned_invoices.xlsx
```

---

##  Project Structure

```
pdf-extraction/
├── main.py                  # Main orchestrator — run this
├── requirements.txt         # Python dependencies
├── .env                     # API keys (never commit this)
├── .gitignore
│
├── data/
│   ├── raw_pdfs/            # Drop your invoice PDFs here
│   ├── output/              # cleaned_invoices.xlsx is saved here
│   └── errors.txt           # Auto-generated log of failed files
│
├── extractors/
│   └── pdf_parser.py        # pdfplumber text extraction
│
├── models/
│   └── schema.py            # Pydantic Invoice + LineItem schemas
│
├── services/
│   └── llm_service.py       # Groq API integration + retry logic
│
└── pipelines/
    └── data_cleaner.py      # pandas flattening and Excel export
```

---

## Output Schema

Each row in the output Excel represents **one line item** from an invoice. Invoice-level fields are repeated for each line item row.

| Column | Description |
|---|---|
| `row_id` | Invoice row number (e.g., `#36258`) |
| `order_id` | Unique order identifier (e.g., `CA-2012-AB10015140-40974`) |
| `order_date` | Date of the order |
| `ship_mode` | Shipping method (e.g., `First Class`) |
| `customer_name` | Full name of the customer |
| `postal_code` | Shipping postal code |
| `city` | Shipping city |
| `state` | Shipping state |
| `country` | Shipping country |
| `product_name` | Name of the product |
| `sub_category` | Product sub-category (e.g., `Chairs`) |
| `category` | Product category (e.g., `Furniture`) |
| `product_id` | Product SKU (e.g., `FUR-CH-4421`) |
| `quantity` | Units purchased |
| `unit_cost` | Cost per unit |
| `amount` | Line item subtotal |
| `subtotal` | Invoice subtotal (before discount & shipping) |
| `discount` | Discount amount applied |
| `shipping_fee` | Shipping fee |
| `total_amount` | Final total amount payable |

---

##  Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd pdf-extraction
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Get a free Groq API key from [console.groq.com](https://console.groq.com).

Create a `.env` file in the project root:
```
GROQ_API_KEY="your_groq_api_key_here"
```

---

## Usage

1. Place your invoice PDFs inside `data/raw_pdfs/`
2. Run the pipeline:
   ```bash
   python main.py
   ```
3. Find your output at `data/output/cleaned_invoices.xlsx`

You can safely press **`Ctrl+C`** at any time — the script will save all successfully parsed invoices to Excel before exiting.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `pdfplumber` | PDF text extraction |
| `groq` | LLM API client (Groq Cloud) |
| `openai/gpt-oss-20b` | AI model for structured data extraction |
| `pydantic` | Schema definition and data validation |
| `pandas` | Data normalization and Excel export |
| `openpyxl` | Excel file writing engine |
| `tenacity` | Exponential backoff retry for API rate limits |
| `python-dotenv` | Secure API key loading from `.env` |

---

## License

MIT
