import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import ResearchRequest
from fastapi import FastAPI
from fastapi import FastAPI, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


from search import search, generate_google_query_with_llm
from scrape import scrape_and_summarize
from database import add_product, get_product_by_url
from analysis import market_analysis, extract_country_pricing_analysis

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
timeout = httpx.Timeout(timeout=5.0, read=15.0)
client = httpx.AsyncClient(limits=limits, timeout=timeout)

app.state.limiter = limiter
# app.add_exception_handler(_rate_limit_exceeded_handler)


@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down...")
    await client.aclose()


@app.get("/", response_class=HTMLResponse)
async def index():
    return "Welcome to Elmo Brain API!"


@app.post("/research")
def research_product(request: ResearchRequest):
    """
    Conducts research on a product by scraping and summarizing provided and generated URLs.

    Parameters:
        - request: An instance of ResearchRequest containing the necessary data.

    Returns:
        - A dictionary with the product_id and the conducted analysis.
    """
    product_url = request.product_url
    product_title = request.product_title
    countries = request.countries
    user_id = request.user_id
    reanalyze = request.reanalyze

    existing_product = get_product_by_url(product_url)

    if existing_product and not reanalyze:
        return {
            "product_id": existing_product.id,
            "analysis": existing_product.analysis_result,
            "scrape_details": existing_product.scrape_details,
            "url": existing_product.url,
            "title": existing_product.title,
        }

    # Scrape and summarize the main URL provided by the user
    product_url_summary = scrape_and_summarize(product_url, product_title, countries)
    all_scraped_contents = [product_url_summary]

    for country in countries:
        query = generate_google_query_with_llm(product_title, country)
        search_results = search(query, num=5, gl=country)

        # Scrape & summarize content for each URL result
        all_scraped_contents.extend(
            scrape_and_summarize(result.get("link", ""), product_title, countries)
            for result in search_results.get("results", [])
            if result.get("link")
        )

    analysis_result = market_analysis("\n".join(all_scraped_contents), product_title, countries)
    detailed_analysis = extract_country_pricing_analysis(analysis_result)

    # Save the result to the product table
    product_data = {
        "userid": user_id,
        "url": product_url,
        "title": product_title,
        "scrape_details": "\n".join(all_scraped_contents),
        "analysis_result": analysis_result,
        "country_pricing_analysis": detailed_analysis,
    }
    product = add_product(product_data)

    return {"product": product}
