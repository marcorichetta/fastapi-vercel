import json
import httpx
from config import settings
from langchain.llms import OpenAI


from langchain.llms import OpenAI


def generate_google_query_with_llm(product_title: str, country: str) -> str:
    # Initialize the OpenAI LLM
    llm = OpenAI(openai_api_key=settings.OPENAI_API_KEY, model_name=settings.llm_model, temperature=0.7)

    # Define a prompt to generate a Google query
    prompt_text = (
        f"Given the product '{product_title}' and its potential market in '{country}', "
        f"generate a comprehensive Google search query to fetch useful information "
        f"about the product in that specific market."
    )

    response = llm(prompt_text)
    query = response.strip()
    return query


async def search(query: str, num: int = 5, gl: str = "us"):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "gl": gl, "num": num})
    headers = {"X-API-KEY": settings.x_api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
    return response.json()
