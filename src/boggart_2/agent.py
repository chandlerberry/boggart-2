from io import BytesIO
from uuid import uuid4

from discord import File
from pydantic_ai import RunContext

from boggart_2.types import BoggartDeps


async def generate_image(ctx: RunContext[BoggartDeps]) -> bool:
    """
    Generate an image using DALLE-3 via the OpenAI API
    """
    if not isinstance(ctx.prompt, str):
        raise TypeError('Expected type string for DALLE image generation request')

    image_response = await ctx.deps.openai_client.images.generate(
        model='dall-e-3',
        prompt=ctx.prompt,
        n=1,
        size='1024x1024',
    )

    image_url = image_response.data[0].url if image_response.data else None

    revised_prompt = (
        image_response.data[0].revised_prompt if image_response.data else None
    )

    if image_url and revised_prompt and ctx.deps.discord_message:
        file = await ctx.deps.http_client.get(image_url)

        # todo: prevent model from overriding revised prompt from the dalle output
        await ctx.deps.discord_message.reply(
            revised_prompt,
            file=File(
                fp=BytesIO(file.read()),
                filename=f'{uuid4()}.png',
            ),
        )
        return True

    return False
