from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DiaryEntry
from django.utils import timezone

# Create your views here.
class DiaryEntryListView(ListView):
    model = DiaryEntry
    template_name = 'code_diary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class DiaryEntryDetailView(DetailView):
    model = DiaryEntry
    template_name = 'code_diary/entry_detail.html'
    context_object_name = 'entry'

class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    model = DiaryEntry
    template_name = 'code_diary/entry_form.html'
    fields = ['date', 'title', 'content', 'technologies']
    success_url = reverse_lazy('code_diary:entry_list')
    login_url = '/admin/login/'

    def form_valid(self, form):
        messages.success(self.request, "Diary entry created successfully!")
        return super().form_valid(form)

class DiaryEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = DiaryEntry
    template_name = 'code_diary/entry_form.html'
    fields = ['date', 'title', 'content', 'technologies']
    login_url = '/admin/login/'

    def get_success_url(self):
        return reverse_lazy('code_diary:entry_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Diary entry updated successfully!")
        return super().form_valid(form)

class DiaryEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = DiaryEntry
    template_name = 'code_diary/entry_confirm_delete.html'
    success_url = reverse_lazy('code_diary:entry_list')
    login_url = '/admin/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Diary entry deleted successfully!")
        return super().delete(request, *args, **kwargs)

def home(request):
    """Home page view that redirects to the diary entry list."""
    return redirect('code_diary:entry_list')
