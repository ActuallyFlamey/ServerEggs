import os
import random

import discord
from discord import app_commands as app
from discord.ext import commands

import utils
import views
from schema import Egg, Guild, User


class Eggs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app.command(name="create", description="create_description")
    @app.rename(text="create_text", attachment="create_attachment", nsfw="create_nsfw")
    @app.describe(text="create_text_description", attachment="create_attachment_description", nsfw="create_nsfw_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def create(self, ctx: discord.Interaction, text: str | None, attachment: discord.Attachment | None, nsfw: bool=False):
        await ctx.response.defer()

        lines = await self.bot.get_line("eggs/create", ctx)

        is_channel_nsfw = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False
        if nsfw and not is_channel_nsfw:
            await ctx.followup.send(lines["no_nsfw"])
            return

        user, _ = await User.get_or_create(id=ctx.user.id)

        if user.banned:
            await ctx.followup.send(lines["banned"])
            return

        if text is None and attachment is None:
            await ctx.followup.send(lines["empty"])
            return

        if text:
            text = text.strip()
            if text == "": text = None

        attach_path = None
        attach_hash = None

        if attachment:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                attach_path, attach_hash = await utils.process_attachment(attachment)
            else:
                await ctx.followup.send(lines["images_only"])
                return
        
        existing = await Egg.filter(text=text, attach_hash=attach_hash).first()

        if existing:
            if attach_path and os.path.exists(attach_path):
                os.remove(attach_path)
            
            await ctx.followup.send(lines["duplicate"].format(existing.id))
            return
        
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        egg = await Egg.create(
            text=text,
            attach_path=attach_path,
            attach_hash=attach_hash,
            nsfw=nsfw,
            creator=user,
            origin=guild
        )
        
        e = discord.Embed(
            title=lines["success"]["title"].format(egg.id) + (" 🌶️" if egg.nsfw else ""),
            color=discord.Color.blurple() if not egg.nsfw else discord.Color.red(),
            description=egg.text
        )
        await utils.brand_embed(e, self.bot, ctx)

        file = utils.show_attachment(egg, e)
        
        await ctx.followup.send(embed=e, file=file if file is not None else discord.utils.MISSING)
    
    @app.command(name="get", description="get_description")
    @app.rename(id="get_id", only_nsfw="get_only-nsfw")
    @app.describe(id="get_id_description", only_nsfw="get_only-nsfw_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def get(self, ctx: discord.Interaction, id: int | None=None, only_nsfw: bool | None=None):
        await ctx.response.defer()

        lines = await self.bot.get_line("eggs/get", ctx)

        is_channel_nsfw = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False

        if id is not None:
            egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

            if not egg:
                await ctx.followup.send(lines["not_found"].format(id))
                return
            
            if egg.nsfw and not is_channel_nsfw:
                await ctx.followup.send(lines["nsfw_id_in_sfw"])
                return
        else:
            eggs = Egg.all()

            if only_nsfw:
                if not is_channel_nsfw:
                    await ctx.followup.send(lines["nsfw_in_sfw"])
                    return
                
                eggs = eggs.filter(nsfw=True)
            elif not is_channel_nsfw:
                eggs = eggs.filter(nsfw=False)
        
            count = await eggs.count()

            if count == 0:
                await ctx.followup.send(lines["no_egg"])
                return

            randegg = random.randint(0, count - 1)
            egg = await eggs.offset(randegg).prefetch_related("creator", "origin").first()

        creator = self.bot.get_user(egg.creator.id)

        if creator is None:
            try:
                creator = await self.bot.fetch_user(egg.creator.id)
            except discord.NotFound:
                creator = None

        origin = self.bot.get_guild(egg.origin.id)
        
        e = discord.Embed(
            title=lines["eggn"].format(egg.id) + (" 🌶️" if egg.nsfw else ""),
            color=discord.Color.blurple() if not egg.nsfw else discord.Color.red(),
            description=egg.text
        )
        e.add_field(
            name=lines["creator"],
            value=f"**{creator.display_name}** ({creator.name})" if creator is not None else lines["unknown_creator"].format(egg.creator.id),
            inline=False
        )
        e.add_field(
            name=lines["origin"],
            value=f"""
                **Name**: {origin.name}
                {f"**Description**: {egg.origin.description}" if egg.origin.description is not None else ""}
            """ if origin is not None else lines["unknown_origin"].format(egg.origin.id),
            inline=False
        )
        await utils.brand_embed(e, self.bot, ctx)

        file = utils.show_attachment(egg, e)
        
        await ctx.followup.send(embed=e, file=file if file is not None else discord.utils.MISSING, view=views.GetEgg(lines, creator, egg.origin))
    
    @app.command(name="delete", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def delete(self, ctx: discord.Interaction, id: int):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.get_line("eggs/delete", ctx)

        egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

        if not egg:
            await ctx.followup.send(content=lines["not_found"].format(id), ephemeral=True)
            return
        
        creatorchk = ctx.user.id == egg.creator.id
        modchk = ctx.guild and ctx.permissions.manage_guild and egg.origin.id == ctx.guild.id

        if not (creatorchk or modchk):
            await ctx.followup.send(content=lines["cannot"], ephemeral=True)
            return
        
        e = discord.Embed(title=lines["ready"]["title"].format(egg.id), color=discord.Color.blurple(), description=lines["ready"]["question"])
        e.add_field(name=lines["ready"]["content"], value=egg.text if egg.text is not None else lines["ready"]["no_content"], inline=False)
        await utils.brand_embed(e, self.bot, ctx)

        file = utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=file if file is not None else discord.utils.MISSING, view=views.DeleteEgg(lines, egg), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggs(bot))