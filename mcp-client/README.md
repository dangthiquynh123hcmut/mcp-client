# MCP Client - FastAPI Gateway

FastAPI gateway tích hợp MCP client, OpenAI GPT-4, và hệ thống backend CDS. Gateway này đóng vai trò trung gian giữa frontend web và MCP server, cung cấp REST API endpoints cho chatbot.

## Architecture

```
Frontend Web
    ↓ (HTTP)
MCP Client Gateway (FastAPI)
    ├→ OpenAI GPT-4 (Tool Selection & Orchestration)
    └→ MCP Server (stdio)
         ↓
       CDS Backend
```

## Installation

```bash
# Clone & navigate
git clone <repository-url>
cd mcp-client

# Install dependencies
pip install -r requirements.txt

# Hoặc với uv
uv pip install -r requirements.txt
```

## Configuration

Tạo file `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# MCP Server Configuration
MCP_SERVER_SCRIPT_PATH=/path/to/new_project/main.py
MCP_SERVER_TYPE=python  # python hoặc node

# FastAPI Configuration
API_HOST=127.0.0.1
API_PORT=8001

# Optional
LOG_LEVEL=INFO
```

Hoặc edit `config.py`:

```python
server_script_path = "/path/to/new_project/main.py"
server_type = "python"
api_host = "127.0.0.1"
api_port = 8001
```

## Running

```bash
python main.py
```

Gateway sẽ:
1. Khởi động FastAPI server tại `http://127.0.0.1:8001`
2. Kết nối đến MCP server via stdio
3. Sẵn sàng nhận requests từ frontend
