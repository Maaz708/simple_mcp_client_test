import asyncio
import json
import streamlit as st

from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# ----------------------------
# MCP SERVERS
# ----------------------------

SERVERS = {
    "test": {
        "transport": "stdio",
        "command": r"C:\Users\maaz7\AppData\Local\Programs\Python\Python311\Scripts\uv.exe",
        "args": [
            "run",
            "fastmcp",
            "run",
            r"D:\mcp project\mcp-server-for-test-math\main.py:mcp",
        ],
    },

    "manim-server": {
        "transport": "stdio",
        "command": r"C:\Users\maaz7\AppData\Local\Programs\Python\Python311\python.exe",
        "args": [
            r"C:\Users\maaz7\OneDrive\Desktop\manim-mcp-server\src\manim_server.py"
        ],
        "env": {
            "MANIM_EXECUTABLE": r"C:\Users\maaz7\AppData\Local\Programs\Python\Python311\Scripts\manim.exe"
        },
    },
}


# ----------------------------
# Async Agent
# ----------------------------

async def run_agent(messages):

    client = MultiServerMCPClient(SERVERS)

    tools = await client.get_tools()

    tool_map = {tool.name: tool for tool in tools}

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
    )

    llm = llm.bind_tools(tools)

    ai = await llm.ainvoke(messages)

    if not ai.tool_calls:
        return ai.content

    tool_messages = []

    for tool_call in ai.tool_calls:

        tool_name = tool_call["name"]

        tool_args = tool_call["args"]

        tool_id = tool_call["id"]

        result = await tool_map[tool_name].ainvoke(tool_args)

        tool_messages.append(
            ToolMessage(
                content=json.dumps(result),
                tool_call_id=tool_id,
            )
        )

    final = await llm.ainvoke(
        messages + [ai] + tool_messages
    )

    return final.content


# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(
    page_title="MCP Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 MCP AI Assistant")

st.caption("Math MCP + Manim MCP")


if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


prompt = st.chat_input("Ask anything...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    history = []

    for msg in st.session_state.messages:

        if msg["role"] == "user":
            history.append(HumanMessage(msg["content"]))
        else:
            history.append(AIMessage(msg["content"]))

    with st.chat_message("assistant"):

        placeholder = st.empty()

        with st.spinner("Thinking..."):

            response = asyncio.run(
                run_agent(history)
            )

        streamed = ""

        for ch in response:
            streamed += ch
            placeholder.markdown(streamed + "▌")

        placeholder.markdown(streamed)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )