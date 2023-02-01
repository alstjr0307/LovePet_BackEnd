# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import timezone
import datetime
from django.db import models
from taggit.managers import TaggableManager

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=10)
    first_name = models.CharField(max_length=10, unique=True)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254, unique=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BlogPostcomment(models.Model):
    content = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    blogpost_connected = models.ForeignKey('BlogPosts', on_delete = models.CASCADE)
    writer = models.ForeignKey(AuthUser, on_delete = models.CASCADE)

    class Meta:
        managed = False
        db_table = 'blog_postcomment'


class BlogPosts(models.Model):
    title = models.CharField(max_length=40)
    slug = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    content = models.TextField()
    create_dt = models.DateTimeField()
    modify_dt = models.DateTimeField()
    category = models.CharField(max_length=1)
    owner = models.ForeignKey(AuthUser, on_delete = models.CASCADE, blank=True, null=True)
    tags = TaggableManager(blank=True)
    pushtoken= models.CharField(max_length=200,blank=True, default='00')

    def get_tags_display(self):
        return self.tags.values_list('name', flat=True)
     
    class Meta:
        managed = False
        db_table = 'blog_posts'


class BlogPostsLikes(models.Model):
    post = models.ForeignKey(BlogPosts, on_delete = models.CASCADE)
    user = models.ForeignKey(AuthUser, on_delete = models.CASCADE)

    class Meta:
        managed = False
        db_table = 'blog_posts_likes'
        unique_together = (('post', 'user'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class TaggitTag(models.Model):
    name = models.CharField(unique=True, max_length=100)
    slug = models.CharField(unique=False, max_length=100, default='none')

    class Meta:
        managed = False
        db_table = 'taggit_tag'


class TaggitTaggeditem(models.Model):
    content_type = models.ForeignKey(DjangoContentType, on_delete = models.CASCADE)
    tag = models.ForeignKey(TaggitTag, on_delete = models.CASCADE)
    object = models.ForeignKey(BlogPosts, on_delete = models.CASCADE)

    class Meta:
        managed = False
        db_table = 'taggit_taggeditem'
        unique_together = (('content_type', 'object_id', 'tag'),)

class HitcountHit(models.Model) :
    object_pk= models.IntegerField()
    content_type_id = models.IntegerField()
    modified = models.DateTimeField()
    hits = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'hitcount_hit_count'

class HitcountHitcount(models.Model) :
    ip = models.CharField(max_length=40)
    session = models.CharField(max_length = 40)
    user_agent = models.CharField(max_length = 255)
    hitcount = models.ForeignKey(HitcountHit, on_delete= models.CASCADE)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'hitcount_hit'
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.CharField(max_length=30)

    def __str__(self):
        return self.pub_date

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

# Create your models here.
class Choice(models.Model):
    pub_date = models.CharField(max_length=30,default = datetime.datetime.now().strftime('%y-%m-%d'))

    call = models.ManyToManyField(AuthUser,related_name='call',blank=True)
    foot = models.ManyToManyField(AuthUser,related_name='foot',blank=True)
    def __str__(self):
        return self.pub_date
