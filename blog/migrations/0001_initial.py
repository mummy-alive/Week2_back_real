# Generated by Django 5.0.6 on 2024-07-08 14:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=70)),
                ('content', models.CharField(max_length=200)),
                ('post_tag', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profile_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_tag', models.IntegerField(choices=[(1, '1분반'), (2, '2분반'), (3, '3분반'), (4, '4분반')], default=1)),
                ('mbti', models.CharField(choices=[('ENTJ', 'ENTJ'), ('ENFJ', 'ENFJ'), ('ESFJ', 'ESFJ'), ('ESTJ', 'ESTJ'), ('ENTP', 'ENTP'), ('ENFP', 'ENFP'), ('ESFP', 'ESFP'), ('ESTP', 'ESTP'), ('INTJ', 'INTJ'), ('INFJ', 'INFJ'), ('ISFJ', 'ISFJ'), ('ISTJ', 'ISTJ'), ('INTP', 'INTP'), ('INFP', 'INFP'), ('ISFP', 'ISFP'), ('ISTP', 'ISTP')], default='INFJ', max_length=4)),
                ('interest', models.CharField(max_length=200)),
                ('is_recruit', models.BooleanField(default=True)),
                ('email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
