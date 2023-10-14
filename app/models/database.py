from pydantic import BaseModel, HttpUrl
from typing import Optional


from typing import List, Dict
from pydantic import BaseModel


from typing import Optional, List, Dict
from pydantic import BaseModel


class ProductModel(BaseModel):
    userid: str
    url: str
    title: str
    scrape_details: str
    analysis_result: str
    country_pricing_analysis: Optional[List[Dict]]
    competitor_analysis: Optional[List[Dict]]

    class Config:
        orm_mode = True


class UpdateProductModel(BaseModel):
    name: str
    url: HttpUrl
    description: str
    price: str
