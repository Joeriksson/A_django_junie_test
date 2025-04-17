from django.utils import timezone
from .models import DiaryEntry

def notifications(request):
    """Context processor to add notification data to all templates."""
    context = {
        'new_entries_from_following': False
    }
    
    # Check for new entries from followed users if logged in
    if request.user.is_authenticated:
        following = request.user.profile.following.all()
        if following.exists():
            new_entries = DiaryEntry.objects.filter(
                user__in=following,
                created_at__gt=timezone.now() - timezone.timedelta(days=1)
            ).exists()
            context['new_entries_from_following'] = new_entries
    
    return context