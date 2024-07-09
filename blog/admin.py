from django.contrib import admin
from .models import User, Post, PostTechTag, PostScrap, UserLike, UserBlock, Profile, TechTag, ProfileTechTag

admin.site.register(User)
admin.site.register(Post)
admin.site.register(PostScrap)
admin.site.register(PostTechTag)
admin.site.register(UserLike)
admin.site.register(UserBlock)
admin.site.register(Profile)
admin.site.register(TechTag)
admin.site.register(ProfileTechTag)