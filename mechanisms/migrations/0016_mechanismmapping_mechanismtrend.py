# Generated by Django 5.1.2 on 2025-03-14 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mechanisms', '0015_mechanism_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='MechanismMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funder', models.CharField(help_text="Name of the funding organization (e.g., 'gitcoin', 'optimism')", max_length=255)),
                ('grant_pool_name', models.CharField(blank=True, help_text='Name of the grant pool or program', max_length=255, null=True)),
                ('priority', models.IntegerField(default=0, help_text='Higher priority mappings are applied first')),
                ('mechanism', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mappings', to='mechanisms.mechanism')),
            ],
            options={
                'verbose_name_plural': 'Mechanism Mappings',
                'ordering': ('-priority',),
                'unique_together': {('funder', 'grant_pool_name')},
            },
        ),
        migrations.CreateModel(
            name='MechanismTrend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(help_text='First day of the month for this data point')),
                ('value', models.DecimalField(decimal_places=2, help_text='Funding amount in USD', max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mechanism', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trends', to='mechanisms.mechanism')),
            ],
            options={
                'verbose_name_plural': 'Mechanism Trends',
                'ordering': ('month',),
                'unique_together': {('mechanism', 'month')},
            },
        ),
    ]
