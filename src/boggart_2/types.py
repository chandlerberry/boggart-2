from dataclasses import dataclass

from httpx import AsyncClient
from openai import AsyncOpenAI
from pydantic import BaseModel


@dataclass
class BoggartDeps:
    openai_client: AsyncOpenAI
    http_client: AsyncClient


class FileResponse(BaseModel):
    message: str
    filename: str
    download_url: str
