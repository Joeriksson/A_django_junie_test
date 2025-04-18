from django.utils import timezone
from django.db.models import Q
from .models import DiaryEntry, ReadEntry

def notifications(request):
    """Context processor to add notification data to all templates."""
    context = {
        'new_entries_from_following': False
    }

    # Check for unread entries from followed users if logged in
    if request.user.is_authenticated:
        following = request.user.profile.following.all()
        if following.exists():
            # Get entries from followed users created in the last day
            recent_entries = DiaryEntry.objects.filter(
                user__in=following,
                created_at__gt=timezone.now() - timezone.timedelta(days=1)
            )

            # Filter out entries that the user has already read
            read_entry_ids = ReadEntry.objects.filter(
                user=request.user,
                entry__in=recent_entries
            ).values_list('entry_id', flat=True)

            unread_entries = recent_entries.exclude(id__in=read_entry_ids)

            context['new_entries_from_following'] = unread_entries.exists()

    return context
