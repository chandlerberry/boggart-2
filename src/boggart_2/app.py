import logging
from os import environ
from pathlib import Path
from typing import Optional

from discord import Intents
from discord.ext import commands
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from boggart_2.openai import OpenAIDiscordExtension


class Config(BaseSettings):
    discord_token: str = Field(default='NO_KEY')
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)

    # todo: set config path with environment variable
    model_config = SettingsConfigDict(
        yaml_file=Path(Path.home(), 'boggart.yml'),
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


class Boggart(commands.Bot):
    def __init__(self, cfg: Config, logger: logging.Logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.logger = logger

        self.command_prefix = '!'

    async def setup_hook(self) -> None:
        if self.cfg.openai_api_key:
            self.logger.info('Loading OpenAI extension...')
            environ['OPENAI_API_KEY'] = self.cfg.openai_api_key
            await self.add_cog(OpenAIDiscordExtension(self))
            self.logger.info('OpenAI extension loaded.')

        if self.cfg.anthropic_api_key:
            self.logger.info('Loading Anthropic extension...')
            self.logger.info('Anthropic extension not implemented yet, ignoring...')
            # environ['ANTHROPIC_API_KEY'] = self.cfg.anthropic_api_key
            # await self.add_cog(AnthropicDiscordExtension(self))
            # logger.info('Anthropic extension loaded.')


async def run_bot(cfg: Config, logger: logging.Logger):
    if cfg.discord_token == 'NO_KEY':
        raise ValueError('No Discord token provided')

    intents = Intents.default()
    intents.message_content = True

    async with Boggart(
        cfg,
        logger,
        commands.when_mentioned,
        intents=intents,
    ) as boggart:
        logger.info('Starting bot...')
        await boggart.start(cfg.discord_token)
