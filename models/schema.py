from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    product_name: str = Field(description="Name of the product (the first line under the Item column)")
    sub_category: Optional[str] = Field(None, description="Sub-category of the product. In the PDF, the line under the product name reads: Sub-Category, Category, Product-ID. The FIRST value is sub_category (e.g., 'Chairs').")
    category: Optional[str] = Field(None, description="Category of the product. In the PDF, the line under the product name reads: Sub-Category, Category, Product-ID. The SECOND value is category (e.g., 'Furniture').")
    product_id: Optional[str] = Field(None, description="Product ID. In the PDF, the line under the product name reads: Sub-Category, Category, Product-ID. The THIRD value (alphanumeric code like FUR-CH-4421) is the product_id.")
    quantity: int = Field(description="Quantity purchased")
    unit_cost: float = Field(description="Cost per unit")
    amount: float = Field(description="Subtotal for this line item")

class Invoice(BaseModel):
    row_id: Optional[str] = Field(None, description="Row ID, usually starts with #")
    order_id: Optional[str] = Field(None, description="Order ID (e.g., CA-2012-AB100...)")
    order_date: Optional[str] = Field(None, description="Date of the order")
    ship_mode: Optional[str] = Field(None, description="Shipping mode (e.g., First Class)")
    customer_name: Optional[str] = Field(None, description="Full name of the customer")
    postal_code: Optional[str] = Field(None, description="Shipping postal code")
    city: Optional[str] = Field(None, description="Shipping city")
    state: Optional[str] = Field(None, description="Shipping state")
    country: Optional[str] = Field(None, description="Shipping country")
    items: List[LineItem] = Field(description="List of items purchased")
    subtotal: Optional[float] = Field(0.0, description="Subtotal amount before discount and shipping")
    discount: Optional[float] = Field(0.0, description="Discount amount applied. Use 0.0 if no discount exists.")
    shipping_fee: Optional[float] = Field(0.0, description="Shipping fee applied. Use 0.0 if no shipping fee exists.")
    total_amount: float = Field(description="Total amount payable")
