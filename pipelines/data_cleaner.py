import pandas as pd
from typing import List
from models.schema import Invoice

def flatten_invoices_to_dataframe(invoices: List[Invoice]) -> pd.DataFrame:
    """
    Converts a list of Pydantic Invoice models into a flat pandas DataFrame.
    Nested line items are flattened so each row represents one item, 
    with the parent invoice details repeated for each item row.
    """
    flat_data = []
    
    for invoice in invoices:
        invoice_dict = invoice.model_dump()
        items = invoice_dict.pop('items', [])
        
        # If there are no items, just add the invoice level data
        if not items:
            flat_data.append(invoice_dict)
            continue
            
        # For each item, combine the invoice level data with the item level data
        for item in items:
            row = {**invoice_dict, **item}
            flat_data.append(row)
            
    df = pd.DataFrame(flat_data)
    
    # Basic data cleaning/normalization
    if not df.empty:
        # Convert date strings to datetime objects where possible
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce').dt.date
            
    return df

def export_to_excel(df: pd.DataFrame, output_path: str):
    """
    Exports the cleaned pandas DataFrame to an Excel file.
    """
    df.to_excel(output_path, index=False)
    print(f"Successfully exported data to {output_path}")
