from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from .models import DiaryEntry, UserProfile
from .forms import SignUpForm, LoginForm, DiaryEntryForm
from django.utils import timezone
from django.contrib.auth import logout

# Create your views here.
# Authentication Views
class CustomLoginView(LoginView):
    """Custom login view using our form."""
    form_class = LoginForm
    template_name = 'code_diary/auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('code_diary:my_entries')

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

class SignUpView(CreateView):
    """View for user registration."""
    form_class = SignUpForm
    template_name = 'code_diary/auth/signup.html'
    success_url = reverse_lazy('code_diary:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! You can now log in.")
        return response

class CustomLogoutView(LogoutView):
    """Custom logout view using our template."""
    template_name = 'code_diary/auth/logout.html'
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        # Ensure the user is properly logged out
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

# Diary Entry Views
class HomeView(ListView):
    """Home page showing the latest entries from all users."""
    model = DiaryEntry
    template_name = 'code_diary/home.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        """Return the latest entries from all users."""
        return DiaryEntry.objects.all().order_by('-date', '-created_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        # Check for new entries from followed users if logged in
        if self.request.user.is_authenticated:
            following = self.request.user.profile.following.all()
            new_entries = DiaryEntry.objects.filter(
                user__in=following,
                created_at__gt=timezone.now() - timezone.timedelta(days=1)
            ).exists()
            context['new_entries_from_following'] = new_entries

        return context

class MyDiaryEntryListView(LoginRequiredMixin, ListView):
    """View for listing the current user's diary entries."""
    model = DiaryEntry
    template_name = 'code_diary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10
    login_url = reverse_lazy('code_diary:login')

    def get_queryset(self):
        """Return only the current user's entries."""
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['is_my_entries'] = True
        return context

class UserDiaryEntryListView(ListView):
    """View for listing a specific user's diary entries (read-only for other users)."""
    model = DiaryEntry
    template_name = 'code_diary/user_entries.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        """Return only the specified user's entries."""
        self.diary_user = get_object_or_404(User, username=self.kwargs['username'])
        return DiaryEntry.objects.filter(user=self.diary_user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diary_user'] = self.diary_user

        # Check if the current user is following this user
        if self.request.user.is_authenticated:
            context['is_following'] = self.request.user.profile.is_following(self.diary_user)

        return context

class DiaryEntryDetailView(DetailView):
    """View for displaying a single diary entry."""
    model = DiaryEntry
    template_name = 'code_diary/entry_detail.html'
    context_object_name = 'entry'

class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new diary entry."""
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'code_diary/entry_form.html'
    login_url = reverse_lazy('code_diary:login')

    def get_success_url(self):
        return reverse_lazy('code_diary:my_entries')

    def form_valid(self, form):
        """Set the user to the current user before saving."""
        form.instance.user = self.request.user
        messages.success(self.request, "Diary entry created successfully!")
        return super().form_valid(form)

class DiaryEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing diary entry."""
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'code_diary/entry_form.html'
    login_url = reverse_lazy('code_diary:login')

    def test_func(self):
        """Check that the user is the owner of the entry."""
        entry = self.get_object()
        return entry.user == self.request.user

    def get_success_url(self):
        return reverse_lazy('code_diary:entry_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Diary entry updated successfully!")
        return super().form_valid(form)

class DiaryEntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a diary entry."""
    model = DiaryEntry
    template_name = 'code_diary/entry_confirm_delete.html'
    login_url = reverse_lazy('code_diary:login')

    def test_func(self):
        """Check that the user is the owner of the entry."""
        entry = self.get_object()
        return entry.user == self.request.user

    def get_success_url(self):
        return reverse_lazy('code_diary:my_entries')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Diary entry deleted successfully!")
        return super().delete(request, *args, **kwargs)


# User Profile and Following Views
class UserListView(ListView):
    """View for listing all users."""
    model = User
    template_name = 'code_diary/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        """Return all active users except the current user."""
        return User.objects.filter(is_active=True).exclude(id=self.request.user.id if self.request.user.is_authenticated else 0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            following_ids = self.request.user.profile.following.values_list('id', flat=True)
            context['following_ids'] = following_ids
        return context

class FollowingListView(LoginRequiredMixin, ListView):
    """View for listing users that the current user is following."""
    model = User
    template_name = 'code_diary/following_list.html'
    context_object_name = 'following'
    paginate_by = 20
    login_url = reverse_lazy('code_diary:login')

    def get_queryset(self):
        """Return users that the current user is following."""
        return self.request.user.profile.following.all()

class FollowersListView(LoginRequiredMixin, ListView):
    """View for listing users that follow the current user."""
    model = User
    template_name = 'code_diary/followers_list.html'
    context_object_name = 'followers'
    paginate_by = 20
    login_url = reverse_lazy('code_diary:login')

    def get_queryset(self):
        """Return users that follow the current user."""
        return self.request.user.profile.get_followers()

@login_required
def follow_user(request, username):
    """View for following a user."""
    user_to_follow = get_object_or_404(User, username=username)

    # Try to follow the user
    if request.user.profile.follow(user_to_follow):
        messages.success(request, f"You are now following {username}")
    else:
        messages.info(request, f"You are already following {username}")

    # Redirect back to the user's profile
    return redirect('code_diary:user_entries', username=username)

@login_required
def unfollow_user(request, username):
    """View for unfollowing a user."""
    user_to_unfollow = get_object_or_404(User, username=username)

    # Try to unfollow the user
    if request.user.profile.unfollow(user_to_unfollow):
        messages.success(request, f"You have unfollowed {username}")
    else:
        messages.info(request, f"You were not following {username}")

    # Redirect back to the user's profile
    return redirect('code_diary:user_entries', username=username)

@login_required
def check_new_entries(request):
    """AJAX view to check for new entries from followed users."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        following = request.user.profile.following.all()
        new_entries = DiaryEntry.objects.filter(
            user__in=following,
            created_at__gt=timezone.now() - timezone.timedelta(days=1)
        ).exists()

        return JsonResponse({'new_entries': new_entries})

    return JsonResponse({'error': 'Invalid request'}, status=400)
