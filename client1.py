import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
import json

SERVERS= {
    "test": {
        "transport": "stdio",
        "command": "C:/Users/maaz7/AppData/Local/Programs/Python/Python311/Scripts/uv.exe",
        "args": [
            "run",
            "fastmcp",
            "run",
"D:/mcp project/mcp-server-for-test-math/main.py:mcp"
        ]
    },
    "manim-server": {
        "transport": "stdio",
        "command": "C:/Users/maaz7/AppData/Local/Programs/Python/Python311/python.exe",
        "args": [
            r"C:\Users\maaz7\OneDrive\Desktop\manim-mcp-server\src\manim_server.py"
        ],
        "env": {
            "MANIM_EXECUTABLE": r"C:\Users\maaz7\AppData\Local\Programs\Python\Python311\Scripts\manim.exe"
        }
    }
    # "expense": {
    #     "transport": "streamable_http",
    #     "url": "https://remote-server-test.fastmcp.app/mcp"
    # }
}

async def main():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools={}

    for tool in tools:
        named_tools[tool.name]=tool
    print("Available Tools:", named_tools.keys())

    llm = ChatGroq(model="openai/gpt-oss-120b",temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    prompt="Draw a triangle rotating in place using the manim tool."

    res = await llm_with_tools.ainvoke(prompt)

    if not getattr(res,"tool_calls", None):
        print("\nLLM Reply:", res.content)
        return
    tool_messages=[]
    for tool_call in res.tool_calls:

        selected_tool = tool_call["name"]
        selected_tool_args = tool_call["args"] or {}
        selected_tool_id = tool_call["id"]

        result = await named_tools[selected_tool].ainvoke(selected_tool_args)

        tool_messages.append(ToolMessage(content=json.dumps(result),tool_call_id=selected_tool_id))

    final_response = await llm_with_tools.ainvoke([prompt, res, *tool_messages])
    print(f"Final Response: {final_response.content}")
if __name__=="__main__":
    asyncio.run(main())