from dataclasses import dataclass, field
from typing import Optional

from discord import Message
from httpx import AsyncClient
from openai import AsyncOpenAI


@dataclass
class BoggartDeps:
    openai_client: AsyncOpenAI
    http_client: AsyncClient
    discord_message: Optional[Message] = field(default=None)
