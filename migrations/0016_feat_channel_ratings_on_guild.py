from tortoise import migrations
from tortoise.migrations import operations as ops
import functools
from json import dumps, loads
from schema import default_rated_channels
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0015_change_private_is_now_public_on_user')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Guild',
            name='channel_ratings',
            field=fields.JSONField(default=default_rated_channels, encoder=functools.partial(dumps, separators=(',', ':')), decoder=loads, null=True)
        ),
        ops.RunSQL(sql="""
            UPDATE "guild"
            SET "channel_ratings" = '{"safe":[],"questionable":[],"explicit":[]}'::jsonb
            WHERE "channel_ratings" IS NULL;
        """,
        reverse_sql="""
            UPDATE "guild"
            SET "channel_ratings" = NULL;
        """),
        ops.AlterField(
            model_name='Guild',
            name='channel_ratings',
            field=fields.JSONField(default=default_rated_channels, encoder=functools.partial(dumps, separators=(',', ':')), decoder=loads, null=False)
        )
    ]
