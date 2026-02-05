import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

OPENAI_MODEL = "gpt-4.1"


class MCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._open_ai: OpenAI | None = None

    @property
    def open_ai(self) -> OpenAI:
        if self._open_ai is None:
            self._open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._open_ai

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        if is_python:
            path = Path(server_script_path).resolve()
            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", str(path.parent), "run", path.name],
                env=None,
            )
        else:
            server_params = StdioServerParameters(
                command="node",
                args=[server_script_path],
                env=None,
            )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        print("\nConnected to server with tools:", [t.name for t in tools])
        return True

    async def get_mcp_tools(self):
        """Get list of available MCP tools"""
        if not self.session:
            raise Exception("Not connected to MCP server")
        tools_response = await self.session.list_tools()
        return tools_response.tools

    async def call_tool(self, tool_name: str, tool_args: dict):
        """Call a specific MCP tool directly"""
        if not self.session:
            raise Exception("Not connected to MCP server")
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            # Extract text from result
            tool_content = ""
            if result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        tool_content += content_item.text
                    else:
                        tool_content += str(content_item)
            return tool_content if tool_content else str(result)
        except Exception as e:
            raise Exception(f"Failed to call tool {tool_name}: {str(e)}")

    async def process_query(self, query: str) -> str:
        """Process a query with OpenAI and MCP tools"""
        if not self.session:
            raise Exception("Not connected to MCP server")
            
        tools_response = await self.session.list_tools()

        available_tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            }
            for tool in tools_response.tools
        ]

        # 1️⃣ First LLM call - input phải là string
        response = self.open_ai.responses.create(
            model=OPENAI_MODEL,
            input=query,  # String query
            tools=available_tools,
            tool_choice="auto",
        )

        final_text = []
        # 2️⃣ Handle response items
        for item in response.output:
            # Chỉ xử lý message từ assistant
            if item.type == "message" and item.role == "assistant":
                for content in item.content:
                    if content.type == "output_text":
                        final_text.append(content.text)

            # Tool call
            elif item.type == "function_call":
                tool_name = item.name
                tool_args = json.loads(item.arguments)
                
                print(f"\n🔧 Calling MCP tool: {tool_name}({tool_args})")

                # Gọi MCP tool và lấy kết quả
                tool_result = await self.session.call_tool(tool_name, tool_args)
                
                # Xử lý tool result
                tool_content = ""
                if tool_result.content:
                    for content_item in tool_result.content:
                        if hasattr(content_item, 'text'):
                            tool_content += content_item.text
                        else:
                            tool_content += str(content_item)
                
                final_text.append(f"Tool result: {tool_content}")
                
                # Input phải là string hoặc array of message objects
                followup_response = self.open_ai.responses.create(
                    model=OPENAI_MODEL,
                    input=f"Tool {tool_name} returned: {tool_content}",
                    tools=available_tools,
                )
                
                # Xử lý followup response
                for out in followup_response.output:
                    if out.type == "output_text":
                        final_text.append(out.text)

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break

            try:
                result = await self.process_query(query)
                print("\n" + result)
            except Exception as e:
                print(f"\n❌ Error: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <path_to_server.py>")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
