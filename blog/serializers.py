from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Post

# serializer: 데이터베이스에서 뽑은 데이터를 json으로 직렬화 or 역직렬화해주는 부분
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the user through the User model manager
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserRegistrationSerializer, self).create(validated_data)
        '''user = User.objects.create_User(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            # Add other fields if necessary
        )
        return user'''

class UserSerializer(serializers.ModelSerializer): #직렬화
    class Meta:
        model = User
        fields = ['id', 'email', 'name']
        extra_kwargs = {'email': {'read_only': True}}

class PostSerializer(serializers.ModelSerializer): #역직렬화
    writer = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'writer', 'title', 'content', 'post_tag', 'created_at']