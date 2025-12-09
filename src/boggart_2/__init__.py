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

from boggart_2.agent import generate_image
from boggart_2.app import Boggart, run_bot
from boggart_2.config import Config
from boggart_2.types import Deps

# configure logging
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

intents = Intents.default()
intents.message_content = True

cfg = Config()

if not cfg.discord_token:
    raise ValueError('No Discord token provided')

if not cfg.openai_api_key:
    raise ValueError('No OpenAI API key provided')
environ['OPENAI_API_KEY'] = cfg.openai_api_key

# review pricing https://platform.openai.com/docs/pricing
agent = Agent(
    cfg.model,
    system_prompt=cfg.system_prompt,
    output_type=str,
    deps_type=Deps,
    tools=[
        Tool(generate_image, takes_ctx=True),
        duckduckgo_search_tool(),  # type: ignore - this is a default search tool that takes no dependencies
    ],
)

deps = Deps(
    openai_client=AsyncOpenAI(),
    http_client=AsyncClient(),
    logger=logger,
)

bot = Boggart(
    cfg,
    agent,
    deps,
    commands.when_mentioned_or('!'),
    intents=intents,
)

logger.info('Starting bot...')
asyncio.run(run_bot(bot, cfg.discord_token))
