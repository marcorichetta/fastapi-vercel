from typing import List
from pydantic import BaseModel


class ResearchRequest(BaseModel):
    product_url: str
    product_title: str
    countries: List[str]
