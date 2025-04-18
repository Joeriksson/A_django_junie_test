# Generated by Django 5.2 on 2025-04-17 15:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("code_diary", "0003_alter_diaryentry_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReadEntry",
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
                ("read_at", models.DateTimeField(auto_now_add=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="code_diary.diaryentry",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Read Entries",
                "unique_together": {("user", "entry")},
            },
        ),
        migrations.AddField(
            model_name="diaryentry",
            name="readers",
            field=models.ManyToManyField(
                related_name="read_entries",
                through="code_diary.ReadEntry",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
