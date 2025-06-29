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
from boggart_2.app import Boggart
from boggart_2.config import Config
from boggart_2.types import BoggartDeps, FileResponse

cfg = Config()

if cfg.discord_token == 'NO_KEY':
    raise ValueError('No Discord token provided')

if not cfg.openai_api_key:
    raise ValueError('No OpenAI API key provided')

environ['OPENAI_API_KEY'] = cfg.openai_api_key

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=cfg.system_prompt,
    output_type=[str, FileResponse],
    deps_type=BoggartDeps,
    # Getting a type checker warning from pyright that this is not valid, but it works. I think the type annotation needs to be adjusted.
    tools=[Tool(generate_image, takes_ctx=True), duckduckgo_search_tool()],
)

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

# initialize client dependencies
deps = BoggartDeps(openai_client=AsyncOpenAI(), http_client=AsyncClient())

# create bot
bot = Boggart(
    cfg,
    agent,
    deps,
    logger,
    commands.when_mentioned_or('!'),
    intents=intents,
)


async def run_bot():
    async with bot:
        await bot.start(cfg.discord_token)


logger.info('Starting bot...')
asyncio.run(run_bot())
