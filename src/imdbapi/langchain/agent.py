"""LangGraph ReAct agent factory for movie intelligence tasks.

Creates a ready-to-use agent that reasons over IMDb data using the full
tool suite exposed by this package.  The agent follows the ReAct loop:

    Thought → Tool call → Observation → Thought → … → Final answer

The agent is model-agnostic: pass any LangChain ``BaseChatModel`` instance.
Provider-specific helpers (``make_anthropic_agent``, ``make_openai_agent``)
are included for convenience.

Usage::

    from imdbapi import IMDBAPIClient
    from imdbapi.langchain import create_movie_agent

    async with IMDBAPIClient() as client:
        agent = create_movie_agent(client)          # uses Claude by default
        result = await agent.ainvoke(
            {"messages": [("human", "What year was Inception released?")]}
        )
        print(result["messages"][-1].content)

Multi-turn conversation::

    config = {"configurable": {"thread_id": "session-42"}}
    async with IMDBAPIClient() as client:
        agent = create_movie_agent(client, checkpointer="memory")
        async for chunk in agent.astream(
            {"messages": [("human", "Tell me about The Dark Knight")]},
            config=config,
            stream_mode="values",
        ):
            print(chunk["messages"][-1].content)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .tools import create_imdb_tools

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.graph.graph import CompiledGraph

    from ..client import IMDBAPIClient

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

MOVIE_AGENT_SYSTEM_PROMPT = """\
You are a knowledgeable movie and television expert assistant powered by real-time \
IMDb data.

## Your capabilities
You have access to a suite of IMDb tools that let you look up:
- Movies, TV shows, mini-series, and other titles — ratings, plots, genres, runtime
- Full cast & crew lists — directors, writers, actors and the characters they play
- Biographical data for any actor, director, or other film professional
- Box office figures — domestic gross, worldwide gross, opening weekend, production budget
- Award nominations and wins (Oscars, Golden Globes, etc.)
- Episode lists and per-episode ratings for TV series
- Genre/interest taxonomy for filtering

## How to reason
1. **Search first** — when the user mentions a title by name, call `search_titles` \
to obtain its IMDb ID before calling any other tool.
2. **Chain tools** — use the `id` fields in one result to drive the next call \
(e.g. use a director's `nameId` from `get_title` to call `get_name`).
3. **Be precise** — if the user asks for a specific piece of information (rating, \
budget, cast), fetch only what is needed rather than dumping entire records.
4. **Handle ambiguity** — if a search returns multiple results with similar names, \
clarify with the user or present the top candidates with their years and types.
5. **Stay honest** — if a tool returns an error or an empty result, say so clearly \
rather than hallucinating data.

## Response style
- Answer in natural, conversational language — don't regurgitate raw JSON.
- Use bullet points or tables when listing multiple items (cast, episodes, awards).
- Include the IMDb rating (score / votes) whenever presenting a title.
- For financial figures, format with commas and the currency symbol (e.g. $58,000,000).
- For dates, use "Month DD, YYYY" format when all components are available.
"""

# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------


def create_movie_agent(
    client: IMDBAPIClient,
    *,
    llm: BaseChatModel | None = None,
    model_name: str = "claude-opus-4-6",
    checkpointer: Any = None,
    additional_tools: list[Any] | None = None,
) -> CompiledGraph:
    """Create a LangGraph ReAct agent wired to all IMDb tools.

    Parameters
    ----------
    client:
        An open :class:`~imdbapi.client.IMDBAPIClient` instance.
    llm:
        A LangChain ``BaseChatModel``.  When ``None``, a
        ``ChatAnthropic`` instance using ``model_name`` is created
        automatically (requires ``langchain-anthropic`` to be installed).
    model_name:
        Model identifier passed to ``ChatAnthropic`` when ``llm`` is ``None``.
        Ignored when ``llm`` is provided explicitly.
    checkpointer:
        LangGraph checkpointer for multi-turn memory.  Pass
        ``"memory"`` to use the built-in in-memory checkpointer, or
        supply any :class:`~langgraph.checkpoint.base.BaseCheckpointSaver`
        instance.  Defaults to ``None`` (no memory across turns).
    additional_tools:
        Extra LangChain tools to register alongside the IMDb tools.

    Returns
    -------
    CompiledGraph
        A compiled LangGraph agent ready for ``.invoke()`` / ``.ainvoke()``.

    Raises
    ------
    ImportError
        If ``langchain-anthropic`` is not installed and ``llm`` is ``None``.

    Examples
    --------
    Basic one-shot query::

        async with IMDBAPIClient() as client:
            agent = create_movie_agent(client)
            out = await agent.ainvoke(
                {"messages": [("human", "Who directed The Matrix?")]}
            )
            print(out["messages"][-1].content)

    With a custom OpenAI model::

        from langchain_openai import ChatOpenAI
        async with IMDBAPIClient() as client:
            agent = create_movie_agent(
                client,
                llm=ChatOpenAI(model="gpt-4o"),
            )

    With persistent memory (multi-turn)::

        async with IMDBAPIClient() as client:
            agent = create_movie_agent(client, checkpointer="memory")
            config = {"configurable": {"thread_id": "user-123"}}
            await agent.ainvoke(
                {"messages": [("human", "Tell me about Interstellar")]}, config
            )
            await agent.ainvoke(
                {"messages": [("human", "How much did it gross?")]}, config
            )
    """
    # Lazy imports — these are optional dependencies
    try:
        from langgraph.prebuilt import create_react_agent
    except ImportError as exc:
        raise ImportError(
            "langgraph is required. Install it with: uv sync --group agents-anthropic"
        ) from exc

    if llm is None:
        try:
            from langchain_anthropic import ChatAnthropic

            llm = ChatAnthropic(model=model_name)  # type: ignore[assignment]
        except ImportError as exc:
            raise ImportError(
                "langchain-anthropic is required when llm=None. "
                "Install it with: uv sync --group agents-anthropic\n"
                "Or provide an explicit llm= parameter."
            ) from exc

    tools = create_imdb_tools(client)
    if additional_tools:
        tools = tools + additional_tools

    # Resolve "memory" shorthand
    resolved_checkpointer = checkpointer
    if checkpointer == "memory":
        try:
            from langgraph.checkpoint.memory import MemorySaver

            resolved_checkpointer = MemorySaver()
        except ImportError as exc:
            raise ImportError(
                "langgraph.checkpoint.memory is required for in-memory checkpointing."
            ) from exc

    return create_react_agent(
        llm,
        tools,
        state_modifier=MOVIE_AGENT_SYSTEM_PROMPT,
        checkpointer=resolved_checkpointer,
    )


# ---------------------------------------------------------------------------
# Provider-specific convenience helpers
# ---------------------------------------------------------------------------


def make_anthropic_agent(
    client: IMDBAPIClient,
    model: str = "claude-opus-4-6",
    **kwargs: Any,
) -> CompiledGraph:
    """Convenience wrapper that creates a Claude-backed movie agent.

    Parameters
    ----------
    client:
        An open :class:`~imdbapi.client.IMDBAPIClient` instance.
    model:
        Anthropic model identifier.  Defaults to ``"claude-opus-4-6"``.
    **kwargs:
        Additional keyword arguments forwarded to :func:`create_movie_agent`.

    Returns
    -------
    CompiledGraph
    """
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError as exc:
        raise ImportError(
            "langchain-anthropic is required. Install it with: uv sync --group agents-anthropic"
        ) from exc

    llm = ChatAnthropic(model=model)
    return create_movie_agent(client, llm=llm, **kwargs)


def make_openai_agent(
    client: IMDBAPIClient,
    model: str = "gpt-4o",
    **kwargs: Any,
) -> CompiledGraph:
    """Convenience wrapper that creates a GPT-backed movie agent.

    Parameters
    ----------
    client:
        An open :class:`~imdbapi.client.IMDBAPIClient` instance.
    model:
        OpenAI model identifier.  Defaults to ``"gpt-4o"``.
    **kwargs:
        Additional keyword arguments forwarded to :func:`create_movie_agent`.

    Returns
    -------
    CompiledGraph
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "langchain-openai is required. Install it with: uv sync --group agents-openai"
        ) from exc

    llm = ChatOpenAI(model=model)
    return create_movie_agent(client, llm=llm, **kwargs)
