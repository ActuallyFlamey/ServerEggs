import itertools

import discord
from discord.ext import commands, tasks


class Presence(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.activities = itertools.cycle([
            "/help for more info!",
            "I am behind the tree...",
            "Could I offer you an /egg in these trying times?",
            "Eggify any message by right-clicking or pressing it!",
            "Giving random Eggs in {guilds} servers!",
            "Enjoying this public beta?",
            "Surprisingly not about DELTARUNE.",
            "I like my Eggs open-source.",
            "Support at discord.gg/G9vfEZGZnT",
            "Gambling without any stakes! So awesome!"
        ])

        self.update_presence.start()
    
    @tasks.loop(seconds=30)
    async def update_presence(self):
        presence = next(self.activities)

        await self.bot.change_presence(activity=discord.CustomActivity(name=presence.format(guilds=len(self.bot.guilds))))
    
    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Presence(bot))