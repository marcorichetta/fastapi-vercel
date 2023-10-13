from typing import Optional, Union
import httpx
from app.config.config import settings


class ClerkClient:
    def __init__(self, bearer_token: str):
        self.headers = {"Authorization": f"Bearer {bearer_token}"}

    async def _request(self, method: str, endpoint: str, **kwargs) -> Union[dict, None]:
        async with httpx.AsyncClient() as client:
            url = f"{settings.CLERK_BASE_URL}{endpoint}"
            try:
                response = await client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"An error occurred: {e}")
                return None

    async def get_user(self, user_id: str) -> Optional[dict]:
        return await self._request("GET", f"/users/{user_id}")
