import httpx
from app.config.config import settings
from langchain.llms import OpenAI
from json import JSONDecodeError


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
    payload = {"q": query, "gl": gl, "num": num}
    headers = {"X-API-KEY": settings.x_api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

        # Check if the response status code is not 200 (OK)
        if response.status_code != 200:
            raise ValueError(f"Unexpected status code {response.status_code}: {response.text}")

        # Safely parse the JSON response
        try:
            return response.json()
        except JSONDecodeError:
            raise ValueError(f"Unable to parse API response: {response.text}")
