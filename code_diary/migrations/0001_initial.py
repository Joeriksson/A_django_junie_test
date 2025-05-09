# Generated by Django 5.2 on 2025-04-17 12:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DiaryEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("title", models.CharField(max_length=200)),
                (
                    "content",
                    models.TextField(help_text="Describe what you coded today"),
                ),
                (
                    "technologies",
                    models.CharField(
                        help_text="Technologies used (comma separated)", max_length=200
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Diary Entries",
                "ordering": ["-date"],
            },
        ),
    ]
