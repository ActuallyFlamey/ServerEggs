from tortoise import fields
from tortoise.models import Model


class Egg(Model):
    id = fields.IntField(primary_key=True)

    text = fields.TextField(null=True)
    attach_path = fields.TextField(null=True)
    attach_hash = fields.CharField(64, null=True, index=True)
    attach_link = fields.TextField(null=True)

    nsfw = fields.BooleanField(default=False)

    reports = fields.ReverseRelation["Report"]

    creator = fields.ForeignKeyField("models.User", "eggs")
    origin = fields.ForeignKeyField("models.Guild", "eggs")

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)

class Guild(Model):
    id = fields.BigIntField(primary_key=True, generated=False)

    description = fields.TextField(null=True)
    invite = fields.TextField(null=True)

    lang = fields.CharField(5, default="en")
    allow_user_lang = fields.BooleanField(default=True)

    eggs = fields.ReverseRelation["Egg"]

class User(Model):
    id = fields.BigIntField(primary_key=True, generated=False)

    lang = fields.CharField(5, default="")
    banned = fields.BooleanField(default=False)

    eggs = fields.ReverseRelation["Egg"]
    reports = fields.ReverseRelation["Report"]

class Report(Model):
    id = fields.BigIntField(primary_key=True)

    egg = fields.ForeignKeyField("models.Egg", "reports")
    reporter = fields.ForeignKeyField("models.User", "reports")

    reason = fields.CharField(max_length=200, null=True)
    log_message_id = fields.BigIntField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("egg", "reporter"),)