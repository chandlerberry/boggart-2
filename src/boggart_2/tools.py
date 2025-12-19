from io import BytesIO
from uuid import uuid4

from discord import File
from pydantic_ai import RunContext

from boggart_2.types import Deps


async def generate_image(ctx: RunContext[Deps]) -> bool:
    """Generate an image using the configured image provider.

    The image is generated via the provider, downloaded, and posted to Discord
    with any revised prompt or metadata from the provider.
    """
    if not isinstance(ctx.prompt, str):
        raise TypeError('Expected type string for image generation request')

    try:
        # Generate image using provider
        result = await ctx.deps.image_provider.generate(ctx.prompt)

        # Download and post to Discord
        if result.url and ctx.deps.discord_message:
            response = await ctx.deps.http_client.get(result.url)

            # Use revised_prompt if available
            message_content = result.revised_prompt if result.revised_prompt else None

            await ctx.deps.discord_message.reply(
                message_content,
                file=File(
                    fp=BytesIO(response.read()),
                    filename=f'{uuid4()}.png',
                ),
            )
            return True

    except (ValueError, RuntimeError) as e:
        # Log provider errors but don't crash
        ctx.deps.logger.error(f'Image generation failed: {e}')
        if ctx.deps.discord_message:
            await ctx.deps.discord_message.reply(
                f'Sorry, image generation failed: {str(e)}'
            )
        return False

    return False
