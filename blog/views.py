from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView
from .models import User, Post, PostScrap, Profile, UserLike, UserBlock
from .serializers import UserSerializer, UserRegistrationSerializer, PostSerializer, ProfileSerializer, PostScrapSerializer
from blog.gemini_api import AIMatchmake

class LoginTemplateView(TemplateView):
    template_name = 'blog/login.html'

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Register new user
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()

            # Authenticate the user
            authenticated_user = authenticate(request, email=email, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_GET
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
    permission_classes = [AllowAny]
    
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProfileCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        return Response({"detail": "Method GET not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(writer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

def HomeView(request):
    return HttpResponse("Welcome to the home page!")

class MainViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

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

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

class MyPostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(writer=user)
    
# class ProfileList(generics.ListCreateAPIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [AllowAny]
    
#     def get_queryset(self):
#         user = self.request.user
#         liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
#         blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)
        
#         filtered_profiles = Profile.objects.filter(is_recruit=True).exclude(email__in=liked_user_ids).exclude(email__in=blocked_user_ids)
        
#         other_profiles = ProfileSerializer(filtered_profiles, many=True).data
        
#         user_profile = Profile.objects.get(email=user.email)
#         user_profile_dict = ProfileSerializer(user_profile).data
        
#         matched_profiles = AIMatchmake(user_profile_dict, other_profiles)
        
#         if not matched_profiles:
#             return filtered_profiles
        
#         matched_emails = [profile['email']['email'] for profile in matched_profiles]
#         return Profile.objects.filter(email__email__in=matched_emails)

class ProfileList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # 모든 사용자 접근 가능
    
    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        
        if email is None:
            return Profile.objects.none()  # 이메일이 없으면 빈 QuerySet 반환
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Profile.objects.none()  # 해당 이메일의 사용자가 없으면 빈 QuerySet 반환
        
        liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
        blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)
        
        filtered_profiles = Profile.objects.filter(is_recruit=True).exclude(email__in=liked_user_ids).exclude(email__in=blocked_user_ids)
        
        other_profiles = ProfileSerializer(filtered_profiles, many=True).data
        
        user_profile = Profile.objects.get(email=user)
        user_profile_dict = ProfileSerializer(user_profile).data
        
        matched_profiles = AIMatchmake(user_profile_dict, other_profiles)
        
        if not matched_profiles:
            return filtered_profiles
        
        matched_emails = [profile['email'] for profile in matched_profiles]
        return Profile.objects.filter(email__in=matched_emails)

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)
        if email is None:
            return Response({"detail": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with the provided email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        return super().get(request, *args, **kwargs)


# class ProfileList(generics.ListCreateAPIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [AllowAny]  # 모든 사용자 접근 가능
    
#     def get_queryset(self):
#         email = self.request.query_params.get('email', None)
        
#         if email is None:
#             return Profile.objects.none()  # 이메일이 없으면 빈 QuerySet 반환
        
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Profile.objects.none()  # 해당 이메일의 사용자가 없으면 빈 QuerySet 반환
        
#         liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
#         blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)
        
#         filtered_profiles = Profile.objects.filter(is_recruit=True).exclude(email__in=liked_user_ids).exclude(email__in=blocked_user_ids)
        
#         other_profiles = ProfileSerializer(filtered_profiles, many=True).data
        
#         user_profile = Profile.objects.get(email=user.email)
#         user_profile_dict = ProfileSerializer(user_profile).data
        
#         matched_profiles = AIMatchmake(user_profile_dict, other_profiles)
        
#         if not matched_profiles:
#             return filtered_profiles
        
#         matched_emails = [profile['email'] for profile in matched_profiles]
#         return Profile.objects.filter(email__in=matched_emails)

#     def get(self, request, *args, **kwargs):
#         email = request.query_params.get('email', None)
#         if email is None:
#             return Response({"detail": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"detail": "User with the provided email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
#         return super().get(request, *args, **kwargs)

class LikeList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        liked_user_ids = UserLike.objects.filter(from_id=user).values_list('to_id', flat=True)
        return Profile.objects.filter(email__in=liked_user_ids)
    
class BlockList(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        blocked_user_ids = UserBlock.objects.filter(from_id=user).values_list('to_id', flat=True)
        return Profile.objects.filter(email__in=blocked_user_ids)
    
class ScrapList(generics.ListCreateAPIView):
    serializer_class = PostScrapSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        scrap_post_ids = PostScrap.objects.filter(user_id=user).values_list('post_id', flat=True)
        return Post.objects.filter(id__in=scrap_post_ids)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def like_user(request, user_id):
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_email(request, email):
    try:
        user = User.objects.get(email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
