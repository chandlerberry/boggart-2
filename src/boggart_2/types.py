from dataclasses import dataclass, field
from logging import Logger
from typing import TYPE_CHECKING, Optional

from discord import Message
from httpx import AsyncClient
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from boggart_2.image_providers import ImageProvider


@dataclass
class Deps:
    openai_client: AsyncOpenAI
    http_client: AsyncClient
    logger: Logger
    image_provider: 'ImageProvider'
    discord_message: Optional[Message] = field(default=None)
