import logging
from pathlib import Path
from typing import Optional

from discord.ext import commands
from pydantic import Field
from pydantic_ai import Agent
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from boggart_2.openai import DalleDiscordExtension


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
    def __init__(
        self,
        cfg: Config,
        agent: Agent,
        logger: logging.Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.logger = logger
        self.agent = agent

        self.command_prefix = '!'

    async def setup_hook(self) -> None:
        if self.cfg.openai_api_key:
            self.logger.info('Loading DALLE extension...')
            await self.add_cog(DalleDiscordExtension(self))
            self.logger.info('DALLE extension loaded.')

        if self.cfg.anthropic_api_key:
            self.logger.info('Loading Anthropic extension...')
            self.logger.info('Anthropic extension not implemented yet, ignoring...')
            # environ['ANTHROPIC_API_KEY'] = self.cfg.anthropic_api_key
            # await self.add_cog(AnthropicDiscordExtension(self))
            # logger.info('Anthropic extension loaded.')

    async def on_message(self, message):
        # Don't respond to bot messages
        if message.author == self.user:
            return

        if self.user in message.mentions:
            async with message.channel.typing():
                agent_run = await self.agent.run(message.content)
                await message.reply(agent_run.output)
