from tortoise import fields
from tortoise.models import Model


class Egg(Model):
    id = fields.IntField(primary_key=True)

    text = fields.TextField(null=True)
    attach_path = fields.TextField(null=True)

    nsfw = fields.BooleanField(default=False)

    creator = fields.ForeignKeyField("models.User", "eggs")
    origin = fields.ForeignKeyField("models.Guild", "eggs")

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)

class Guild(Model):
    id = fields.BigIntField(primary_key=True, generated=False)

    lang = fields.CharField(5, default="en")
    allow_user_lang = fields.BooleanField(default=True)

    eggs = fields.ReverseRelation["Egg"]

class User(Model):
    id = fields.BigIntField(primary_key=True, generated=False)

    lang = fields.CharField(5, default="en")
    banned = fields.BooleanField(default=False)

    eggs = fields.ReverseRelation["Egg"]