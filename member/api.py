from django.db.models.fields import CharField
from .models import AuthUser, BlogPostcomment, BlogPosts, BlogPostsLikes,HitcountHit, HitcountHitcount, DjangoAdminLog, DjangoContentType, DjangoMigrations, TaggitTaggeditem,TaggitTag,Question,Choice
from rest_framework import serializers, viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django_filters import Filter, FilterSet,CharFilter
from django.db.models import OuterRef, Subquery, Count
from django_filters.widgets import CSVWidget
from django_filters.filters import Filter
from rest_framework.serializers import ValidationError
from django_filters.fields import Lookup
from django_filters import rest_framework as filters
from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from taggit.models import Tag
from django.db.models import Q
from .permissions import PostIsUserOrReadOnly, AuthUserIsAdminUserOrReadOnly, PostCommentIsUserOrReadOnly, TagIsUserOrReadOnly,PostLikesIsUserOrReadOnly, ReadOnly, TagIsUserOrReadOnly
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.shortcuts import render

from pyfcm import FCMNotification
 
APIKEY = "AAAAQ5V5t5g:APA91bHBM7LdQ1fjQOchQEf4FPNSMzs_-buTHkNKor8Qn50O6sf5piz-V1dPe2qYZCB4JmxR2z4ZdTKJIZl9XxhKaq4trx9m9mNuOxn0IyoL0blYwKUGtV8kfnmMBPwwz5M3LG50qN0m"
push_service = FCMNotification(APIKEY)
 
def sendMessage(body, title, token):
    # 메시지 (data 타입)
    data_message = {
        "body": body,
        "title": title
    }
 
    # 토큰값을 이용해 1명에게 푸시알림을 전송함
    result = push_service.single_device_data_message(registration_id=token, data_message=data_message)
 
    # 전송 결과 출력
    print(result)
class UserRegistrationSerializer(BaseUserRegistrationSerializer):


    def validate_first_name(self, attrs) :
        if not attrs:
            raise serializers.ValidationError("닉네임을 입력해주세요")
        if AuthUser.objects.filter(first_name=attrs).exists():
            raise serializers.ValidationError("닉네임이 이미 존재합니다")

        return attrs
    def validate_email(self, attrs) :
        if not attrs:
            raise serializers.ValidationError("이메일을 입력해주세요")
        if AuthUser.objects.filter(email=attrs).exists():
            raise serializers.ValidationError("이미 등록된 이메일입니다")

        return attrs

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('id','email','username','first_name','password',)
        extra_kwargs = {
            "username": 
                {
                    "error_messages": 
                    {
                        "blank": "아이디를 입력해주세요", 
                        "duplicate": "이미 아이디가 존재합니다"
                    }
                },
        }

def multiple_search(queryset, name, value):
    queryset = queryset.filter(Q(title__icontains=value) | Q(content__icontains=value))
    return queryset
def title_search(queryset, name, value):
    queryset = queryset.filter(Q(title__icontains=value))
    return queryset
def content_search(queryset, name, value):
    queryset = queryset.filter(Q(content__icontains=value))
    return queryset

class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass
class MyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug']
class TagViewSet(viewsets.ModelViewSet):
    """
    Not using taggit_serializer.serializers.TaggitSerializer because that's for listing
    tags for an instance of a model
    """
    queryset = Tag.objects.all().order_by('name')
    serializer_class = MyTagSerializer

class AccommodationFilter(filters.FilterSet):
    id_in = NumberInFilter(field_name='id', lookup_expr='in')
    likess=filters.NumberFilter(field_name = 'postlike', lookup_expr='gt')
    multisearch = filters.CharFilter(label='name or place', method=multiple_search)
    titlesearch= filters.CharFilter(label='title', method=title_search)
    contentsearch= filters.CharFilter(method=content_search)
    class Meta:
        model = BlogPosts
        fields = ['id_in', 'likess', 'category', 'owner', 'multisearch', 'titlesearch', 'contentsearch']

    def filter_status(self, queryset, name, value):
        pks = BlogPostsLikes.objects(post=value).count()
        return queryset.filter(pk__in=Subquery(pks))

class PostPageNumberPagination(PageNumberPagination):
    page_size = 10


class AuthUserSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    email = serializers.EmailField()
    class Meta:
        model = AuthUser
        fields = '__all__'
    def get_comment(self, user):
        return BlogPostcomment.objects.filter(writer=user).count()
    
    def get_post(self, user):
        return BlogPosts.objects.filter(owner=user).count()


class AuthUserViewSet(viewsets.ModelViewSet):

    queryset =AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    permission_classes = [AuthUserIsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_fields =('username',)

class BlogPostcommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='writer.first_name')
    class Meta:
        model = BlogPostcomment
        fields = '__all__'
class BlogPostcommentViewSet(viewsets.ModelViewSet):
    queryset = BlogPostcomment.objects.all()
    serializer_class = BlogPostcommentSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields =('blogpost_connected', 'writer')
    pagination_class = PostPageNumberPagination
    permission_classes = [PostCommentIsUserOrReadOnly]
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
class BlogPostsLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostsLikes
        fields = '__all__'
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
class BlogPostsLikesViewSet(viewsets.ModelViewSet):
    queryset = BlogPostsLikes.objects.all()
    permission_classes = [
        PostLikesIsUserOrReadOnly
    ]

    serializer_class = BlogPostsLikesSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ('post', 'user')

class TagFilter(filters.FilterSet):
    
    namee=filters.CharFilter(field_name = 'name', lookup_expr='exact')
    class Meta:
        model = TaggitTaggeditem
        fields = ['tag', 'namee']

    def filter_status(self, queryset, name, value):
        pks = BlogPostsLikes.objects(post=value).count()
        return queryset.filter(pk__in=Subquery(pks))

class TaggitTaggeditemSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='tag.name')
    class Meta:
        model = TaggitTaggeditem
        fields = '__all__'


class TaggitTaggeditemViewSet(viewsets.ModelViewSet):
    queryset = TaggitTaggeditem.objects.all().annotate(name=Subquery(
        TaggitTag.objects.filter(pk=OuterRef('tag')).values('name')
    )).order_by('-id')
    serializer_class = TaggitTaggeditemSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = TagFilter
    filter_fields =('tag',)
    permission_classes = [
        TagIsUserOrReadOnly
    ]
    




class TaggitTagSerializer(serializers.ModelSerializer):
    taggittaggeditem_set = TaggitTaggeditemSerializer(many=True, read_only=True)
    class Meta:
        model = TaggitTag
        fields = '__all__'

class TaggitTagViewSet(viewsets.ModelViewSet):
    queryset = TaggitTag.objects.all()
 
    serializer_class = TaggitTagSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ('name',)



class BlogPostsSerializer(TaggitSerializer, serializers.ModelSerializer):
    writer = serializers.ReadOnlyField(source='owner.first_name')
    blogpostslikes_set = BlogPostsLikesSerializer(many=True, read_only=True)
    blogpostcomment_set = BlogPostcommentSerializer(many=True, read_only=True)
    likes = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    taggittaggeditem_set = TaggitTaggeditemSerializer(many=True, read_only = True)
    def get_likes(self, post):
        qs = BlogPostsLikes.objects.filter(post=post).count()
        return qs
    def get_comment(self, post):
        return BlogPostcomment.objects.filter(blogpost_connected=post).count()

    class Meta:
        model = BlogPosts
        fields = '__all__'
    

class BlogPostsViewSet(viewsets.ModelViewSet):
    queryset = BlogPosts.objects.order_by('-create_dt').all().annotate(postlike=Coalesce(Subquery(
        BlogPostsLikes.objects.filter(post=OuterRef('pk')).values('post').annotate(count=Count('pk')).values('count')
    ),0))
    serializer_class = BlogPostsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = AccommodationFilter
    pagination_class = PostPageNumberPagination
    permission_classes = [
        PostIsUserOrReadOnly
    ]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BlogPostsListSerializer(TaggitSerializer, serializers.ModelSerializer): #게시물 리스트만
    writer = serializers.ReadOnlyField(source='owner.first_name')
   
    likes = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
   
    def get_likes(self, post):
        qs = BlogPostsLikes.objects.filter(post=post).count()
        return qs
    def get_comment(self, post):
        return BlogPostcomment.objects.filter(blogpost_connected=post).count()

    class Meta:
        model = BlogPosts
        fields = ['id', 'writer', 'likes', 'comment', 'title', 'create_dt', 'category', 'owner']
    

class BlogPostsListViewSet(viewsets.ModelViewSet):
    queryset = BlogPosts.objects.order_by('-create_dt').all().annotate(postlike=Coalesce(Subquery(
        BlogPostsLikes.objects.filter(post=OuterRef('pk')).values('post').annotate(count=Count('pk')).values('count')
    ),0))
    serializer_class = BlogPostsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = AccommodationFilter
    pagination_class = PostPageNumberPagination
    permission_classes = [
        PostIsUserOrReadOnly
    ]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DjangoAdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoAdminLog
        fields = '__all__'
class DjangoAdminLogViewSet(viewsets.ModelViewSet):
    queryset = DjangoAdminLog.objects.all()
    serializer_class = DjangoAdminLogSerializer

class DjangoContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoContentType
        fields = '__all__'
class DjangoContentTypeViewSet(viewsets.ModelViewSet):
    queryset = DjangoContentType.objects.all()
    serializer_class = DjangoContentTypeSerializer

class DjangoMigrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoMigrations
        fields = '__all__'
class DjangoMigrationsViewSet(viewsets.ModelViewSet):
    queryset = DjangoMigrations.objects.all()
    serializer_class = DjangoMigrationsSerializer



class HitcountHitcountSerializer(serializers.ModelSerializer):  

    class Meta:
        model = HitcountHitcount
        fields= '__all__'

class HitcountHitcountViewSet(viewsets.ModelViewSet):
    queryset= HitcountHitcount.objects.all()
    serializer_class=HitcountHitcountSerializer

    
class HitcountHitSerializer(serializers.ModelSerializer):
    hitcounthitcount_set = HitcountHitcountSerializer(many=True)
    class Meta:
        model = HitcountHit
        fields= '__all__'

class HitcountHitViewSet(viewsets.ModelViewSet):
    queryset= HitcountHit.objects.all()
    serializer_class=HitcountHitSerializer

def Agreeview(request):
  return render(request,"agree.html")
class VoteSerializer(serializers.ModelSerializer):
    call_count  = serializers.IntegerField(
        source = 'call.count',
        read_only=True
    )
    foot_count = serializers.IntegerField(
        source='foot.count',
        read_only=True

    )

    class Meta:
        model = Choice
        fields= '__all__'

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class= VoteSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields=['pub_date']
    permission_classes = [AuthUserIsAdminUserOrReadOnly]