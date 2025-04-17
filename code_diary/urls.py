from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'code_diary'

urlpatterns = [
    # Home and entry list views
    path('', views.HomeView.as_view(), name='home'),
    path('my-entries/', views.MyDiaryEntryListView.as_view(), name='my_entries'),
    path('user/<str:username>/', views.UserDiaryEntryListView.as_view(), name='user_entries'),

    # Entry CRUD views
    path('entry/<int:pk>/', views.DiaryEntryDetailView.as_view(), name='entry_detail'),
    path('entry/new/', views.DiaryEntryCreateView.as_view(), name='entry_create'),
    path('entry/<int:pk>/edit/', views.DiaryEntryUpdateView.as_view(), name='entry_update'),
    path('entry/<int:pk>/delete/', views.DiaryEntryDeleteView.as_view(), name='entry_delete'),

    # Authentication views
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # User and following views
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('following/', views.FollowingListView.as_view(), name='following'),
    path('followers/', views.FollowersListView.as_view(), name='followers'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),

    # AJAX views
    path('check-new-entries/', views.check_new_entries, name='check_new_entries'),
]
