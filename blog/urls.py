from django.urls import path

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    LoginTemplateView,
    LoginAPIView,
    LogoutView,
    RegisterView,
    get_user_profile,
    HomeView,
    PostList,
    PostDetail,
    MyPostList,
    ProfileList,
    LikeList,
    BlockList,
    ScrapList,
    check_user_by_mail,
    like_user,
    block_user,
)

urlpatterns = [
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('register/', RegisterView.as_view(), name='register'),

    path('api/token/', TokenObtainPairView.as_view(), name = 'token-obtain-pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),

    # ToDo: Create Tab1 View

    path('api/posts/', PostList.as_view(), name='postlist'),                #2번탭 - 전체리스트
    path('api/posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),  #2번탭 - 상세보기

    path('api/profilelist/', ProfileList.as_view(), name='profile-list'),   # 3번탭
    path('api/like/', like_user, name='like_user'),                         # 좋아요
    path('api/block/', block_user, name='block_user'),                      # 싫어요
    
    path('checkUser/', views.check_user, name='check_user'),                # 얜 뭐임?
    
    path('logout/', LogoutView.as_view(), name='logout'),                   # 로그아웃
    

    path('', HomeView, name='home'),    #온보딩

    #path('api/myTab')                                                      # 5번탭
    #path('api/myTab/profile'),                                             # 5번탭 내프로필 수정
    path('api/myTab/likelist/', LikeList.as_view(), name='like-list'),      #5번탭 좋아요 누른 사람
    path('api/myTab/blocklist/', BlockList.as_view(), name='block-list'),   #5번탭 차단한 사람
    path('api/myTab/scraplist/', ScrapList.as_view(), name='scrap-list'),   #5번탭 내가 스크랩한 글
    path('api/mypostlist/', MyPostList.as_view(), name='my-posts'),         #5번탭 내가 쓴 글

#    path('checkUserByMail/<str:Mail>/', check_user_by_mail, name='check_user_by_Mail'),
]