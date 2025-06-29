from typing import Optional
from uuid import uuid4

from pydantic_ai import RunContext

from boggart_2.types import BoggartDeps, FileResponse


async def generate_image(
    ctx: RunContext[BoggartDeps],
) -> Optional[FileResponse]:
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

    # ipdb.set_trace()
    if image_url and revised_prompt:
        response = FileResponse(
            message=revised_prompt,
            filename=f'i{uuid4()}.png',
            download_url=image_url,
        )

        return response

    return None
