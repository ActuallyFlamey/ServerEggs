from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='Guild',
            fields=[
                ('id', fields.BigIntField(primary_key=True, unique=True, db_index=True)),
                ('description', fields.TextField(null=True, unique=False)),
                ('invite', fields.TextField(null=True, unique=False)),
                ('lang', fields.CharField(default='en', max_length=5)),
                ('allow_user_lang', fields.BooleanField(default=True)),
            ],
            options={'table': 'guild', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.BigIntField(primary_key=True, unique=True, db_index=True)),
                ('lang', fields.CharField(default='', max_length=5)),
                ('banned', fields.BooleanField(default=False)),
            ],
            options={'table': 'user', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Egg',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('text', fields.TextField(null=True, unique=False)),
                ('attach_path', fields.TextField(null=True, unique=False)),
                ('attach_hash', fields.CharField(null=True, db_index=True, max_length=64)),
                ('attach_link', fields.TextField(null=True, unique=False)),
                ('nsfw', fields.BooleanField(default=False)),
                ('creator', fields.ForeignKeyField('models.User', source_field='creator_id', db_constraint=True, to_field='id', related_name='eggs', on_delete=OnDelete.CASCADE)),
                ('origin', fields.ForeignKeyField('models.Guild', source_field='origin_id', db_constraint=True, to_field='id', related_name='eggs', on_delete=OnDelete.CASCADE)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('edited_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={'table': 'egg', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Report',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('egg', fields.ForeignKeyField('models.Egg', source_field='egg_id', db_constraint=True, to_field='id', related_name='reports', on_delete=OnDelete.CASCADE)),
                ('reporter', fields.ForeignKeyField('models.User', source_field='reporter_id', db_constraint=True, to_field='id', related_name='reports', on_delete=OnDelete.CASCADE)),
                ('reason', fields.CharField(null=True, max_length=200)),
                ('log_message_id', fields.BigIntField(null=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'report', 'app': 'models', 'unique_together': (('egg', 'reporter'),), 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
