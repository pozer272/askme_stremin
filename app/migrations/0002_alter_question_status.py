# Generated by Django 5.0.4 on 2024-04-06 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('n', 'New'), ('h', 'Hot')], max_length=10),
        ),
    ]