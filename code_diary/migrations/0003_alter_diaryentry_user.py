# Generated by Django 5.2 on 2025-04-17 14:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("code_diary", "0002_diaryentry_user_userprofile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="diaryentry",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="diary_entries",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
