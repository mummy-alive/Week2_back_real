from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class MemberManager(BaseUserManager):
    def create_member(self, email, password, name, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        if not password:
            raise ValueError('The Password must be set')
        if not name:
            raise ValueError('The Name must be set')
        email = self.normalize_email(email)
        member = self.model(email=email, name=name, **extra_fields)
        member.set_password(password)
        member.save(using=self._db)
        return member
    
    def create_superuser(self, email, password, name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_member(email, password, name, **extra_fields)

class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  
    name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = MemberManager()
    
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        # Simplest possible answer: Yes, always
        return True    

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    writer = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=70)
    content = models.CharField(max_length=200)
    post_tag = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
