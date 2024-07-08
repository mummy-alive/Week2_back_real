from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password, name, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email , password=None, **extra_fields): #, password, name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
        #return self.create_user(email, password, name, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  
    name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()
    
    def __str__(self):
        return self.email

class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    email = models.OneToOneField(User, on_delete=models.CASCADE)
    
    class ClassTag(models.IntegerChoices):
        Tag1 = 1, '1분반'
        Tag2 = 2, '2분반'
        Tag3 = 3, '3분반'
        Tag4 = 4, '4분반'
    
    class MBTI(models.TextChoices):
        ENTJ = 'ENTJ', 'ENTJ'
        ENFJ = 'ENFJ', 'ENFJ'
        ESFJ = 'ESFJ', 'ESFJ'
        ESTJ = 'ESTJ', 'ESTJ'
        ENTP = 'ENTP', 'ENTP'
        ENFP = 'ENFP', 'ENFP'
        ESFP = 'ESFP', 'ESFP'
        ESTP = 'ESTP', 'ESTP'
        INTJ = 'INTJ', 'INTJ'
        INFJ = 'INFJ', 'INFJ'
        ISFJ = 'ISFJ', 'ISFJ'
        ISTJ = 'ISTJ', 'ISTJ'
        INTP = 'INTP', 'INTP'
        INFP = 'INFP', 'INFP'
        ISFP = 'ISFP', 'ISFP'
        ISTP = 'ISTP', 'ISTP'
        
    class_tag = models.IntegerField(choices = ClassTag.choices, default=ClassTag.Tag1)
    mbti = models.CharField(choices = MBTI.choices, max_length = 4, default=MBTI.INFJ)
    interest = models.CharField(max_length = 200)
    is_recruit = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.email.email} - {self.mbti}'

class TechTag(models.Model):      
    tech_tag_id = models.AutoField(primary_key=True)
    tech_tag_name = models.CharField(max_length=40)

class ProfileTechTag(models.Model):
    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name ='profile_tech_tags')
    tech_tag_id = models.ForeignKey(TechTag, on_delete=models.CASCADE, related_name ='profile_tech_tags')
    # primary key는 (profile_id, tech_tag_id)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile_id', 'tech_tag_id'], name='unique_profile_tech_tag')
        ]
        
    def __str__(self):
        return f"{self.profile_id} - {self.tech_tag_id}"

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=70)
    content = models.CharField(max_length=200)
    post_tag = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    def created_at_seoul_time(self):
        return self.created_at.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M")