import discord

from schema import Rating, default_ratings


def channel_is_nsfw(channel) -> bool:
    return bool(channel and hasattr(channel, "is_nsfw") and channel.is_nsfw())

def coerce_rating(value):
    if value is None or isinstance(value, Rating):
        return value

    return Rating(value)

def channel_ratings(guild, channel) -> list[Rating]:
    default = default_ratings()

    key = "nsfw" if channel_is_nsfw(channel) else "normal"

    if guild is None:
        return default[key]

    stored = getattr(guild, "ratings", None) or {}

    return stored.get(key, default[key])

async def get_or_fetch_user(bot, user_id: int):
    user = bot.get_user(user_id)

    if user is not None:
        return user

    try:
        return await bot.fetch_user(user_id)
    except (discord.NotFound, discord.HTTPException):
        return None