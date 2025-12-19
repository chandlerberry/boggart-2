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

**Entry Point (`main.py`)**: Orchestrates initialization of the entire application. Contains factory functions for creating dependencies, agent, and bot instances. The `main()` function sets up logging, loads configuration, creates the Pydantic AI agent with tools, initializes dependencies, and starts the bot. This is where all components are wired together.

**Package Initialization (`__init__.py`)**: Clean package exports defining the public API. Allows safe importing of components without side effects.

**Boggart Bot (`bot.py`)**: Discord bot implementation extending `discord.ext.commands.Bot`. Listens for mentions and command prefix ('!'). When mentioned, it passes messages to the Pydantic AI agent and returns responses to Discord. Manages the async lifecycle of the bot.

**Tools (`tools.py`)**: Defines custom tools for the Pydantic AI agent. Currently implements `generate_image()` which uses the configured image provider to generate images and posts them back to Discord via the message context stored in dependencies.

**Image Providers (`image_providers.py`)**: Pluggable provider system for image generation. Defines `ImageProvider` protocol for clean abstraction, `ImageResult` dataclass for structured results, and provider implementations (currently DALL-E 3). The `create_image_provider()` factory function instantiates providers based on configuration. Provider selection uses a unified model string format (e.g., `"dalle:dall-e-3"`).

**Configuration (`config.py`)**: Uses Pydantic Settings to load configuration from a YAML file (default: `~/boggart.yml`, override with `BOGGART_CONFIG_PATH`). Manages API keys, model selection, system prompt, and image generation settings. Includes provider-specific Pydantic models (e.g., `DalleParams`) for type-safe validation.

**Dependencies (`types.py`)**: Defines the `Deps` dataclass used for dependency injection throughout the agent. Contains shared clients (OpenAI, HTTP), logger, image provider instance, and optional Discord message context for tool use.

### Data Flow

1. Discord message mentioning bot → `Boggart.on_message()` in `bot.py`
2. Message content passed to Pydantic AI agent with dependencies
3. Agent processes message using configured LLM model and available tools
4. Tools access shared dependencies via `RunContext[Deps]`:
   - Image generation: uses `image_provider` to generate images via configured provider
   - Web search: uses DuckDuckGo search tool
5. Image provider generates image and returns structured `ImageResult`
6. Tool downloads image and posts to Discord with metadata
7. Agent response returned to Discord channel

### Tool System

Tools are registered with the Pydantic AI agent in the `create_agent()` factory function in `main.py`. Custom tools (in `tools.py`) receive `RunContext[Deps]` for accessing shared resources like the image provider, HTTP client, and Discord message context. The DuckDuckGo search tool is imported from `pydantic_ai.common_tools`.

### Image Provider System

The image provider system uses a pluggable architecture for extensibility:

- **Protocol-based abstraction**: `ImageProvider` protocol defines the interface without forced inheritance
- **Factory pattern**: `create_image_provider()` instantiates providers based on parsed model string
- **Model string format**: Unified `"provider:model_name"` format (e.g., `"dalle:dall-e-3"`)
- **Generic parameters**: Provider-agnostic settings like `image_size` work across all providers
- **Provider-specific params**: Validated Pydantic models (e.g., `DalleParams`) for type safety
- **Dependency injection**: Providers receive only required dependencies (DALL-E uses OpenAI client, REST providers use HTTP client)

### Project Structure

```
src/boggart_2/
├── __init__.py          # Package exports (public API)
├── main.py              # Entry point with factory functions
├── bot.py               # Discord bot implementation
├── tools.py             # Custom agent tools
├── image_providers.py   # Image provider abstraction and implementations
├── config.py            # Configuration management
└── types.py             # Type definitions and dependencies
```

## Configuration

The bot requires a YAML configuration file with:

### Required Settings
- `discord_token`: Discord bot token
- `openai_api_key`: OpenAI API key

### Optional Settings
- `model`: LLM model string, defaults to `openai:gpt-4o-mini`
- `anthropic_api_key`: Anthropic API key if using Claude models
- `system_prompt`: Agent personality and behavior instructions

### Image Generation Settings
- `image_model`: Image provider and model in format `"provider:model_name"`, defaults to `"dalle:dall-e-3"`
- `image_size`: Generic image size parameter, defaults to `"1024x1024"`
- `dalle_params`: Optional DALL-E specific parameters (Pydantic model)
  - `quality`: Image quality - `"standard"` or `"hd"` (default: `"standard"`)
  - `style`: Image style - `"vivid"` or `"natural"` (optional)

### Example Configuration

```yaml
# Required
discord_token: "your-discord-token"
openai_api_key: "your-openai-key"

# Optional - LLM
model: "openai:gpt-4o-mini"
system_prompt: "You are a helpful assistant named Boggart."

# Optional - Image generation
image_model: "dalle:dall-e-3"
image_size: "1792x1024"
dalle_params:
  quality: "hd"
  style: "vivid"
```

## Code Style

- Python 3.13+
- Ruff formatter with single quotes, 88 character line length
- Type hints required (uses Pyright for type checking)
