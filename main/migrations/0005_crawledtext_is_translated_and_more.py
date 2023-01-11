# Generated by Django 4.1.5 on 2023-01-11 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_crawledtext_is_translated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawledtext',
            name='is_translated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='crawledtext',
            name='translated_text',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='crawledtext',
            name='translated_title',
            field=models.TextField(default=''),
        ),
    ]
