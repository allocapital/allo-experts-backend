# Generated by Django 5.1.2 on 2024-11-01 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0003_build_metadata_build_status_build_type'),
        ('courses', '0001_initial'),
        ('experts', '0011_alter_expert_mechanisms'),
        ('mechanisms', '0009_mechanism_builds_mechanism_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='courses',
            field=models.ManyToManyField(blank=True, related_name='related_builds', to='courses.course'),
        ),
        migrations.AddField(
            model_name='build',
            name='experts',
            field=models.ManyToManyField(blank=True, related_name='related_builds', to='experts.expert'),
        ),
        migrations.AddField(
            model_name='build',
            name='mechanisms',
            field=models.ManyToManyField(blank=True, related_name='related_builds', to='mechanisms.mechanism'),
        ),
    ]
