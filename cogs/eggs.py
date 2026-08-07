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
    @app.rename(text="create_text", file="create_file", link="create_link", nsfw="create_nsfw")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", nsfw="create_nsfw_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def create(self, ctx: discord.Interaction, text: str | None, file: discord.Attachment | None, link: str | None, nsfw: bool | None = False):
        await ctx.response.defer()

        lines = await self.bot.get_lines(ctx)
        myloc = self.bot.get_line("eggs/create", lines)

        is_channel_nsfw = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False
        if nsfw and not is_channel_nsfw:
            await ctx.followup.send(myloc["no_nsfw"])
            return
        
        if file and link:
            await ctx.followup.send(myloc["toomanyattach"])
            return

        user, _ = await User.get_or_create(id=ctx.user.id)

        if user.banned:
            await ctx.followup.send(myloc["banned"])
            return

        if text is None and file is None and link is None:
            await ctx.followup.send(myloc["empty"])
            return

        if text:
            text = text.strip()
            if text == "": text = None

        trimtext = text[:4095] + ("…" if len(text) > 4095 else "") if text else None

        attach_path = None
        attach_hash = None

        if file:
            if file.content_type and file.content_type.startswith("image/"):
                attach_path, attach_hash = await utils.process_attachment(file)
            else:
                await ctx.followup.send(myloc["images_only"])
                return

        existing = await Egg.filter(text=trimtext, attach_hash=attach_hash, attach_link=link).first()

        if existing:
            if attach_path and os.path.exists(attach_path):
                os.remove(attach_path)

            await ctx.followup.send(myloc["duplicate"].format(existing.id))
            return

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        egg = await Egg.create(
            text=trimtext,
            attach_path=attach_path,
            attach_hash=attach_hash,
            attach_link=link,
            nsfw=nsfw,
            creator=user,
            origin=guild
        )

        e = discord.Embed(
            title=myloc["success"]["title"].format(egg.id) + (" 🌶️" if egg.nsfw else ""),
            color=discord.Color.blurple() if not egg.nsfw else discord.Color.red(),
            description=egg.text
        )
        utils.brand_embed(e, lines)

        file = await utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING)

    @app.command(name="get", description="get_description")
    @app.rename(id="get_id")
    @app.describe(id="get_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def get(self, ctx: discord.Interaction, id: int | None):
        await ctx.response.defer()

        lines = await self.bot.get_lines(ctx)
        myloc = self.bot.get_line("eggs/get", lines)

        is_channel_nsfw = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False

        if id is not None:
            egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id))
                return

            if egg.nsfw and not is_channel_nsfw:
                await ctx.followup.send(myloc["nsfw_id_in_sfw"])
                return
        else:
            eggs = Egg.all()

            if not is_channel_nsfw:
                eggs = eggs.filter(nsfw=False)

            count = await eggs.count()

            if count == 0:
                await ctx.followup.send(myloc["no_egg"])
                return

            randegg = random.randint(0, count - 1)
            egg = await eggs.offset(randegg).prefetch_related("creator", "origin").first()

        creator = self.bot.get_user(egg.creator.id)

        if creator is None:
            try:
                creator = await self.bot.fetch_user(egg.creator.id)
            except discord.NotFound:
                creator = None
        
        e, file = await utils.get_egg_embed(self.bot, lines, egg, creator)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING, view=views.GetEgg(self.bot, lines, egg, creator))
    
    @app.command(name="nsfw", description="nsfw_description", nsfw=True)
    async def nsfw(self, ctx: discord.Interaction):
        await ctx.response.defer()

        lines = await self.bot.get_lines(ctx)
        myloc = self.bot.get_line("eggs/get", lines)

        eggs = Egg.all().filter(nsfw=True)

        count = await eggs.count()

        if count == 0:
            await ctx.followup.send(myloc["no_egg"])
            return

        randegg = random.randint(0, count - 1)
        egg = await eggs.offset(randegg).prefetch_related("creator", "origin").first()

        creator = self.bot.get_user(egg.creator.id)

        if creator is None:
            try:
                creator = await self.bot.fetch_user(egg.creator.id)
            except discord.NotFound:
                creator = None
        
        e, file = await utils.get_egg_embed(self.bot, lines, egg, creator)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING, view=views.GetEgg(self.bot, lines, egg, creator))

    @app.command(name="delete", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def delete(self, ctx: discord.Interaction, id: int):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.get_lines(ctx)
        myloc = self.bot.get_line("eggs/delete", lines)

        egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

        if not egg:
            await ctx.followup.send(content=myloc["not_found"].format(id), ephemeral=True)
            return

        creatorchk = ctx.user.id == egg.creator.id
        modchk = ctx.guild and ctx.permissions.manage_guild and egg.origin.id == ctx.guild.id

        if not (creatorchk or modchk):
            await ctx.followup.send(content=myloc["cannot"], ephemeral=True)
            return

        text = egg.text[:1023] + ("…" if len(egg.text) > 1023 else "") if egg.text else None

        e = discord.Embed(title=myloc["ready"]["title"].format(egg.id), color=discord.Color.blurple(), description=myloc["ready"]["question"])
        e.add_field(name=myloc["ready"]["content"], value=text if text is not None else myloc["ready"]["no_content"], inline=False)
        utils.brand_embed(e, lines)

        file = await utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING, view=views.DeleteEgg(self.bot, lines, egg), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggs(bot))