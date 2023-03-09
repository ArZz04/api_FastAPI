from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id : Optional[str]
    ean : str
    product_name : str
    price : float