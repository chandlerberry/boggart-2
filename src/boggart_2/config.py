from dataclasses import dataclass, field
from logging import Logger
from os import environ, getenv
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from discord import Message
from httpx import AsyncClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

if TYPE_CHECKING:
    from boggart_2.image_providers import ImageProvider


@dataclass
class MemoryDeps: ...


@dataclass
class Deps:
    openai_client: AsyncOpenAI
    http_client: AsyncClient
    logger: Logger
    image_provider: 'ImageProvider'
    discord_message: Optional[Message] = field(default=None)


class DalleParams(BaseModel):
    """DALL-E specific parameters."""

    quality: str = Field(default='standard', pattern='^(standard|hd)$')
    style: Optional[str] = Field(default=None, pattern='^(vivid|natural)$')


class Config(BaseSettings):
    model: str = Field(
        default='anthropic/claude-haiku-4.5',
        description='Model name as detailed in the Vercel AI Gateway model list',
    )
    discord_token: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    vercel_ai_gateway_api_key: str = Field()
    system_prompt: str = Field(default='You are a helpful assistant named Boggart.')

    # Image generation configuration
    image_model: str = Field(default='dalle:dall-e-3')
    image_size: str = Field(default='1024x1024')
    dalle_params: Optional[DalleParams] = Field(default=None)

    model_config = SettingsConfigDict(
        yaml_file=Path(Path.home(), 'boggart.yml')
        if not getenv('BOGGART_CONFIG_PATH')
        else Path(environ['BOGGART_CONFIG_PATH']),
        yaml_file_encoding='utf-8',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        super().settings_customise_sources(
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
        return (YamlConfigSettingsSource(settings_cls),)
