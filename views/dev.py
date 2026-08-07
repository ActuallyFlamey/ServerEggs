import os

import discord
import dotenv

dotenv.load_dotenv()

DEVELOPER_GUILD = discord.Object(id=os.getenv("DEVELOPER_GUILD_ID"))
DEV_IDS = [int(dev_id) for dev_id in os.getenv("DEV_IDS").split(", ")]

class ReportActions(discord.ui.View):
    def __init__(self, report):
        super().__init__(timeout=None)

        self.report = report

    async def delete_reports(self, ctx: discord.Interaction, egg):
        all_reports = await egg.reports.all()

        for r in all_reports:
            if r.log_message_id:
                try:
                    msg = ctx.channel.get_partial_message(r.log_message_id)
                    await msg.delete()
                except discord.HTTPException:
                    pass 

            await r.delete()

    async def interaction_check(self, ctx: discord.Interaction):
        if ctx.user.id not in DEV_IDS:
            await ctx.response.send_message(content="Not allowed.", ephemeral=True)
            return False
        
        return True
    
    @discord.ui.button(label="Ignore", style=discord.ButtonStyle.secondary)
    async def ignore(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg

        await self.delete_reports(ctx, egg)
    
    @discord.ui.button(label="Mark NSFW", style=discord.ButtonStyle.primary)
    async def mark_nsfw(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg

        if not egg.nsfw:
            egg.nsfw = True
            await egg.save(update_fields=["nsfw"])
        
        await self.delete_reports(ctx, egg)
    
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg

        await egg.delete()

        await self.delete_reports(ctx, egg)
    
    @discord.ui.button(label="Delete and Ban", style=discord.ButtonStyle.danger)
    async def delete_ban(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.defer()

        egg = await self.report.egg
        creator = await egg.creator

        creator.banned = True
        await creator.save(update_fields=["banned"])

        await egg.delete()

        await self.delete_reports(ctx, egg)