from fastapi import APIRouter, HTTPException
from models import ToolCall
from fastapi import FastAPI, Body

router = APIRouter(prefix="/api", tags=["query"])

def setup_routes(app: "FastAPI"):
    """Setup all routes"""
    
    @router.get("/tools")
    async def get_available_tools():
        """Get list of available tools"""
        if not app.state.client_connected:
            raise HTTPException(status_code=503, detail="MCP Server not connected")
        try:
            tools = await app.state.client.get_mcp_tools()
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                    for tool in tools
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/query")
    async def process_query(request: str = Body(..., media_type="text/plain")):
        """Process a query and return the response"""
        if not app.state.client_connected:
            raise HTTPException(status_code=503, detail="MCP Server not connected")
        try:
            messages = await app.state.client.process_query(str(request))
            return {"messages": messages}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/tool")
    async def call_tool(tool_call: ToolCall):
        """Call a specific tool"""
        if not app.state.client_connected:
            raise HTTPException(status_code=503, detail="MCP Server not connected")
        try:
            result = await app.state.client.call_tool(tool_call.name, tool_call.args)
            return {"result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    app.include_router(router)