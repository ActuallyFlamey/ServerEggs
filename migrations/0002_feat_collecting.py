from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0001_initial')]

    initial = False

    operations = [
        ops.AddIndex(
            model_name='Guild',
            index=Index(fields=['id']),
        ),
        ops.AddField(
            model_name='User',
            name='collected',
            field=fields.ManyToManyField('eggs.Egg', unique=True, db_constraint=True, through='user_collected_eggs', forward_key='egg_id', backward_key='user_id', related_name='collectors', on_delete=OnDelete.CASCADE),
        ),
        ops.AddIndex(
            model_name='User',
            index=Index(fields=['id']),
        ),
    ]
