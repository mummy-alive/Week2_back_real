from django.urls import path

from . import views
from .views import (
    LoginView,
    RegisterView,
    get_member_profile,
    HomeView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', get_member_profile, name='get_member_profile'),
    path('checkMember/', views.check_member, name='check_member'),
    path('', HomeView, name='home'),
]