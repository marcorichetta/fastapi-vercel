import json
from app.services.scrape_summarize import scrape_and_summarize
from app.database.database import add_product, get_product_by_id, update_product_by_user_and_url
from app.services.analysis import market_analysis, extract_country_pricing_analysis
from app.models.research_request import ResearchRequest
from app.models.product import AddProductModel
from app.models.database import ProductModel


async def validate_request(request: ResearchRequest) -> ResearchRequest:
    try:
        research_request_data = request.json()
        if isinstance(research_request_data, str):
            research_request_data = json.loads(research_request_data)
        return ResearchRequest(**research_request_data)
    except (ValueError, TypeError) as e:
        raise ValueError("Invalid request data format.") from e


async def handle_existing_product(existing_product: dict) -> dict:
    if existing_product:
        print(f"Handling existing product: {existing_product}")
        return {
            "product_id": existing_product["id"],
            "analysis": existing_product["analysis_result"],
            "scrape_details": existing_product["scrape_details"],
            "url": existing_product["url"],
            "title": existing_product["title"],
            "country_pricing_analysis": existing_product["country_pricing_analysis"],
            "competitor_analysis": existing_product["competitor_analysis"],
            "message": "Product analysis already exists. Click 'Reanalyze' to update the analysis.",
        }


async def perform_analysis(product_url: str, product_title: str, countries: list) -> tuple:
    # Scrape and summarize the main URL provided by the user
    product_url_summary = await scrape_and_summarize(product_url, product_title, countries)
    analysis_result = market_analysis(product_url_summary, product_title, countries)
    detailed_analysis = extract_country_pricing_analysis(analysis_result)
    return product_url_summary, analysis_result, detailed_analysis


async def create_or_update_product_data(product_data: dict, existing_product: dict, reanalyze: bool) -> dict:
    if existing_product and reanalyze:
        update_product_by_user_and_url(product_data["userid"], product_data["url"], product_data)

        updated_product = get_product_by_id(existing_product["id"])
        return updated_product
    else:
        add_product_model_instance = AddProductModel(**product_data)
        new_product = add_product(add_product_model_instance)
        return new_product
