from dataclasses import dataclass, field
from logging import Logger
from typing import Optional

from discord import Message
from httpx import AsyncClient
from openai import AsyncOpenAI


@dataclass
class Deps:
    openai_client: AsyncOpenAI
    http_client: AsyncClient
    logger: Logger
    discord_message: Optional[Message] = field(default=None)
