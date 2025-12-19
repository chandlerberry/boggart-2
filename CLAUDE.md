# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Boggart is a Discord chat bot powered by Pydantic AI that integrates LLM agents with Discord. The bot responds when mentioned in Discord channels, using tools like DuckDuckGo search and DALL-E 3 image generation.

## Development Commands

### Environment Setup
```bash
# Install dependencies (uses uv package manager)
uv sync --locked

# Run the bot
uv run boggart
```

### Code Quality
```bash
# Format code with Ruff
uv run ruff format

# Lint code with Ruff
uv run ruff check
```

### Docker
```bash
# Build container
docker build -t boggart:local .

# Run container (requires BOGGART_CONFIG_PATH env var)
docker run --name boggart -d --rm -v $BOGGART_CONFIG_PATH:/config.yml boggart:local
```

## Architecture

### Core Components

**Entry Point (`__init__.py`)**: Orchestrates initialization of the entire application. Sets up logging, loads configuration, creates the Pydantic AI agent with tools, initializes dependencies, and starts the bot. This is where all components are wired together.

**Boggart Bot (`app.py`)**: Discord bot implementation extending `discord.ext.commands.Bot`. Listens for mentions and command prefix ('!'). When mentioned, it passes messages to the Pydantic AI agent and returns responses to Discord. Manages the async lifecycle of the bot.

**Agent (`agent.py`)**: Defines custom tools for the Pydantic AI agent. Currently implements `generate_image()` which uses DALL-E 3 to generate images and posts them back to Discord via the message context stored in dependencies.

**Configuration (`config.py`)**: Uses Pydantic Settings to load configuration from a YAML file (default: `~/boggart.yml`, override with `BOGGART_CONFIG_PATH`). Manages API keys, model selection, and system prompt.

**Dependencies (`types.py`)**: Defines the `Deps` dataclass used for dependency injection throughout the agent. Contains shared clients (OpenAI, HTTP), logger, and optional Discord message context for tool use.

### Data Flow

1. Discord message mentioning bot → `Boggart.on_message()` in `app.py`
2. Message content passed to Pydantic AI agent with dependencies
3. Agent processes message using configured LLM model and available tools
4. Tools (image generation, web search) access shared dependencies via `RunContext`
5. Agent response returned to Discord channel

### Tool System

Tools are registered with the Pydantic AI agent in `__init__.py`. Custom tools (in `agent.py`) receive `RunContext[Deps]` for accessing shared resources like the OpenAI client and Discord message context. The DuckDuckGo search tool is imported from `pydantic_ai.common_tools`.

## Configuration

The bot requires a YAML configuration file with:
- `discord_token`: Discord bot token (required)
- `openai_api_key`: OpenAI API key (required)
- `model`: LLM model string, defaults to `openai:gpt-4o-mini` (optional)
- `anthropic_api_key`: Anthropic API key if using Claude models (optional)
- `system_prompt`: Agent personality and behavior instructions (optional)

## Code Style

- Python 3.13+
- Ruff formatter with single quotes, 88 character line length
- Type hints required (uses Pyright for type checking)
