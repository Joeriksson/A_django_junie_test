from django.db import models
from django.utils import timezone

# Create your models here.
class DiaryEntry(models.Model):
    """Model for storing daily code diary entries."""
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Describe what you coded today")
    technologies = models.CharField(max_length=200, help_text="Technologies used (comma separated)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Diary Entries"

    def __str__(self):
        return f"{self.date}: {self.title}"
