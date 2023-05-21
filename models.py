from pydantic import BaseModel


class GithubUserModel(BaseModel):
    name: str | None
    blog: str
    bio: str | None
    public_repos: int
    followers: int
    avatar_url: str