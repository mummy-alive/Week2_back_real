from django.urls import path

from . import views
from .views import (
    LoginTemplateView,
    LoginAPIView,
    LogoutView,
    RegisterView,
    get_user_profile,
    HomeView,
    PostList,
    PostDetail,
    ProfileList,
    check_user_by_mail,
)

urlpatterns = [
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('api/login', LoginAPIView.as_view(), name='api-login'),
    path('register/', RegisterView.as_view(), name='register'),

    path('api/profile/', ProfileList.as_view(), name='profile-list'),
    
    path('checkUser/', views.check_user, name='check_user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('', HomeView, name='home'),
    
    path('api/posts/', PostList.as_view(), name='postlist'),
    path('api/posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
#    path('checkUserByMail/<str:Mail>/', check_user_by_mail, name='check_user_by_Mail'),
]