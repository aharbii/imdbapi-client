# Changelog — imdbapi-client

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

<!-- Add new changes here under the appropriate subsection. -->
<!-- Subsections: Added, Changed, Deprecated, Removed, Fixed, Security -->

---

## [0.1.0] — 2026-03-22

### Added

- `IMDBAPIClient` — fully async context manager with `httpx` transport
- Automatic retry with exponential backoff via `tenacity` (5xx, timeout, connection errors)
- **Titles** endpoint group (18 operations): `get`, `list`, `list_pages`, `batch_get`,
  `get_credits`, `get_release_dates`, `get_akas`, `get_seasons`, `get_episodes`,
  `get_episodes_pages`, `get_images`, `get_videos`, `get_award_nominations`,
  `get_parents_guide`, `get_certificates`, `get_company_credits`, `get_box_office`
- **Names** endpoint group (7 operations): `get`, `batch_get`, `get_images`,
  `get_filmography`, `get_filmography_pages`, `get_relationships`, `get_trivia`
- **Interests** endpoint group (2 operations): `list_categories`, `get`
- **Search** endpoint group (1 operation): `titles`
- **Charts** endpoint group (2 operations): `starmeter`, `starmeter_pages`
- `AsyncPaginator` — generic async iterator for any paginated list endpoint
- Full Pydantic v2 model layer: `Title`, `Name`, `Interest`, `Credit`, `Episode`,
  `BoxOffice`, `Image`, `Rating`, `Country`, `Money`, and more
- Exception hierarchy: `IMDBAPIError`, `IMDBAPIHTTPError`, `IMDBAPIConnectionError`,
  `IMDBAPITimeoutError`, `IMDBAPIValidationError`
- LangChain integration (optional): `create_movie_agent()`, `create_imdb_tools()`
  — installable via `agents-anthropic` or `agents-openai` dependency groups
- PEP 561 `py.typed` marker — fully typed package
- Full test suite using `respx` HTTP mocks — zero real API calls
- Multi-stage Docker image (standalone build context)
- `Jenkinsfile` — lint → test → build/push pipeline
- `examples/langchain_agent_example.py` — 5 demos: one-shot, multi-turn, streaming,
  custom tool subset, OpenAI variant
