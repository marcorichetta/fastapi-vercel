from datetime import datetime
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import models

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, username: str = None):
    if not username:
        return templates.TemplateResponse("index.html", context={"request": request})

    user = get_github_profile(request, username)

    context = {"request": request, "user": user}

    return templates.TemplateResponse("index.html", context=context)


@app.get("/{username}", response_model=models.GithubUserModel)
def get_github_profile(request: Request, username: str) -> Optional[models.GithubUserModel]:

    headers = {"accept": "application/vnd.github.v3+json"}

    response = httpx.get(f"https://api.github.com/users/{username}", headers=headers)

    if response.status_code == 404:
        return False

    user = models.GithubUserModel(**response.json())

    # Sobreescribir la fecha con el formato que necesitamos
    user.created_at = datetime.strptime(user.created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%y")

    return user
