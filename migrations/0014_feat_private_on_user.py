from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0013_feat_egg_set_null_on_user_guild_delete')]

    initial = False

    operations = [
        ops.AddField(
            model_name='User',
            name='private',
            field=fields.BooleanField(default=False, null=True),
        ),
        ops.RunSQL(sql="""
            UPDATE "user"
            SET private = false
            WHERE private IS NULL;
        """),
        ops.AlterField(
            model_name='User',
            name='private',
            field=fields.BooleanField(default=False, null=False)
        )
    ]
