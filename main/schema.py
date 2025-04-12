from pydantic import BaseModel
from typing import Optional

class Drug(BaseModel):
    PRODUCT_ID: Optional[str] = None
    PRODUCT_NAME: Optional[str] = None
    PRODUCT_FORM: Optional[str] = None
    INGREDIENTS: Optional[str] = None
    MANUFACTURER_NAME: Optional[str] = None