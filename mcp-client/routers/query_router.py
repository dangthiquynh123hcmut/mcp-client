from fastapi import APIRouter, HTTPException
from fastapi import FastAPI, Body

router = APIRouter(prefix="/api", tags=["query"])

def setup_routes(app: "FastAPI"):
    
    @router.post("/query")
    async def process_query(request: str = Body(..., media_type="text/plain")):
        if not app.state.client_connected:
            raise HTTPException(status_code=503, detail="MCP Server not connected")
        try:
            messages = await app.state.client.process_query(str(request))
            return {"messages": messages}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)