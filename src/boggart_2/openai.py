from discord.ext import commands


class OpenAIDiscordExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dalle(self, ctx):
        await ctx.send('Recieved DALLE Request')
