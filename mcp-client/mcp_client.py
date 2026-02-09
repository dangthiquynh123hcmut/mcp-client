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
        self._open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith(".py")

        if not is_python:
            raise ValueError("Server script must be a .py file")

        if is_python:
            path = Path(server_script_path).resolve()
            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", str(path.parent), "run", path.name],
                env=None,
            )

        self.stdio, self.write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        return True

    async def process_query(self, query: str) -> str:
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

        response = self._open_ai.responses.create(
            model=OPENAI_MODEL,
            input=query,
            tools=available_tools,
            tool_choice="auto",
        )

        final_text = []
        for item in response.output:
            if item.type == "message" and item.role == "assistant":
                for content in item.content:
                    if content.type == "output_text":
                        final_text.append(content.text)

            elif item.type == "function_call":
                tool_name = item.name
                tool_args = json.loads(item.arguments)
                
                tool_result = await self.session.call_tool(tool_name, tool_args)
                
                tool_content = ""
                if tool_result.content:
                    for content_item in tool_result.content:
                        if hasattr(content_item, 'text'):
                            tool_content += content_item.text
                        else:
                            tool_content += str(content_item)
                
                final_text.append(f"Tool result: {tool_content}")
                
                followup_response = self._open_ai.responses.create(
                    model=OPENAI_MODEL,
                    input=f"Tool {tool_name} returned: {tool_content}",
                    tools=available_tools,
                )
                
                for out in followup_response.output:
                    if out.type == "output_text":
                        final_text.append(out.text)

        return "\n".join(final_text)

async def main():
   
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

    client = MCPClient()
    
    await client.connect_to_server(sys.argv[1])


if __name__ == "__main__":
    asyncio.run(main())
