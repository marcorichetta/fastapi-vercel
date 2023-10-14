from app.models.database import ProductModel
from app.models.research_request import ResearchRequest
from app.database.database import get_product_by_url
from app.services.search_product import search, generate_google_query_with_llm
from app.services.scrape_summarize import scrape_and_summarize
from app.services.utils.research_utils import (
    validate_request,
    handle_existing_product,
    perform_analysis,
    create_or_update_product_data,
)


async def detailed_research_product(request: ResearchRequest):
    """
    Conducts detailed research on a product by scraping and summarizing provided and generated URLs.

    Parameters:
        - request: An instance of ResearchRequest containing the necessary data.

    Returns:
        - A dictionary with the product_id and the conducted analysis.
    """
    try:
        research_request = await validate_request(request)

        existing_product = get_product_by_url(research_request.product_url)
        existing_product_dict = await handle_existing_product(existing_product)

        if existing_product_dict and not research_request.reanalyze:
            return existing_product_dict

        # Scrape and summarize the main URL provided by the user
        product_url_summary = await scrape_and_summarize(
            research_request.product_url, research_request.product_title, research_request.countries
        )

        # If detailed research is needed, additional summaries can be appended to all_scraped_contents
        all_scraped_contents = [product_url_summary]

        # Initiate detailed research, e.g., scraping additional URLs here
        search_results_array = []

        for country in research_request.countries:
            try:
                query = generate_google_query_with_llm(research_request.product_title, country)
                search_results = await search(query, num=5, gl=country)
            except ValueError as e:
                return {"error": str(e)}

            # Scrape & summarize content for each URL result
            for result in search_results.get("results", []):
                if result.get("link"):
                    summary = await scrape_and_summarize(
                        result.get("link", ""), research_request.product_title, research_request.countries
                    )
                    all_scraped_contents.append(summary)
                    search_results_array.append({"url": result.get("link"), "summary": summary})

        analysis_result, detailed_analysis = await perform_analysis(
            "\n".join(all_scraped_contents), research_request.product_title, research_request.countries
        )

        product = ProductModel(
            userid=research_request.id,
            url=research_request.product_url,
            title=research_request.product_title,
            scrape_details="\n".join(all_scraped_contents),
            analysis_result=analysis_result,
            country_pricing_analysis=detailed_analysis,
            competitor_analysis=search_results_array,
        )

        product = await create_or_update_product_data(product, existing_product, research_request.reanalyze)

        return {
            "product_id": product.id,
            "analysis": product.analysis_result,
            "scrape_details": product.scrape_details,
            "url": product.url,
            "title": product.title,
            "country_pricing_analysis": product.country_pricing_analysis,
            "competitor_analysis": product.competitor_analysis,
            "message": "Product analysis conducted successfully.",
        }

    except Exception as e:
        # Logging or further exception handling here
        raise ValueError(f"An error occurred during product research: {str(e)}")


async def research_product(request: ResearchRequest) -> dict:
    """
    Conducts research on a product by scraping and summarizing provided URLs.

    Parameters:
        - request: An instance of ResearchRequest containing the necessary data.

    Returns:
        - A dictionary with the product_id and the conducted analysis.
    """
    try:
        research_request = await validate_request(request)
        existing_product = get_product_by_url(research_request.product_url)
        if existing_product:
            existing_product_dict = await handle_existing_product(existing_product)
            if existing_product_dict:
                return existing_product_dict

        product_url_summary, analysis_result, detailed_analysis = await perform_analysis(
            research_request.product_url, research_request.product_title, research_request.countries
        )

        product_data = {
            "userid": research_request.user_id,
            "url": research_request.product_url,
            "title": research_request.product_title,
            "scrape_details": product_url_summary,
            "analysis_result": analysis_result,
            "country_pricing_analysis": detailed_analysis,
            "competitor_analysis": [],
        }

        product = await create_or_update_product_data(product_data, existing_product, research_request.reanalyze)

        return {
            "product_id": product["id"],
            "analysis": product["analysis_result"],
            "scrape_details": product["scrape_details"],
            "url": product["url"],
            "title": product["title"],
            "country_pricing_analysis": product["country_pricing_analysis"],
            "competitor_analysis": product["competitor_analysis"],
            "message": "Product analysis conducted successfully.",
        }

    except Exception as e:
        # You might want to log the exception here
        raise ValueError(f"An error occurred during product research: {str(e)}")
