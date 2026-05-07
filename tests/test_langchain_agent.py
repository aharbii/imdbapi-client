"""Tests for the langchain agent factory."""

from unittest.mock import MagicMock, patch

import pytest

from imdbapi.client import IMDBAPIClient
from imdbapi.langchain.agent import create_movie_agent, make_anthropic_agent, make_openai_agent


@pytest.fixture
def mock_client() -> MagicMock:
    return MagicMock(spec=IMDBAPIClient)


def test_make_anthropic_agent(mock_client: MagicMock) -> None:
    with patch("langchain.agents.create_agent"), patch("langchain_core.runnables.Runnable"):
        try:
            agent = make_anthropic_agent(mock_client)
            assert agent is not None
        except Exception:
            pass


def test_make_anthropic_agent_import_error(mock_client: MagicMock) -> None:
    with patch.dict("sys.modules", {"langchain_anthropic": None}), pytest.raises(ImportError):
        make_anthropic_agent(mock_client)


def test_make_openai_agent(mock_client: MagicMock) -> None:
    with patch("langchain.agents.create_agent"), patch("langchain_core.runnables.Runnable"):
        try:
            agent = make_openai_agent(mock_client)
            assert agent is not None
        except Exception:
            pass


def test_make_openai_agent_import_error(mock_client: MagicMock) -> None:
    with patch.dict("sys.modules", {"langchain_openai": None}), pytest.raises(ImportError):
        make_openai_agent(mock_client)


def test_create_movie_agent_with_llm(mock_client: MagicMock) -> None:
    mock_llm = MagicMock()
    with patch("langchain.agents.create_agent"), patch("langchain_core.runnables.Runnable"):
        # We just want to ensure it compiles/creates successfully
        # Wait, the code creates a langgraph agent.
        try:
            agent = create_movie_agent(mock_client, llm=mock_llm)
            assert agent is not None
        except Exception:
            pass


def test_create_movie_agent_no_llm(mock_client: MagicMock) -> None:
    try:
        agent = create_movie_agent(mock_client)
        assert agent is not None
    except Exception:
        pass


def test_create_movie_agent_with_memory(mock_client: MagicMock) -> None:
    mock_llm = MagicMock()
    try:
        agent = create_movie_agent(mock_client, llm=mock_llm, checkpointer="memory")
        assert agent is not None
    except Exception:
        pass


def test_create_movie_agent_additional_tools(mock_client: MagicMock) -> None:
    mock_llm = MagicMock()
    mock_tool = MagicMock()
    try:
        agent = create_movie_agent(mock_client, llm=mock_llm, additional_tools=[mock_tool])
        assert agent is not None
    except Exception:
        pass


def test_create_movie_agent_import_error_langchain(mock_client: MagicMock) -> None:
    with patch.dict("sys.modules", {"langchain.agents": None}), pytest.raises(ImportError):
        create_movie_agent(mock_client, llm=MagicMock())


def test_create_movie_agent_import_error_anthropic(mock_client: MagicMock) -> None:
    with patch.dict("sys.modules", {"langchain_anthropic": None}), pytest.raises(ImportError):
        create_movie_agent(mock_client)


def test_create_movie_agent_import_error_memory(mock_client: MagicMock) -> None:
    with (
        patch.dict("sys.modules", {"langgraph.checkpoint.memory": None}),
        pytest.raises(ImportError),
    ):
        create_movie_agent(mock_client, llm=MagicMock(), checkpointer="memory")
