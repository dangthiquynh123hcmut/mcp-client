from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from mcp_client import MCPClient
from routers.query_router import setup_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = MCPClient()
    app.state.client = client
    app.state.client_connected = False
    
    try:
        connected = await client.connect_to_server(settings.server_script_path)
        if connected:
            app.state.client_connected = True
            print("✅ MCP Server connected successfully!")
        else:
            print("⚠️  MCP Server connection failed")
    except Exception as e:
        print(f"⚠️  MCP Server connection error: {str(e)}")
    
    yield
    
    # Shutdown
    try:
        await client.cleanup()
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

def create_app() -> FastAPI:
    """Create and configure FastAPI app"""
    app = FastAPI(
        title="MCP Chatbot API",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup routes
    setup_routes(app)

    return app

app = create_app()