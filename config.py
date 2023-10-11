from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    x_api_key: str
    serpapi_url: str
    OPENAI_API_KEY: str
    browserless_token: str
    llm_model: str

    class Config:
        env_file = ".env"


settings = Settings()
