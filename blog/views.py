from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from blog.models import User

from .serializers import UserSerializer, UserRegistrationSerializer, PostSerializer, ProfileSerializer, PostScrapSerializer
from .serializers import UserRegistrationSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from allauth.socialaccount.providers import registry
from blog.models import User, Post, PostScrap, Profile, UserLike, UserBlock
from blog.gemini_api import AIMatchmake

class LoginTemplateView(TemplateView):
    template_name = 'blog/login.html'

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f'Email: {email}, Pasword: {password}')
        user = authenticate(request, email=email, password=password)
        print(f'Authenticated user: {user}')
        if user is not None:
            # User authentication successful
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})
            # return Response(UserSerializer(user).data)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            '''try:
                # Try to get a user with the given email
                user = user.objects.get(email=email)
                # User with the email exists, so the password must be incorrect
                return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # User with the email does not exist
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)'''

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token':token.key,
                             "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_GET    #클라이언트의 요청이 들어오면:
def check_user(request):
    email = request.GET.get('email', None)
    response_data = {'exists': False}

    if email:
        try:
            user = User.objects.get(email=email)
            response_data['exists'] = True
        except ObjectDoesNotExist:
            response_data['exists'] = False

    return JsonResponse(response_data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(writer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

def HomeView(request):          # 온보딩
    return HttpResponse("Welcome to the home page!")

class MainViewSet(viewsets.ViewSet):  # 1번탭
    permission_classes = [IsAuthenticated]

    def list(self, request):
        recent_posts = Post.objects.order_by('-created_at')[:4]

        user = request.user
        liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
        blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)

        filtered_profiles = Profile.objects.filter(is_recruit=True).exclude(email__in=liked_user_ids).exclude(email__in=blocked_user_ids)
        other_profiles = ProfileSerializer(filtered_profiles, many=True).data

        user_profile = Profile.objects.get(email=user.email)
        user_profile_dict = ProfileSerializer(user_profile).data

        matched_profiles = AIMatchmake(user_profile_dict, other_profiles)
        matched_emails = [profile['email']['email'] for profile in matched_profiles]

        profiles = Profile.objects.filter(email__email__in=matched_emails)[:4]

        response_data = {
            'recent_posts': PostSerializer(recent_posts, many=True).data,
            'profiles': ProfileSerializer(profiles, many=True).data
        }

        return Response(response_data)

class PostList(generics.ListCreateAPIView): # 2번탭
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostDetail(generics.RetrieveUpdateDestroyAPIView):    # 2번탭 - Post 세부내용
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostListCreateView(generics.ListCreateAPIView):   #게시물 생성
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

class MyPostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(writer=user)
    
class ProfileList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user = self.request.user
        liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
        blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)
        
        filtered_profiles = Profile.objects.filter(is_recruit=True).exclude(email__in=liked_user_ids).exclude(email__in=blocked_user_ids)
        
        other_profiles = ProfileSerializer(filtered_profiles, many=True).data
        
        user_profile = Profile.objects.get(email=user.email)
        user_profile_dict = ProfileSerializer(user_profile).data
        
        matched_profiles = AIMatchmake(user_profile_dict, other_profiles)
        
        matched_emails = [profile['email']['email'] for profile in matched_profiles]
        return Profile.objects.filter(email__email__in=matched_emails)

class LikeList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] #권한수정 필요할수도?

    def get_queryset(self):
        user = self.request.user
        liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
        return Profile.objects.filter(email__in=liked_user_ids)
    
class BlockList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] #권한수정 필요할수도?

    def get_queryset(self):
        user = self.request.user
        blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id',flat=True)
        return Profile.objects.filter(email__in=blocked_user_ids)
    
class ScrapList(generics.ListCreateAPIView):
    serializer_class = PostScrapSerializer
    permission_classes = [IsAuthenticated] #권한수정 필요할수도?

    def get_queryset(self):
        user = self.request.user
        scrap_post_ids = PostScrap.objects.filter(user_id=user).values_list('post_id', flat=True)
        return Post.objects.filter(id__in=scrap_post_ids)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_user(request,user_id):
    try:
        to_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    like, created = UserLike.objects.get_or_create(from_id=request.user, to_id=to_user)
    if created:
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request, user_id):
    try:
        to_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    block, created = UserBlock.objects.get_or_create(from_id=request.user, to_id=to_user)
    if created:
        return Response({'status': 'blocked'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'status': 'already blocked'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scrap_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    scrap, created = PostScrap.objects.get_or_create(user_id=request.user, post_id=post)
    
    if created:
        return Response({'status': 'scrapped'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'status': 'already scrapped'}, status=status.HTTP_200_OK)

def check_user_by_mail(request, email):
    user_exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': user_exists})

