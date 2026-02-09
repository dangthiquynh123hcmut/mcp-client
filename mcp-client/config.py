from pathlib import Path
from pydantic_settings import BaseSettings
import os

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    server_script_path: str = str(os.getenv(
        "MCP_SERVER_PATH", 
        BASE_DIR / "mcp_server.py"
    ))
    
    api_host: str = os.getenv("MCP_SERVER_HOST", "localhost")
    api_port: int = int(os.getenv("MCP_SERVER_PORT", 8001))

settings = Settings()