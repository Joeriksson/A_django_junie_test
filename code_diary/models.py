from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class DiaryEntry(models.Model):
    """Model for storing daily code diary entries."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
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

    def get_absolute_url(self):
        return reverse('code_diary:entry_detail', kwargs={'pk': self.pk})


class UserProfile(models.Model):
    """Model for storing user profile information and following relationships."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def follow(self, user):
        """Follow a user if not already following."""
        if user != self.user and not self.following.filter(id=user.id).exists():
            self.following.add(user)
            return True
        return False

    def unfollow(self, user):
        """Unfollow a user if currently following."""
        if self.following.filter(id=user.id).exists():
            self.following.remove(user)
            return True
        return False

    def is_following(self, user):
        """Check if following a specific user."""
        return self.following.filter(id=user.id).exists()

    def get_following(self):
        """Get all users that this user is following."""
        return self.following.all()

    def get_followers(self):
        """Get all users that follow this user."""
        return User.objects.filter(profile__following=self.user)


# Signal to create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for a new User."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist (for existing users)
        UserProfile.objects.create(user=instance)
