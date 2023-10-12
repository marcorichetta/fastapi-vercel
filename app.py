import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import ResearchRequest
from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


from search import search, generate_google_query_with_llm
from scrape import scrape_and_summarize
from database import add_product, get_product_by_url, update_product_by_user_and_url
from analysis import market_analysis, extract_country_pricing_analysis

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

origins = ["http://localhost:3000", "https://elmo-aipfs9ovf-elmo-ui.vercel.app"]  # React app address

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],
)

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
    print(request)
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
            "country_pricing_analysis": existing_product.country_pricing_analysis,
            "competitor_analysis": existing_product.competitor_analysis,
            "message": "Product analysis already exists. Click 'Reanalyze' to update the analysis.",
        }

    # Scrape and summarize the main URL provided by the user
    product_url_summary = scrape_and_summarize(product_url, product_title, countries)
    all_scraped_contents = [product_url_summary]

    search_results_array = []

    for country in countries:
        query = generate_google_query_with_llm(product_title, country)
        search_results = search(query, num=5, gl=country)

        # Scrape & summarize content for each URL result
        for result in search_results.get("results", []):
            if result.get("link"):
                summary = scrape_and_summarize(result.get("link", ""), product_title, countries)
                all_scraped_contents.append(summary)
                search_results_array.append({"url": result.get("link"), "summary": summary})

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
        "competitor_analysis": search_results_array,
    }
    if existing_product and reanalyze:
        # Update existing product
        update_product_by_user_and_url(user_id, product_url, product_data)
        product = existing_product  # Use the existing product for the return data
        response_data = {"message": "Product analysis updated successfully.", "product": product.as_dict()}
    else:
        # Add a new product
        product = add_product(product_data)
        response_data = {"message": "Product analysis completed successfully.", "product": product.as_dict()}

    return {
        "product_id": response_data["product"]["id"],
        "analysis": response_data["product"]["analysis_result"],
        "scrape_details": response_data["product"]["scrape_details"],
        "url": response_data["product"]["url"],
        "title": response_data["product"]["title"],
        "country_pricing_analysis": response_data["product"]["country_pricing_analysis"],
        "competitor_analysis": response_data["product"]["competitor_analysis"],
        "message": response_data["message"],
    }
