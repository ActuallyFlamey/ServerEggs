import functools
from json import dumps, loads
from schema import Rating, default_ratings
from tortoise import fields, migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("eggs", "0007_search_trgm")]

    initial = False

    operations = [
        ops.AddField(
            model_name="Egg",
            name="rating",
            field=fields.CharEnumField(
                enum_type=Rating,
                max_length=12,
                null=True,
                description="SAFE: SAFE\nQUESTIONABLE: QUESTIONABLE\nEXPLICIT: EXPLICIT",
            ),
        ),
        ops.RunSQL(
            sql="""
                UPDATE "egg"
                SET "rating" = CASE
                    WHEN "nsfw" = TRUE THEN 'EXPLICIT'
                    ELSE 'SAFE'
                END;
            """,
            reverse_sql="""
                UPDATE "egg"
                SET "nsfw" = CASE
                    WHEN "rating" = 'EXPLICIT' THEN TRUE
                    ELSE FALSE
                END;
            """,
        ),
        ops.AlterField(
            model_name="Egg",
            name="rating",
            field=fields.CharEnumField(
                enum_type=Rating,
                max_length=12,
                default=Rating.SAFE,
                null=False,
                description="SAFE: SAFE\nQUESTIONABLE: QUESTIONABLE\nEXPLICIT: EXPLICIT",
            ),
        ),
        ops.RemoveField(model_name="Egg", name="nsfw"),
        ops.AddField(
            model_name="Guild",
            name="ratings",
            field=fields.JSONField(
                null=True,
                encoder=functools.partial(dumps, separators=(",", ":")),
                decoder=loads,
            ),
        ),
        ops.RunSQL(
            sql="""
                UPDATE "guild"
                SET "ratings" = '{"normal":["SAFE","QUESTIONABLE"],"nsfw":["SAFE","QUESTIONABLE","EXPLICIT"]}'::jsonb
                WHERE "ratings" IS NULL;
            """,
            reverse_sql="""
                UPDATE "guild"
                SET "ratings" = NULL;
            """,
        ),
        ops.AlterField(
            model_name="Guild",
            name="ratings",
            field=fields.JSONField(
                default=default_ratings,
                null=False,
                encoder=functools.partial(dumps, separators=(",", ":")),
                decoder=loads,
            ),
        ),
    ]