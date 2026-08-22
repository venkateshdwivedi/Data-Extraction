import os
import json
from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt
from models.schema import Invoice

def handle_retry(retry_state):
    print(f"Retrying after error: {retry_state.outcome.exception()}")

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    before_sleep=handle_retry
)
def parse_invoice_with_llm(raw_text: str) -> Invoice:
    """
    Sends the raw text to Groq (openai/gpt-oss-20b) and parses it into
    the strict Invoice schema using json_object response format.
    Uses tenacity for exponential backoff in case of rate limits.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Please set a valid GROQ_API_KEY in your .env file.")

    client = Groq(api_key=api_key)

    schema_str = json.dumps(Invoice.model_json_schema(), indent=2)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert invoice data extractor. "
                    "Extract all invoice details from the provided text and return a single valid JSON object. "
                    "You MUST use EXACTLY the following field names — do not rename, abbreviate, or invent any field names:\n\n"
                    f"{schema_str}\n\n"
                    "Rules:\n"
                    "- Use null for any field not found in the text.\n"
                    "- The field 'items' must be a list of line item objects.\n"
                    "- Use 'customer_name' for the customer, 'order_id' for the order ID, 'order_date' for the date.\n"
                    "- Use 'unit_cost' (not 'unit_price') and 'amount' for line item pricing.\n"
                    "- Return ONLY raw JSON. No markdown, no explanation, no surrounding text."
                )
            },
            {
                "role": "user",
                "content": f"Extract the invoice details from the following text:\n\n{raw_text}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    response_dict = json.loads(response.choices[0].message.content)
    return Invoice(**response_dict)
