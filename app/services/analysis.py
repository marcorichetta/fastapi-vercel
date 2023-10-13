from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate

from typing import List
from app.config.config import settings


def market_analysis(content, product_title: str, countries: List[str]):
    llm = ChatOpenAI(
        temperature=0,
        model=settings.llm_model,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])

    map_prompt = """
    Given the provided scraped data and based on your training data, suggest a suitable selling price for the product in the mentioned countries, factoring in local market conditions, demand, and other relevant factors. Analyze the product's description thoroughly to understand its characteristics, as this will play a key role in the pricing decision.

    Text from scraped URL:
    "{text}"

    Instructions:
    1. Locate the product with the title "{product_title}" within the text.
    2. Analyze the product description to discern its type, features, and any unique selling points.
    3. Present the information in the following structured format:

    Product Details:
    - Title: [Product Title]
    - Price: [Original Price using the local currency symbol, e.g., "$38.50"]
    - Description: [Product Description]

    Suggested Selling Price:
    [For each country in {countries}, structure the response as: 

    Country: [Country Name]
    Price: [Suggested Price]
    Analysis: [Detailed rationale]

    Ensure that the country name, suggested price, and analysis are on separate lines for easier extraction.]

    4. Ensure your suggested price format uses the local currency symbol correctly (e.g., for the US, suggest as "$59.99", not "59.99 US dollars" or "200 US dollars"). Also, consider local economic conditions, product demand, and other relevant factors in your suggestion.
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


def extract_country_pricing_analysis(output):
    country_analysis_data = output.split("Suggested Selling Price:")[-1].strip()
    country_data_entries = country_analysis_data.split("Country:")

    country_pricing_analysis = []

    for entry in country_data_entries[1:]:
        lines = entry.strip().split("\n")
        country_name = lines[0].strip()
        price = lines[1].split(":")[1].strip()
        analysis = lines[2].split(":")[1].strip()

        country_pricing_analysis.append({"country": country_name, "Price": price, "Analysis": analysis})

    return country_pricing_analysis
