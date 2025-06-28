import asyncio
import logging
from os import environ
from sys import stdout

from discord import Intents
from discord.ext import commands
from pydantic_ai import Agent

from boggart_2.app import Boggart, Config

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

cfg = Config()

if cfg.discord_token == 'NO_KEY':
    raise ValueError('No Discord token provided')

if not cfg.openai_api_key:
    raise ValueError('No OpenAI API key provided')

environ['OPENAI_API_KEY'] = cfg.openai_api_key

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt='You are Boggart, a witty and snarky chat agent in a Discord server.',
    output_type=str,
)

intents = Intents.default()
intents.message_content = True

bot = Boggart(
    cfg,
    agent,
    logger,
    commands.when_mentioned_or('!'),
    intents=intents,
)

logger.info('Starting bot...')


async def run_bot():
    async with bot:
        await bot.start(cfg.discord_token)


asyncio.run(run_bot())
