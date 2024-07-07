from rest_framework import serializers
from .models import Member, Post


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the member through the Member model manager
        member = Member.objects.create_member(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            # Add other fields if necessary
        )
        return member

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'email', 'name']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'writer', 'title', 'content', 'post_tag', 'created_at']