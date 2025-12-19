from discord.ext import commands
from discord.message import Message
from pydantic_ai import Agent

from boggart_2.config import Config
from boggart_2.types import Deps


class Boggart(commands.Bot):
    def __init__(
        self,
        cfg: Config,
        agent: Agent[Deps, str],
        deps: Deps,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.agent = agent
        self.deps = deps

    async def on_message(self, message: Message):
        # Don't respond to bot messages
        if message.author == self.user:
            return

        if self.user in message.mentions:
            async with message.channel.typing():
                self.deps.discord_message = message
                agent_run = await self.agent.run(message.content, deps=self.deps)

                self.deps.logger.info(
                    f'Recieved response from agent: {agent_run.output[:30]}...'
                )
                await message.channel.send(agent_run.output)
                self.deps.discord_message = None

        if message.content[0] == '!':
            await self.process_commands(message)


async def run_bot(bot: Boggart, token: str):
    async with bot:
        await bot.start(token)
