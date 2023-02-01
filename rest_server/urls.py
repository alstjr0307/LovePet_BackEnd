"""rest_server URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import re_path,path, include
from django.contrib import admin
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from member.views import request_user_activation,signup
import member.api
import member.push_notifications
app_name='member'

router = routers.DefaultRouter()
router.register('AuthUser', member.api.AuthUserViewSet)
router.register('BlogPostcomment', member.api.BlogPostcommentViewSet)
router.register('BlogPosts', member.api.BlogPostsViewSet)
router.register('BlogPostsLikes', member.api.BlogPostsLikesViewSet)
router.register('TaggitTag', member.api.TaggitTagViewSet)
router.register('TaggitTaggedItem', member.api.TaggitTaggeditemViewSet)
router.register(r'tag', member.api.TagViewSet)
router.register('BlogPostsList', member.api.BlogPostsListViewSet),
router.register('Vote', member.api.VoteViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('api/doc', get_swagger_view(title='Rest API Document')),
    path('api/v1/', include((router.urls, 'member'), namespace='api')),
    path("api/v2/auth/", include('djoser.urls.authtoken')),
    path('api/v2/auth/', include('djoser.urls')),
    re_path(r'^auth/users/activate/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', request_user_activation),
    path('push/<str:token>/<str:content>', member.push_notifications.send_noti, name='post_detail'),
    path('agreement/',member.api.AgreeView),
    
]