#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from code_diary.models import DiaryEntry

# Check if a superuser exists
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser...")
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )
    print("Superuser created.")
else:
    print("Superuser already exists.")

# Get the first superuser
superuser = User.objects.filter(is_superuser=True).first()

# Update existing diary entries to associate them with the superuser
entries_updated = DiaryEntry.objects.filter(user__isnull=True).update(user=superuser)
print(f"Updated {entries_updated} diary entries.")

print("Done!")