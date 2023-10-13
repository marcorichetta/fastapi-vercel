from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.routers import research_router
from app.models.research_request import ResearchRequest
from app.services import research_service


app = FastAPI()

app.include_router(research_router.router, tags=["Research"])

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["http://localhost:3000", "https://getelmo.vercel.app"]  # React app address
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],
)
