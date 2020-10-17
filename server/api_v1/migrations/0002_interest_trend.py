# Generated by Django 3.1.2 on 2020-10-14 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('site', models.CharField(max_length=254)),
            ],
            options={
                'db_table': 'trend',
            },
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pull_datetime', models.DateTimeField()),
                ('pull_value', models.FloatField()),
                ('pull_type', models.CharField(max_length=100)),
                ('trend', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api_v1.trend')),
            ],
            options={
                'db_table': 'interest',
            },
        ),
    ]