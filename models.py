from pydantic import BaseModel, constr
from typing import Optional, List


class ResearchRequest(BaseModel):
    product_url: str
    product_title: str
    countries: List[str]
    user_id: str
    reanalyze: Optional[bool] = False


class AddProductModel(BaseModel):
    userid: int
    url: constr(max_length=191)
    title: constr(max_length=255)
    scrape_details: Optional[constr(max_length=5000)]
    analysis_result: Optional[constr(max_length=5000)]
    country_pricing_analysis: Optional[dict]  # You can define a more specific type if you know the structure


class UpdateProductModel(BaseModel):
    url: Optional[constr(max_length=191)]
    title: Optional[constr(max_length=255)]
    scrape_details: Optional[constr(max_length=5000)]
    analysis_result: Optional[constr(max_length=5000)]
    country_pricing_analysis: Optional[dict]
