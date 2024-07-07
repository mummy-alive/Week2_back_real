from django.urls import path

from . import views
from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    get_member_profile,
    HomeView,
    PostList,
    PostDetail,
    check_member_by_mail,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', get_member_profile, name='get_member_profile'),
    path('checkMember/', views.check_member, name='check_member'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', HomeView, name='home'),
    path('posts/', PostList.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
#    path('checkMemberByMail/<str:Mail>/', check_member_by_mail, name='check_member_by_Mail'),
]