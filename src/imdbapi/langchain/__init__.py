"""LangChain / LangGraph integration for the imdbapi client.

Exposes the full imdbapi.dev endpoint surface as typed LangChain tools that
can be registered with any LangGraph ReAct agent or LangChain agent executor.

Quick start::

    from imdbapi import IMDBAPIClient
    from imdbapi.langchain import create_imdb_tools, create_movie_agent

    async with IMDBAPIClient() as client:
        tools  = create_imdb_tools(client)          # list[BaseTool]
        agent  = create_movie_agent(client)          # LangGraph CompiledGraph
        result = await agent.ainvoke(
            {"messages": [("human", "Who directed Inception?")]}
        )

Dependencies (install one provider group)::

    uv sync --group agents-anthropic   # Claude
    uv sync --group agents-openai      # GPT
"""

from imdbapi.langchain.agent import create_movie_agent
from imdbapi.langchain.tools import (
    GetInterestCategoryTool,
    GetNameFilmographyTool,
    GetNameTool,
    GetTitleAwardsTool,
    GetTitleBoxOfficeTool,
    GetTitleCreditsTool,
    GetTitleEpisodesTool,
    GetTitleTool,
    ListInterestCategoriesTool,
    ListTitlesTool,
    SearchTitlesTool,
    create_imdb_tools,
)

__all__ = [
    # factory
    "create_imdb_tools",
    "create_movie_agent",
    # individual tools (for custom agent composition)
    "GetInterestCategoryTool",
    "GetNameFilmographyTool",
    "GetNameTool",
    "GetTitleAwardsTool",
    "GetTitleBoxOfficeTool",
    "GetTitleCreditsTool",
    "GetTitleEpisodesTool",
    "GetTitleTool",
    "ListInterestCategoriesTool",
    "ListTitlesTool",
    "SearchTitlesTool",
]
