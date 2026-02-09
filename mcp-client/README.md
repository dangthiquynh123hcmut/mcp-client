# MCP Client - FastAPI Gateway

FastAPI gateway tích hợp MCP server, OpenAI GPT-4, và hệ thống backend CDS. Gateway này đóng vai trò trung gian giữa frontend web và MCP server, cung cấp REST API endpoints cho chatbot và xử lý việc tạo CRF (Case Report Form) thông qua các công cụ MCP.

## Architecture

```
Frontend Web
    ↓ (HTTP)
MCP Client Gateway (FastAPI)
    ├→ OpenAI GPT-4 (Tool Selection & Orchestration)
    ├→ MCP Server (FastMCP)
    │  ├→ laboratory_test Tool
    │  └─→ CDS Backend API
    └─→ AI Backend (CDS)
         ├→ Laboratory Test Processing
         └→ CRF Form Generation
```

## Features

- **MCP Server Integration**: Tích hợp FastMCP server với các công cụ chuyên biệt
- **Laboratory Test Tool**: Tạo CRF form cho xét nghiệm lâm sàng
- **OpenAI Integration**: Sử dụng GPT-4 cho lựa chọn và orchetra công cụ
- **REST API**: Cung cấp endpoints cho frontend web
- **Backend Integration**: Kết nối đến CDS backend API

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

# AI Backend Configuration
AI_BACKEND_URL=http://localhost:8000

# FastAPI Configuration
API_HOST=127.0.0.1
API_PORT=8001

# Optional
LOG_LEVEL=INFO
```

Hoặc edit `config.py`:

```python
openai_api_key = "sk-..."
ai_backend_url = "http://localhost:8000"
api_host = "127.0.0.1"
api_port = 8001
```## Running

```bash
python main.py
```

Gateway sẽ:
1. Khởi động FastAPI server tại `http://127.0.0.1:8001`
2. Khởi động MCP server với các công cụ được định nghĩa
3. Kết nối đến CDS AI Backend
4. Sẵn sàng nhận requests từ frontend

## Development

```bash
# Run with hot reload
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## Dependencies

- FastAPI
- Pydantic
- MCP (Model Context Protocol)
- OpenAI Python SDK
- Requests
