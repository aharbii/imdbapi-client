"""End-to-end LangGraph movie agent example.

Demonstrates three usage patterns:

1. One-shot query     — single question, no memory
2. Multi-turn chat    — conversation with persistent memory
3. Custom tool subset — selective tool registration
4. Streaming          — real-time token streaming

Prerequisites
-------------
Install the agent dependencies::

    uv sync --group agents-anthropic   # for Claude (default)
    # or
    uv sync --group agents-openai      # for GPT

Set your API key::

    export ANTHROPIC_API_KEY="sk-ant-..."
    # or
    export OPENAI_API_KEY="sk-..."

Run::

    uv run python examples/langchain_agent_example.py
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from imdbapi import IMDBAPIClient
from imdbapi.langchain import create_movie_agent
from imdbapi.langchain.agent import make_openai_agent
from utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

# ---------------------------------------------------------------------------
# 1. One-shot query
# ---------------------------------------------------------------------------


async def demo_one_shot() -> None:
    """Ask a single question and print the agent's answer."""
    print("\n" + "=" * 60)
    print("DEMO 1 — One-shot query")
    print("=" * 60)

    async with IMDBAPIClient() as client:
        agent = create_movie_agent(client)

        result = await agent.ainvoke(
            {"messages": [("human", "What is the IMDb rating of Inception and who directed it?")]}
        )

    # The final message in the result is the agent's answer
    answer = result["messages"][-1].content
    print(f"\nAgent: {answer}")


# ---------------------------------------------------------------------------
# 2. Multi-turn conversation with memory
# ---------------------------------------------------------------------------


async def demo_multi_turn() -> None:
    """Hold a multi-turn conversation where the agent remembers context."""
    print("\n" + "=" * 60)
    print("DEMO 2 — Multi-turn conversation")
    print("=" * 60)

    async with IMDBAPIClient() as client:
        # checkpointer="memory" enables in-memory conversation history
        agent = create_movie_agent(client, checkpointer="memory")
        config = {"configurable": {"thread_id": "demo-session"}}

        questions = [
            "Tell me about The Shawshank Redemption.",
            "How much money did it make at the box office?",
            "Was it nominated for any Oscars?",
            "What else has the director made?",
        ]

        for question in questions:
            print(f"\nUser: {question}")
            result = await agent.ainvoke(
                {"messages": [("human", question)]}, config
            )
            answer = result["messages"][-1].content
            print(f"Agent: {answer}")


# ---------------------------------------------------------------------------
# 3. Custom tool subset
# ---------------------------------------------------------------------------


async def demo_custom_tools() -> None:
    """Build an agent with only a subset of tools (content-only, no financials)."""
    print("\n" + "=" * 60)
    print("DEMO 3 — Content-only agent (no box office / awards tools)")
    print("=" * 60)

    from langchain_anthropic import ChatAnthropic
    from langchain.agents import create_agent

    from imdbapi.langchain.agent import MOVIE_AGENT_SYSTEM_PROMPT
    from imdbapi.langchain.tools import (
        GetNameFilmographyTool,
        GetNameTool,
        GetTitleCreditsTool,
        GetTitleTool,
        SearchTitlesTool,
    )

    async with IMDBAPIClient() as client:
        # Hand-pick only the tools you want
        tools = [
            SearchTitlesTool(client=client),
            GetTitleTool(client=client),
            GetTitleCreditsTool(client=client),
            GetNameTool(client=client),
            GetNameFilmographyTool(client=client),
        ]

        agent = create_agent(
            ChatAnthropic(model="claude-opus-4-6"),
            tools,
            system_prompt=MOVIE_AGENT_SYSTEM_PROMPT,
        )

        result = await agent.ainvoke(
            {"messages": [("human", "Who played the Joker in The Dark Knight?")]}
        )

    print(f"\nAgent: {result['messages'][-1].content}")


# ---------------------------------------------------------------------------
# 4. Streaming tokens in real time
# ---------------------------------------------------------------------------


async def demo_streaming() -> None:
    """Stream the agent's answer token by token."""
    print("\n" + "=" * 60)
    print("DEMO 4 — Streaming response")
    print("=" * 60)
    print("User: Recommend 5 top-rated sci-fi movies from the 2000s.")
    print("Agent: ", end="", flush=True)

    async with IMDBAPIClient() as client:
        agent = create_movie_agent(client)

        async for event in agent.astream_events(
            {"messages": [
                ("human", "Recommend 5 top-rated sci-fi movies from the 2000s.")
            ]},
            version="v2",
        ):
            kind = event.get("event")
            # Only print text chunks from the LLM (not tool calls)
            if kind == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content"):
                    for part in (chunk.content if isinstance(chunk.content, list) else [chunk.content]):
                        if isinstance(part, str):
                            print(part, end="", flush=True)
                        elif isinstance(part, dict) and part.get("type") == "text":
                            print(part.get("text", ""), end="", flush=True)

    print()  # newline after streaming


# ---------------------------------------------------------------------------
# 5. Using the OpenAI variant
# ---------------------------------------------------------------------------


async def demo_openai_agent() -> None:
    """Same agent, GPT-4o backend.  Requires OPENAI_API_KEY."""
    print("\n" + "=" * 60)
    print("DEMO 5 — OpenAI GPT-4o agent (skipped if no key)")
    print("=" * 60)

    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipped — set OPENAI_API_KEY to run this demo.")
        return

    async with IMDBAPIClient() as client:
        agent = make_openai_agent(client, model="gpt-4o")
        result = await agent.ainvoke(
            {"messages": [("human", "What won Best Picture at the Oscars in 2020?")]}
        )

    print(f"\nAgent: {result['messages'][-1].content}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run all demos sequentially."""
    # Demo 1 is always safe to run
    await demo_one_shot()

    # DEMO 2 — Multi-turn conversation
    await demo_multi_turn()

    # DEMO 3 — Content-only agent (no box office / awards tools)
    await demo_custom_tools()
    
    # Demo 4 — streaming (comment out if you prefer clean output)
    await demo_streaming()
    
    # DEMO 5 — OpenAI GPT-4o agent (skipped if no key)
    await demo_openai_agent()


if __name__ == "__main__":
    asyncio.run(main())
