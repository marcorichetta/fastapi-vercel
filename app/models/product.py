from pydantic import BaseModel, constr
from typing import Optional, List, Dict, Any


class AddProductModel(BaseModel):
    userid: int
    url: constr(max_length=191)
    title: constr(max_length=255)
    scrape_details: Optional[constr(max_length=5000)]
    analysis_result: Optional[constr(max_length=5000)]
    country_pricing_analysis: Optional[dict]


class UpdateProductModel(BaseModel):
    url: Optional[constr(max_length=191)]
    title: Optional[constr(max_length=255)]
    scrape_details: Optional[constr(max_length=5000)]
    analysis_result: Optional[constr(max_length=5000)]
    country_pricing_analysis: Optional[List[Dict[str, Any]]]
