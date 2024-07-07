from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Member, Post

# serializer: 데이터베이스에서 뽑은 데이터를 json으로 직렬화 or 역직렬화해주는 부분
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the member through the Member model manager
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserRegistrationSerializer, self).create(validated_data)
        '''member = Member.objects.create_member(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            # Add other fields if necessary
        )
        return member'''

class UserSerializer(serializers.ModelSerializer): #직렬화
    class Meta:
        model = Member
        fields = ['id', 'email', 'name']
        extra_kwargs = {'email': {'read_pnly': True}}

class PostSerializer(serializers.ModelSerializer): #역직렬화
    writer = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'writer', 'title', 'content', 'post_tag', 'created_at']