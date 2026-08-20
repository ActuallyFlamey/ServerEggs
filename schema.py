from enum import StrEnum

from tortoise import fields, models


class Rating(StrEnum):
    SAFE = "SAFE"
    QUESTIONABLE = "QUESTIONABLE"
    EXPLICIT = "EXPLICIT"

def default_ratings() -> dict:
    return {
        "normal": [Rating.SAFE, Rating.QUESTIONABLE],
        "nsfw": [Rating.SAFE, Rating.QUESTIONABLE, Rating.EXPLICIT]
    }

class Egg(models.Model):
    id = fields.IntField(primary_key=True)

    text = fields.TextField(null=True)
    attach_path = fields.TextField(null=True)
    attach_hash = fields.CharField(64, null=True, index=True)
    attach_link = fields.TextField(null=True)

    rating = fields.CharEnumField(enum_type=Rating, default=Rating.SAFE)

    secret = fields.BooleanField(default=False)

    reports = fields.ReverseRelation["Report"]

    creator = fields.ForeignKeyField("eggs.User", "eggs")
    origin = fields.ForeignKeyField("eggs.Guild", "eggs")

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def get_with_related(cls, id):
        return await cls.get_or_none(id=id).prefetch_related("creator", "origin")

class Guild(models.Model):
    id = fields.BigIntField(primary_key=True, generated=False, unique=True, db_index=True)

    description = fields.TextField(null=True)
    invite = fields.TextField(null=True)

    lang = fields.CharField(5, default="en")
    allow_user_lang = fields.BooleanField(default=True)

    ratings = fields.JSONField(default=default_ratings)

    logch = fields.BigIntField(null=True)

    filtered: fields.ManyToManyField["Egg"] = fields.ManyToManyField("eggs.Egg", related_name="filtered_in", through="guild_filtered_eggs")

    eggs = fields.ReverseRelation["Egg"]

class User(models.Model):
    id = fields.BigIntField(primary_key=True, generated=False, unique=True, db_index=True)

    lang = fields.CharField(5, default="")
    banned = fields.BooleanField(default=False)

    collected: fields.ManyToManyRelation["Egg"] = fields.ManyToManyField("eggs.Egg", related_name="collectors", through="user_collected_eggs")

    eggs = fields.ReverseRelation["Egg"]
    reports = fields.ReverseRelation["Report"]

class Report(models.Model):
    id = fields.BigIntField(primary_key=True)

    egg = fields.ForeignKeyField("eggs.Egg", "reports")
    reporter = fields.ForeignKeyField("eggs.User", "reports")

    reason = fields.CharField(max_length=200, null=True)
    log_message_id = fields.BigIntField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("egg", "reporter"),)