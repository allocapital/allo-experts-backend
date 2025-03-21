# Generated by Django 5.1.2 on 2024-11-01 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0002_expert_content_type_expert_object_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expert',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='expert',
            name='object_id',
        ),
        migrations.AddField(
            model_name='relatedobject',
            name='expert',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='experts.expert'),
            preserve_default=False,
        ),
    ]
