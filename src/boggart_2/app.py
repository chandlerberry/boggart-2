import logging

from discord.ext import commands
from discord.message import Message
from pydantic_ai import Agent

from boggart_2.config import Config
from boggart_2.types import BoggartDeps


class Boggart(commands.Bot):
    def __init__(
        self,
        cfg: Config,
        agent: Agent[BoggartDeps, str],
        deps: BoggartDeps,
        logger: logging.Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.logger = logger
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

                self.logger.info(
                    f'Recieved response from agent: {agent_run.output[:30]}...'
                )
                await message.channel.send(agent_run.output)
                self.deps.discord_message = None

        if message.content[0] == '!':
            await self.process_commands(message)
