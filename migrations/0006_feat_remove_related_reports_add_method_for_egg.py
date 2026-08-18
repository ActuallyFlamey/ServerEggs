from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('eggs', '0005_feat_related_report_message')]

    initial = False

    operations = [
        ops.RemoveField(model_name='Report', name='related_message_id')
    ]
