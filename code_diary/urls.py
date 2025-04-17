from django.urls import path
from . import views

app_name = 'code_diary'

urlpatterns = [
    path('', views.DiaryEntryListView.as_view(), name='entry_list'),
    path('entry/<int:pk>/', views.DiaryEntryDetailView.as_view(), name='entry_detail'),
    path('entry/new/', views.DiaryEntryCreateView.as_view(), name='entry_create'),
    path('entry/<int:pk>/edit/', views.DiaryEntryUpdateView.as_view(), name='entry_update'),
    path('entry/<int:pk>/delete/', views.DiaryEntryDeleteView.as_view(), name='entry_delete'),
    path('home/', views.home, name='home'),
]