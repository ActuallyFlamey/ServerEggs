from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0003_feat_log_channel_on_guild')]

    initial = False

    operations = [
        ops.AddField(
            model_name='Guild',
            name='filtered',
            field=fields.ManyToManyField('eggs.Egg', unique=True, db_constraint=True, through='guild_filtered_eggs', forward_key='egg_id', backward_key='guild_id', related_name='filtered_in', on_delete=OnDelete.CASCADE),
        )
    ]
