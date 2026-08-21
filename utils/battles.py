import datetime
import random

import discord
from discord.ext import commands

from schema import Battle, BattleStatus, BattleVote, Egg, Guild, Rating, User

from . import attach, embed, misc


async def random_egg(guild: Guild | None, channel, *, secret: bool | None = None, explicit_only: bool = False, exclude_ids=None):
    query = Egg.all()

    if guild:
        filtered = await Egg.filter(filtered_in__id=guild.id).values_list("id", flat=True)
        if filtered:
            query = query.filter(id__not_in=filtered)

    allowed = misc.channel_ratings(guild, channel)

    if explicit_only:
        query = query.filter(rating=Rating.EXPLICIT)
    else:
        query = query.filter(rating__in=allowed)

    if secret is not None:
        query = query.filter(secret=secret)

    if exclude_ids:
        query = query.exclude(id__in=list(exclude_ids))

    count = await query.count()

    if count == 0:
        return None

    return await query.offset(random.randint(0, count - 1)).prefetch_related("creator", "origin").first()

async def fight_pool_ids(user: User) -> list[int]:
    created = await Egg.filter(creator=user).values_list("id", flat=True)
    collected = await Egg.filter(collectors=user).values_list("id", flat=True)

    return list(dict.fromkeys(created + collected))

async def random_fight_egg(user: User, guild: Guild | None = None, channel=None, *, exclude_ids=None):
    ids = await fight_pool_ids(user)

    if exclude_ids:
        ids = [egg_id for egg_id in ids if egg_id not in exclude_ids]

    if not ids:
        return None

    query = Egg.filter(id__in=ids).filter(rating__in=misc.channel_ratings(guild, channel))

    if guild:
        filtered = await Egg.filter(filtered_in__id=guild.id).values_list("id", flat=True)
        if filtered:
            query = query.exclude(id__in=filtered)

    count = await query.count()

    if count == 0:
        return None

    return await query.offset(random.randint(0, count - 1)).first()

async def battle_side_embed(bot: commands.Bot, lines: dict, myloc: dict, egg, side: str) -> dict:
    creator = await misc.get_or_fetch_user(bot, egg.creator_id)

    e = discord.Embed(
        title=embed.egg_title(egg, myloc["eggn"].format(egg.id, side)),
        color=embed.get_egg_color(egg),
        description=egg.text
    )
    e.add_field(
        name=myloc["creator"],
        value=discord.utils.escape_markdown(f"**{creator.display_name}** ({creator.name})") if creator is not None else myloc["unknown_creator"].format(egg.creator_id)
    )
    embed.brand_embed(e, lines)

    file, link, inline = attach.show_attachment(egg, e)

    return {
        "embed": e,
        "file": file if inline else None,
        "vfile": attach.file_path(file) if not inline else None,
        "vlink": link if not inline else None
    }

async def build_battle_message(bot: commands.Bot, lines: dict, myloc: dict, egg_a, egg_b) -> list[dict]:
    return [await battle_side_embed(bot, lines, myloc, egg_a, "A"), await battle_side_embed(bot, lines, myloc, egg_b, "B")]

async def count_votes(battle) -> tuple[int, int]:
    rows = await BattleVote.filter(battle=battle).values("choice")

    count_a = sum(1 for row in rows if row["choice"] == 0)
    count_b = len(rows) - count_a

    return count_a, count_b

def result_embed(lines: dict, myloc: dict, winner, count_a: int, count_b: int) -> discord.Embed:
    if winner is not None:
        e = discord.Embed(
            title=myloc["result_win_title"].format(winner.id),
            color=discord.Color.gold(),
            description=myloc["result_win"].format(winner.id, max(count_a, count_b), min(count_a, count_b))
        )
    else:
        e = discord.Embed(
            title=myloc["result_tie_title"],
            color=discord.Color.blurple(),
            description=myloc["result_tie"].format(count_a, count_b)
        )

    embed.brand_embed(e, lines)

    return e

async def finalize_battle(bot: commands.Bot, battle):
    guild = await battle.guild
    locale = bot.locales.get(guild.lang if guild else "", bot.locales["en"])
    lines = locale["lines"]
    myloc = bot.get_lines("battles/battle", lines)

    count_a, count_b = await count_votes(battle)

    winner = None
    if count_a > count_b: winner_id = battle.egg_a_id
    elif count_b > count_a: winner_id = battle.egg_b_id
    else: winner_id = None

    if winner_id is not None:
        winner = await Egg.get_or_none(id=winner_id)

    winner_user_id = None
    if winner_id == battle.egg_a_id: winner_user_id = battle.user_a_id
    elif winner_id == battle.egg_b_id: winner_user_id = battle.user_b_id

    battle.winner_id = winner_id
    battle.winner_user_id = winner_user_id
    battle.status = BattleStatus.FINISHED
    await battle.save(update_fields=["winner_id", "winner_user_id", "status"])

    if battle.channel_id is None or battle.message_id is None:
        return

    channel = bot.get_channel(battle.channel_id)
    if channel is None:
        return

    try: message = await channel.fetch_message(battle.message_id)
    except discord.HTTPException: return

    try: await message.edit(content=None, embed=result_embed(lines, myloc, winner, count_a, count_b), attachments=[], view=None)
    except discord.HTTPException: pass

    try: await message.reply(content=myloc["finished"])
    except discord.HTTPException: pass

async def finalize_due_battles(bot: commands.Bot):
    due = await Battle.filter(status=BattleStatus.OPEN, ends_at__lte=datetime.datetime.now(datetime.timezone.utc))

    for battle in due:
        await finalize_battle(bot, battle)