import asyncio
import logging
from os import environ
from sys import stdout

from discord import Intents
from discord.ext import commands
from httpx import AsyncClient
from openai import AsyncOpenAI
from pydantic_ai import Agent, Tool
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

from boggart_2.tools import generate_image
from boggart_2.bot import Boggart, run_bot
from boggart_2.config import Config
from boggart_2.image_providers import create_image_provider
from boggart_2.types import Deps


def setup_logging() -> logging.Logger:
    """Configure and return a logger for the Discord bot."""
    stream_handler = logging.StreamHandler(stream=stdout)
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname}] {name}: {message}',
        date_format,
        style='{',
    )
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    return logger


def create_deps(cfg: Config, logger: logging.Logger) -> Deps:
    """Create and return dependencies for the agent."""
    if not cfg.openai_api_key:
        raise ValueError('No OpenAI API key provided')
    environ['OPENAI_API_KEY'] = cfg.openai_api_key

    openai_client = AsyncOpenAI()
    http_client = AsyncClient()

    # Create image provider with all necessary dependencies
    image_provider = create_image_provider(
        cfg=cfg,
        openai_client=openai_client,
        http_client=http_client,
    )

    return Deps(
        openai_client=openai_client,
        http_client=http_client,
        logger=logger,
        image_provider=image_provider,
    )


def create_agent(cfg: Config) -> Agent[Deps, str]:
    """Create and configure the Pydantic AI agent with tools."""
    return Agent(
        cfg.model,
        system_prompt=cfg.system_prompt,
        output_type=str,
        deps_type=Deps,
        tools=[
            Tool(generate_image, takes_ctx=True),
            duckduckgo_search_tool(),  # type: ignore - this is a default search tool that takes no dependencies
        ],
    )


def create_bot(cfg: Config, agent: Agent[Deps, str], deps: Deps) -> Boggart:
    """Create and configure the Discord bot."""
    intents = Intents.default()
    intents.message_content = True

    return Boggart(
        cfg,
        agent,
        deps,
        commands.when_mentioned_or('!'),
        intents=intents,
    )


def main():
    """Main entry point for the Boggart Discord bot."""
    logger = setup_logging()
    cfg = Config()

    if not cfg.discord_token:
        raise ValueError('No Discord token provided')

    deps = create_deps(cfg, logger)
    agent = create_agent(cfg)
    bot = create_bot(cfg, agent, deps)

    logger.info('Starting bot...')
    asyncio.run(run_bot(bot, cfg.discord_token))
