import httpx
from typing import Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8001/api"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools"""
        response = await self.client.get("/tools")
        response.raise_for_status()
        return response.json()["tools"]

    async def query(self, query: str) -> List[Dict[str, Any]]:
        """Send a query and get response"""
        response = await self.client.post(
            "/query",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()["messages"]

    async def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Call a specific tool"""
        response = await self.client.post(
            "/tool",
            json={"name": name, "args": args}
        )
        response.raise_for_status()
        return response.json()["result"]

    async def close(self):
        """Close client connection"""
        await self.client.aclose()