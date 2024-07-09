from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Post, PostTechTag, PostScrap, UserLike, UserBlock, Profile, TechTag, ProfileTechTag

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

class UserLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLike
        fields = '__all__'

class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBlock
        fields = '__all__'

class PostScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostScrap
        fields = '__all__'

class TechTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechTag
        fields = ['tech_tag_id', 'tech_tag_name']

class ProfileTechTagSerializer(serializers.ModelSerializer):
    tech_tag = TechTagSerializer(source='tech_tag_id')
    class Meta:
        model = ProfileTechTag
        fields = ['tech_tag']

class ProfileSerializer(serializers.ModelSerializer):
    tech_tags = ProfileTechTagSerializer(source='profile_tech_tags', many=True)
    email = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['profile_id', 'email', 'class_tag', 'mbti', 'interest', 'is_recruit', 'tech_tags']

    def get_tech_tags(self, obj):
        profile_tech_tags = ProfileTechTag.objects.filter(profile_id = obj.profile_id)
        return ProfileTechTagSerializer(profile_tech_tags, many=True).data

class PostTechTagSerializer(serializers.ModelSerializer):
    tech_tag = TechTagSerializer(source='tech_tag_id')
    class Meta:
        model = PostTechTag
        fields = ['tech_tag']

class PostSerializer(serializers.ModelSerializer): #역직렬화
    tech_tags = PostTechTagSerializer(source='post_tech_tags', many=True)
    writer = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = ['post_id', 'writer', 'title', 'content', 'post_tag', 'created_at', 'tech_tags']
        
    # def get_tech_tags(self, obj):
    #     post_tech_tags = PostTechTag.objects.filter(post_id = obj.post_id)
    #     return PostTechTagSerializer(post_tech_tags, many=True).data