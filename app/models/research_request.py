from pydantic import BaseModel
from typing import Optional, List


class ResearchRequest(BaseModel):
    product_url: str
    product_title: str
    countries: List[str]
    user_id: str
    reanalyze: Optional[bool] = False
