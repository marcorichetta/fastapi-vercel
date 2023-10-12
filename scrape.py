import json
import requests
from bs4 import BeautifulSoup
from typing import List
from fastapi import HTTPException
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
from config import settings


def scrape_and_summarize(customer_product_url: str, product_title: str, countries: List[str]):
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

        # Initialize language model
        llm = ChatOpenAI(
            temperature=0,
            model=settings.llm_model,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
        docs = text_splitter.create_documents([text])

        map_prompt = """
            Given the content from the scraped website, analyze and extract key details of the product. Focus on summarizing the main points and retrieving pertinent information.

            Content:
            "{text}"

            Instructions:
            1. Identify the product with the title "{product_title}".
            2. Extract and summarize the following details:
                - Title of the product.
                - Original price (use currency symbols if mentioned, e.g., "$38.50").
                - Main features and unique selling points of the product.

            Example Output:
            - Title: Silk Tie
            - Price: $38.50
            - Description: A high-quality silk tie suitable for formal events with a unique paisley design.
        """

        map_prompt_template = PromptTemplate(
            template=map_prompt,
            input_variables=["text", "product_title"],
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
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to scrape the website.")
