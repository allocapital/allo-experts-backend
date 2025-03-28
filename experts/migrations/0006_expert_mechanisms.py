# Generated by Django 5.1.2 on 2024-11-01 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0005_relatedobject_expert_relatedobject_mechanism'),
        ('mechanisms', '0007_remove_mechanism_related_build_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='mechanisms',
            field=models.ManyToManyField(blank=True, related_name='experts', to='mechanisms.mechanism'),
        ),
    ]
