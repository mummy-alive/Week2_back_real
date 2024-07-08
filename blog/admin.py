from django.contrib import admin
from .models import User, Post, Profile, TechTag, ProfileTechTag

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(TechTag)
admin.site.register(ProfileTechTag)