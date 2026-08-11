import asyncio
import io
import os
import random

import aiohttp
import discord
from discord import app_commands as app
from discord.ext import commands

import utils
import views
from schema import Egg, Guild, User


class Eggs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_or_edit(
        self,
        ctx: discord.Interaction,
        id: int | None = None,
        text: str | None = None,
        file: discord.Attachment | None = None,
        link: str | None = None,
        nsfw: bool | None = None
    ):
        if not ctx.response.is_done():
            await ctx.response.defer()

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggs/create_edit", lines)

        if text is None and file is None and link is None and nsfw is None:
            if not id:
                await ctx.followup.send(myloc["empty_create"])
            else:
                await ctx.followup.send(myloc["empty_edit"])
            return

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

        egg = None
        if id:
            egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id), ephemeral=True)
                return

            creatorchk = ctx.user.id == egg.creator.id
            modchk = ctx.guild and ctx.permissions.manage_guild and egg.origin.id == ctx.guild.id

            if not (creatorchk or modchk):
                await ctx.followup.send(myloc["cannot"], ephemeral=True)
                return

        trimtext = None
        if text is not None:
            text = text.strip() or None
            trimtext = text[:4000] + ("…" if text and len(text) > 4000 else "") if text else None

        attach_path = attach_hash = attach_link = attach_file = attach_bytes = None
        if file:
            if not file.content_type or not file.content_type.startswith("image/"):
                await ctx.followup.send(myloc["images_only"])
                return
            
            attach_file = await file.to_file()
        elif link:
            attach_link = await utils.resolve_media_url(link)
            if attach_link is None:
                await ctx.followup.send(myloc["invalid_url"])
                return

            try:
                async with aiohttp.ClientSession() as session, session.get(attach_link, timeout=10) as res:
                    if res.status == 200:
                        filebytes = await res.read()
                        with io.BytesIO(filebytes) as stream:
                            attach_file = discord.File(stream)
                    else:
                        await ctx.followup.send(myloc["could_not_scan"])
                        return
            except (aiohttp.ClientError, asyncio.TimeoutError):
                await ctx.followup.send(myloc["could_not_scan"])
                return

        if attach_file:
            scan, attach_bytes = await utils.scan_csam(attach_file)
            if scan:
                await ctx.followup.send(myloc["illegal"])

                user.banned = True
                await user.save()

                return
        
        if file:
            attach_path, attach_hash = await utils.process_attachment(file, attach_bytes)

        check_text = trimtext if text is not None else (egg.text if id else None)
        check_hash = attach_hash if file else (None if link else (egg.attach_hash if id else None))
        check_link = attach_link if link else (None if file else (egg.attach_link if id else None))

        existing = await Egg.filter(text=check_text, attach_hash=check_hash, attach_link=check_link).first()

        if existing and (not id or existing.id != id):
            if attach_path and os.path.exists(attach_path):
                os.remove(attach_path)

            await ctx.followup.send(myloc["duplicate"].format(existing.id))
            return

        if not id:
            guild, _ = await Guild.get_or_create(id=ctx.guild.id)

            egg = await Egg.create(
                text=trimtext,
                attach_path=attach_path,
                attach_hash=attach_hash,
                attach_link=attach_link,
                nsfw=nsfw or False,
                creator=user,
                origin=guild
            )
        else:
            if (file or link) and egg.attach_path and os.path.exists(egg.attach_path):
                os.remove(egg.attach_path)

            if text is not None: egg.text = trimtext
            if file is not None or link is not None:
                egg.attach_path = attach_path
                egg.attach_hash = attach_hash
                egg.attach_link = attach_link
            if nsfw is not None: egg.nsfw = nsfw

            await egg.save()

        e = discord.Embed(
            title=myloc["success"]["title"]
                .format(
                    egg.id,
                    format(myloc["success"]["created"] if not id else myloc["success"]["edited"])
                )
                + (" 🌶️" if egg.nsfw else ""),
            color=discord.Color.red() if egg.nsfw else discord.Color.blurple(),
            description=egg.text
        )
        utils.brand_embed(e, lines)

        out_file = utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=out_file or discord.utils.MISSING)

    @app.command(name="create", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", nsfw="create_nsfw")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", nsfw="create_nsfw_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def create(self, ctx: discord.Interaction, text: str | None, file: discord.Attachment | None, link: str | None, nsfw: bool | None):
        await self.create_or_edit(ctx, None, text, file, link, nsfw)

    @app.command(name="lay", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", nsfw="create_nsfw")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", nsfw="create_nsfw_description")
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def lay(self, ctx: discord.Interaction, text: str | None, file: discord.Attachment | None, link: str | None, nsfw: bool | None):
        await self.create_or_edit(ctx, None, text, file, link, nsfw)

    async def _get(self, ctx: discord.Interaction, id: int | None, only_nsfw: bool = False):
        await ctx.response.defer()

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggs/get", lines)

        is_channel_nsfw = ctx.channel.is_nsfw() if ctx.channel and hasattr(ctx.channel, "is_nsfw") else False

        if id is not None:
            egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id))
                return

            if egg.nsfw and not is_channel_nsfw:
                await ctx.followup.send(myloc["nsfw_id_in_sfw"])
                return

            if egg.secret:
                await ctx.followup.send(myloc["secret"])
                return
        else:
            eggs = Egg.all()

            if not is_channel_nsfw:
                eggs = eggs.filter(nsfw=False)
            elif only_nsfw:
                eggs = eggs.filter(nsfw=True)

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

    @app.command(name="get", description="get_description")
    @app.rename(id="get_id")
    @app.describe(id="get_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def get(self, ctx: discord.Interaction, id: int | None):
        await self._get(ctx, id)

    @app.command(name="egg", description="get_description")
    @app.rename(id="get_id")
    @app.describe(id="get_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def egg(self, ctx: discord.Interaction, id: int | None):
        await self._get(ctx, id)

    @app.command(name="nsfw", description="nsfw_description", nsfw=True)
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def nsfw(self, ctx: discord.Interaction):
        await self._get(ctx, None, True)

    @app.command(name="edit", description="edit_description")
    @app.rename(id="edit_id", text="edit_text", file="edit_file", link="edit_link", nsfw="edit_nsfw")
    @app.describe(id="edit_id_description", text="edit_text_description", file="edit_file_description", link="edit_link_description", nsfw="edit_nsfw_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def edit(self, ctx: discord.Interaction, id: int, text: str | None, file: discord.Attachment | None, link: str | None, nsfw: bool | None):
        await self.create_or_edit(ctx, id, text, file, link, nsfw)

    @app.command(name="report", description="report_description")
    @app.rename(id="report_id")
    @app.describe(id="report_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def report(self, ctx: discord.Interaction, id: int):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggs/report", lines)

        egg = await Egg.get_or_none(id=id).prefetch_related("creator", "origin")

        if not egg:
            await ctx.followup.send(myloc["not_found"].format(id))
            return

        text = egg.text[:1023] + ("…" if len(egg.text) > 1023 else "") if egg.text else None

        e = discord.Embed(title=myloc["ready"]["title"].format(egg.id), color=discord.Color.red(), description=myloc["ready"]["question"])
        e.add_field(name=myloc["ready"]["content"], value=text if text is not None else myloc["ready"]["no_content"], inline=False)
        utils.brand_embed(e, lines)

        file = utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING, view=views.PreReportEgg(self.bot, lines, egg), ephemeral=True)

    @app.command(name="delete", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def delete(self, ctx: discord.Interaction, id: int):
        await ctx.response.defer(ephemeral=True)

        lines = await self.bot.fetch_lines(ctx)
        myloc = self.bot.get_lines("eggs/delete", lines)

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

        file = utils.show_attachment(egg, e)

        await ctx.followup.send(embed=e, file=file or discord.utils.MISSING, view=views.DeleteEgg(self.bot, lines, egg), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggs(bot))