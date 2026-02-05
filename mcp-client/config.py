from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # MCP Server path - cấu hình từ .env hoặc mặc định
    server_script_path: str = os.getenv(
        "MCP_SERVER_PATH", 
        "e:\\works\\claude_final\\new_project\\main.py"
    )
    api_host: str = "127.0.0.1"  # Hoặc "localhost"
    api_port: int = 8001

settings = Settings()