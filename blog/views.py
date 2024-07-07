from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from blog.models import Member

from .serializers import UserSerializer, UserRegistrationSerializer, PostSerializer
from .serializers import UserRegistrationSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from blog.models import Member, Post

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f'Email: {email}, Pasword: {password}')
        member = authenticate(request, email=email, password=password)
        print(f'Authenticated user: {member}')
        if member is not None:
            # User authentication successful
            login(request, member)
            token, created = Token.objects.get_or_create(user=member)
            return Response({'token': token.key, 'user': UserSerializer(member).data})
            # return Response(UserSerializer(member).data)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            '''try:
                # Try to get a user with the given email
                member = Member.objects.get(email=email)
                # User with the email exists, so the password must be incorrect
                return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
            except Member.DoesNotExist:
                # User with the email does not exist
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)'''

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            token, created = Token.objects.get_or_create(user=member)
            return Response({'token':token.key,
                             "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_GET
def check_member(request):
    email = request.GET.get('email', None)
    response_data = {'exists': False}

    if email:
        try:
            member = Member.objects.get(email=email)
            response_data['exists'] = True
        except ObjectDoesNotExist:
            response_data['exists'] = False

    return JsonResponse(response_data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.member.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_member_profile(request):
    member = request.member
    serializer = UserSerializer(member)
    return Response(serializer.data)

def HomeView(request):
    return HttpResponse("Welcome to the home page!")

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class PostListCreateView(generics.ListCreateAPIView):   #게시물 생성
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(writer=self.request.member)

def check_member_by_mail(request, email):
    member_exists = Member.objects.filter(email=email).exists()
    return JsonResponse({'exists': member_exists})