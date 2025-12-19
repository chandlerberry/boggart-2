from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Protocol

from httpx import AsyncClient
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from boggart_2.config import Config, DalleParams


@dataclass
class ImageResult:
    """Result of an image generation operation."""

    url: str
    revised_prompt: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class ImageProvider(Protocol):
    """Protocol for image generation providers."""

    async def generate(self, prompt: str) -> ImageResult:
        """Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate

        Returns:
            ImageResult containing the image URL and optional metadata

        Raises:
            ValueError: If prompt is invalid
            RuntimeError: If generation fails
        """
        ...


def parse_image_model(model_string: str) -> tuple[str, str]:
    """Parse image model string into provider and model name.

    Args:
        model_string: Format "provider:model_name" (e.g., "dalle:dall-e-3")

    Returns:
        Tuple of (provider_name, model_name)

    Raises:
        ValueError: If format is invalid
    """
    parts = model_string.split(':', 1)
    if len(parts) != 2:
        raise ValueError(
            f"Invalid image_model format: '{model_string}'. "
            f"Expected format: 'provider:model_name' (e.g., 'dalle:dall-e-3')"
        )

    provider, model = parts
    if not provider or not model:
        raise ValueError(f"Provider and model name cannot be empty in '{model_string}'")

    return provider.lower().strip(), model.strip()


class DalleImageProvider:
    """DALL-E 3 image generation provider."""

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
        size: str,
        params: Optional['DalleParams'] = None,
    ):
        """Initialize DALL-E provider.

        Args:
            client: OpenAI async client
            model: Model name (e.g., "dall-e-3")
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            params: Optional DalleParams with quality and style settings
        """
        self.client = client
        self.model = model
        self.size = size

        # Validate size parameter
        valid_sizes = {'1024x1024', '1792x1024', '1024x1792'}
        if size not in valid_sizes:
            raise ValueError(f'Invalid size: {size}. Must be one of {valid_sizes}')

        # Extract params from Pydantic model if provided
        if params:
            self.quality = params.quality
            self.style = params.style
        else:
            self.quality = 'standard'
            self.style = None

    async def generate(self, prompt: str) -> ImageResult:
        """Generate an image using DALL-E 3."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError('Prompt must be a non-empty string')

        # Build API call parameters
        api_params = {
            'model': self.model,
            'prompt': prompt,
            'n': 1,
            'size': self.size,
            'quality': self.quality,
        }

        # Only include style if it's set (not all models support it)
        if self.style:
            api_params['style'] = self.style

        response = await self.client.images.generate(**api_params)

        if not response.data:
            raise RuntimeError('DALL-E returned no image data')

        image_data = response.data[0]

        return ImageResult(
            url=image_data.url,
            revised_prompt=image_data.revised_prompt,
            metadata={
                'model': self.model,
                'size': self.size,
                'quality': self.quality,
                'style': self.style,
            },
        )


def create_image_provider(
    cfg: 'Config',
    openai_client: AsyncOpenAI,
    http_client: AsyncClient,
) -> ImageProvider:
    """Factory function to create an image provider based on configuration.

    Args:
        cfg: Application configuration
        openai_client: OpenAI client for DALL-E provider
        http_client: HTTP client for REST API providers

    Returns:
        Configured image provider instance

    Raises:
        ValueError: If provider is unknown or required config is missing
    """
    provider_name, model_name = parse_image_model(cfg.image_model)

    if provider_name == 'dalle':
        return DalleImageProvider(
            client=openai_client,
            model=model_name,
            size=cfg.image_size,
            params=cfg.dalle_params,
        )
    else:
        raise ValueError(
            f'Unknown image provider: {provider_name}. Available providers: dalle'
        )
