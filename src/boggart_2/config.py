from os import environ, getenv
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class Config(BaseSettings):
    model: str = Field(default='openai:gpt-4o-mini')
    discord_token: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    system_prompt: str = Field(default='You are a helpful assistant named Boggart.')

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
