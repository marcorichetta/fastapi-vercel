import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import ResearchRequest

from typing import List
import json
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
import json
from config import settings

from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate


app = FastAPI()
templates = Jinja2Templates(directory="templates")

limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
timeout = httpx.Timeout(timeout=5.0, read=15.0)
client = httpx.AsyncClient(limits=limits, timeout=timeout)


@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down...")
    await client.aclose()


@app.get("/", response_class=HTMLResponse)
async def index():
    return "Welcome to Elmo Brain API!"


def search(query: str, num: int = 5, gl: str = "us"):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "gl": gl, "num": num})
    headers = {"X-API-KEY": settings.x_api_key, "Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


def scrape(
    customer_product_url: str,
    product_title: str,
    countries: List[str],
):
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }
    data = {"url": customer_product_url}
    data_json = json.dumps(data)
    response = requests.post(
        f"https://chrome.browserless.io/content?token={settings.browserless_token}",
        headers=headers,
        data=data_json,
    )
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        if len(text) > 8000 or customer_product_url:
            output = market_analysis(text, product_title, countries)
            return output
        else:
            return text
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to scrape the website.")


def market_analysis(content, product_title: str, countries: List[str]):
    llm = ChatOpenAI(
        temperature=0,
        model=settings.llm_model,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])

    map_prompt = """
        Given the provided scraped data and based on your training data, suggest a suitable selling price for the product in the mentioned countries, factoring in local market conditions, demand, and other relevant factors. 

        Text from scraped URL:
        "{text}"

        Instructions:
        1. Locate the product with the title "{product_title}" within the text.
        2. Present the information in the following structured format:

        Product Details:
        - Title: [Product Title]
        - Price: [Original Price using the local currency symbol, e.g., "$38.50"]
        - Description: [Product Description]

        Suggested Selling Price:
        [For each country in {countries} provide a detailed rationale and the suggested price using the local currency symbol]

            Example:
            1. Mexico: Considering the economic conditions, market demand, and the average income in Mexico, a suitable selling price for the "[Product Title]" could be around MXN$750.00. This price is competitive and affordable for the middle-class consumers who would be the target market for this product.

        3. Ensure your suggested price format uses the local currency symbol correctly (e.g., for the US, suggest as "$59.99", not "59.99 US dollars" or "200 US dollars"). Also, consider local economic conditions, product demand, and other relevant factors in your suggestion.
    """

    map_prompt_template = PromptTemplate(
        template=map_prompt,
        input_variables=["text", "product_title", "countries"],
    )
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True,
    )
    output = summary_chain.run(input_documents=docs, product_title=product_title, countries=countries)
    return output


@app.post("/research")
def research_product(request: ResearchRequest):
    product_url = request.product_url
    product_title = request.product_title
    countries = request.countries

    # 1. Search for similar products on Google
    google_results = search(product_title)
    top_urls = [
        result["link"]
        for result in google_results.get("organic", [])
        if "link" in result and result["link"] != product_url
    ][:5]

    print(top_urls)

    scraped_contents = []
    for url in top_urls:
        scraped_content = scrape(url, product_title, countries)
        scraped_contents.append(scraped_content)
    print(scraped_contents)

    return []
