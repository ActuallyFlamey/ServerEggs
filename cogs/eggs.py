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

    async def manage_check(self, ctx: discord.Interaction, egg):
        creatorchk = ctx.user.id == egg.creator.id

        modchk = ctx.guild and ctx.permissions.manage_guild and egg.origin.id == ctx.guild.id

        globalmodchk = await utils.is_global_mod(self.bot, ctx.user.id)

        return creatorchk or modchk or globalmodchk

    async def create_or_edit(
        self,
        ctx: discord.Interaction,
        id: int | None = None,
        text: str | None = None,
        file: discord.Attachment | None = None,
        link: str | None = None,
        nsfw: bool | None = None,
        secret: bool | None = None
    ):
        if not ctx.response.is_done():
            await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggs/create_edit")

        if text is None and file is None and link is None and nsfw is None and secret is None:
            await ctx.followup.send(myloc["empty_create"] if not id else myloc["empty_edit"])
            return

        if nsfw and not utils.channel_is_nsfw(ctx.channel):
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
            egg = await Egg.get_with_related(id)

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id), ephemeral=True)
                return

            if not await self.manage_check(ctx, egg):
                await ctx.followup.send(myloc["cannot"], ephemeral=True)
                return

        trimtext = None
        if text is not None:
            text = text.strip() or None
            trimtext = utils.truncate(text, 4000)

        attach_path = attach_hash = attach_link = scanfile = attach_bytes = None
        if file:
            content_type = utils.get_content_type(file)

            if not file.content_type or content_type not in {"image", "video", "audio"}:
                await ctx.followup.send(myloc["supported_only"])
                return

            scanfile = await file.to_file()
        elif link:
            attach_link = await utils.resolve_media_url(link)
            if attach_link is None:
                await ctx.followup.send(myloc["invalid_url"])
                return

            if not utils.is_native_embed(attach_link):
                scanfile = await utils.url_to_file(attach_link)
                if not scanfile:
                    await ctx.followup.send(myloc["could_not_scan"])
                    return

        processing = await ctx.followup.send(myloc["processing"])

        if scanfile:
            scan, too_long, attach_bytes = await utils.scan_csam(scanfile)

            if too_long:
                await processing.edit(content=myloc["too_long"])
                return

            if scan:
                await processing.edit(content=myloc["illegal"])

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
            utils.safe_remove(attach_path)

            await processing.edit(content=myloc["duplicate"].format(existing.id))
            return

        guild = None
        if ctx.guild:
            guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if not id:
            egg = await Egg.create(
                text=trimtext,
                attach_path=attach_path,
                attach_hash=attach_hash,
                attach_link=attach_link,
                nsfw=nsfw or False,
                secret=secret or False,
                creator=user,
                origin=guild
            )
        else:
            if (file or link):
                utils.safe_remove(egg.attach_path)

            if text is not None: egg.text = trimtext
            if file is not None or link is not None:
                egg.attach_path = attach_path
                egg.attach_hash = attach_hash
                egg.attach_link = attach_link
            if nsfw is not None: egg.nsfw = nsfw
            if secret is not None: egg.secret = secret

            await egg.save()

        creator = self.bot.get_user(egg.creator.id)
        if ctx.guild: await utils.log_egg(self.bot, lines, guild, egg, creator, ctx.user, bool(id))

        e = discord.Embed(
            title=utils.egg_title(egg, myloc["title"].format(egg.id, myloc["created"] if not id else myloc["edited"])),
            color=utils.get_egg_color(egg),
            description=egg.text
        )
        utils.brand_embed(e, lines)

        resfile, reslink, inline = utils.show_attachment(egg, e)
        _, vfile, vlink = utils.attachment_kwargs(resfile, reslink, inline)

        attachments = [resfile] if inline and resfile else []

        await processing.edit(
            content=None,
            embed=e,
            attachments=attachments,
            view=views.CreateEgg(self.bot, myloc, vfile, vlink)
        )

    @app.command(name="create", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", nsfw="create_nsfw", secret="create_secret")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", nsfw="create_nsfw_description", secret="create_secret_description")
    @app.allowed_installs(guilds=True, users=False)
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def create(
        self,
        ctx: discord.Interaction,
        text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        nsfw: bool | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, None, text, file, link, nsfw, secret)

    @app.command(name="lay", description="create_description")
    @app.rename(text="create_text", file="create_file", link="create_link", nsfw="create_nsfw")
    @app.describe(text="create_text_description", file="create_file_description", link="create_link_description", nsfw="create_nsfw_description")
    @app.allowed_installs(guilds=True, users=False)
    @app.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def lay(
        self,
        ctx: discord.Interaction,
        text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        nsfw: bool | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, None, text, file, link, nsfw, secret)

    async def _get(self, ctx: discord.Interaction, id: int | None, only_nsfw: bool = False):
        await ctx.response.defer()

        lines, myloc = await self.bot.get_section(ctx, "eggs/get")

        is_channel_nsfw = utils.channel_is_nsfw(ctx.channel)

        collected = False

        if id is not None:
            egg = await Egg.get_with_related(id)

            if not egg:
                await ctx.followup.send(myloc["not_found"].format(id))
                return

            if egg.nsfw and not is_channel_nsfw:
                await ctx.followup.send(myloc["nsfw_id_in_sfw"].format(id))
                return

            if egg.secret:
                await ctx.followup.send(myloc["secret"].format(id))
                return

            if ctx.guild and await egg.filtered_in.filter(id=ctx.guild.id).exists():
                await ctx.followup.send(myloc["filtered"].format(id, ctx.guild.name))
                return
        else:
            eggs = Egg.all()

            if ctx.guild:
                filtered = await Egg.filter(filtered_in__id=ctx.guild.id).values_list("id", flat=True)
                if filtered:
                    eggs = eggs.filter(id__not_in=filtered)

            if only_nsfw:
                eggs = eggs.filter(nsfw=True)
            elif not is_channel_nsfw:
                eggs = eggs.filter(nsfw=False)

            count = await eggs.count()

            if count == 0:
                await ctx.followup.send(myloc["no_egg"])
                return

            randegg = random.randint(0, count - 1)
            egg = await eggs.offset(randegg).prefetch_related("creator", "origin").first()

            user, _ = await User.get_or_create(id=ctx.user.id)
            if not await user.collected.filter(id=egg.id).exists():
                await user.collected.add(egg)
                collected = True

        collections = await egg.collectors.all().count()

        creator = await utils.get_or_fetch_user(self.bot, egg.creator.id)

        e, file, link, inline = await utils.get_egg_embed(self.bot, lines, egg, creator, collections, collected)
        sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

        await ctx.followup.send(
            embed=e,
            file=sfile,
            view=views.GetEgg(self.bot, lines, egg, creator, vfile, vlink)
        )

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
    async def nsfw(self, ctx: discord.Interaction):
        await self._get(ctx, None, True)

    @app.command(name="edit", description="edit_description")
    @app.rename(id="edit_id", text="edit_text", file="edit_file", link="edit_link", nsfw="edit_nsfw", secret="edit_secret")
    @app.describe(id="edit_id_description", text="edit_text_description", file="edit_file_description", link="edit_link_description", nsfw="edit_nsfw_description", secret="edit_secret_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def edit(
        self,
        ctx: discord.Interaction,
        id: int, text: str | None,
        file: discord.Attachment | None,
        link: str | None,
        nsfw: bool | None,
        secret: bool | None
    ):
        await self.create_or_edit(ctx, id, text, file, link, nsfw, secret)

    def _confirm_embed(self, lines: dict, myloc: dict, egg, color: discord.Color):
        text = utils.truncate(egg.text, 1023)

        e = discord.Embed(title=myloc["ready"]["title"].format(egg.id), color=color, description=myloc["ready"]["question"])
        e.add_field(name=myloc["ready"]["content"], value=text if text is not None else myloc["ready"]["no_content"], inline=False)
        utils.brand_embed(e, lines)

        file, link, inline = utils.show_attachment(egg, e)

        if link:
            e.add_field(name=myloc["ready"]["link"], value=link)

        return e, file, link, inline

    async def _confirm_flow(self, ctx: discord.Interaction, path: str, id: int, color: discord.Color, view_class, *, check_manage: bool = False):
        await ctx.response.defer(ephemeral=True)

        lines, myloc = await self.bot.get_section(ctx, path)

        egg = await Egg.get_with_related(id)

        if not egg:
            await ctx.followup.send(myloc["not_found"].format(id), ephemeral=True)
            return

        if check_manage and not await self.manage_check(ctx, egg):
            await ctx.followup.send(myloc["cannot"], ephemeral=True)
            return

        e, file, link, inline = self._confirm_embed(lines, myloc, egg, color)
        sfile, vfile, vlink = utils.attachment_kwargs(file, link, inline)

        await ctx.followup.send(
            embed=e,
            file=sfile,
            view=view_class(self.bot, lines, egg, vfile, vlink),
            ephemeral=True
        )

    @app.command(name="report", description="report_description")
    @app.rename(id="report_id")
    @app.describe(id="report_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def report(self, ctx: discord.Interaction, id: int):
        await self._confirm_flow(ctx, "eggs/report", id, discord.Color.red(), views.PreReportEgg)

    @app.command(name="delete", description="delete_description")
    @app.rename(id="delete_id")
    @app.describe(id="delete_id_description")
    @app.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def delete(self, ctx: discord.Interaction, id: int):
        await self._confirm_flow(ctx, "eggs/delete", id, discord.Color.blurple(), views.DeleteEgg, check_manage=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Eggs(bot))