import uuid
from io import BytesIO

# import ipdb
from discord import File
from discord.ext import commands
from httpx import AsyncClient
from openai import AsyncOpenAI


class DalleDiscordExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = AsyncOpenAI()
        self.http_client = AsyncClient()

    @commands.command()
    async def img(self, ctx: commands.Context, *, prompt: str):
        image_response = await self.openai_client.images.generate(
            model='dall-e-3',
            prompt=prompt,
            n=1,
            size='1024x1024',
        )

        async with ctx.typing():
            image_url = image_response.data[0].url if image_response.data else None
            revised_prompt = (
                image_response.data[0].revised_prompt if image_response.data else None
            )

            # ipdb.set_trace()
            if image_url and revised_prompt:
                image_dl = await self.http_client.get(image_url)
                image_bytes = BytesIO(image_dl.content)

                await ctx.reply(
                    revised_prompt,
                    file=File(fp=image_bytes, filename=f'{uuid.uuid4()}.png'),
                )
                return

        await ctx.reply(
            'Sorry, for some reason there is no image content. Tell Chandler to fix me.'
        )
        return
