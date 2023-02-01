from rest_framework import permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
# views.py
from rest_framework.permissions import AllowAny
import urllib 
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import response, HttpResponseRedirect, HttpResponse
import requests,json
from rest_auth.registration.views import SocialLoginView                   
from allauth.socialaccount.providers.kakao import views as kakao_views     
from allauth.socialaccount.providers.oauth2.client import OAuth2Client                 
from .models import AuthUser  
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User

log = logging.getLogger('pybo')

class KakaoException(Exception):
    pass

class R(Exception):
    pass
# access token 요청 함수
@permission_classes([permissions.AllowAny])
def kakao_callback(request):

    try:
        app_rest_api_key = '97a132b9aa0807ebb166f18e1bae41f9'
        redirect_uri = "http://13.125.62.90/account/login/kakao/callback"
        client_secret = "AIBSCdKQ2RhvZoeqKCtOebznLxV99vua"
        user_token = request.GET.get("code")
        dataf= {
            'grant_type':"authorization_code",
            'client_id': app_rest_api_key,
            'redirect_uri': redirect_uri,
            'code': user_token
        }
        # post request
        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token", data=dataf
        )
        token_response_json = token_request.json()
        error = token_response_json.get("error", None)
        error_code = token_response_json.get("error_code", None)
        # if there is an error from token_request
        if error is not None :
            log.debug(error)
            raise R(error_code)
        access_token = token_response_json.get("access_token")

        # post request
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()

        # parsing profile json
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        if email is None:
            raise KakaoException()   # 이메일은 필수제공 항목이 아니므로 수정 필요 (비즈니스 채널을 연결하면 검수 신청 후 필수 변환 가능)
        profile = kakao_account.get("profile")
        nickname = profile.get("nickname")
        profile_image = profile.get("thumbnail_image_url")   # 사이즈 'thumbnail_image_url' < 'profile_image_url'
        print('image', profile_image)

        try:   
            user_in_db = AuthUser.objects.get(email=email)
            # kakao계정 email이 서비스에 이미 따로 가입된 email 과 충돌한다면
            print('트라이부분')
            
            # 서비스에 rest-auth 로그인
            data = {'code': user_token, 'access_token': access_token}
            accept = requests.post("http://13.125.62.90/account/login/kakao/todjango", data=data)
            print(accept)
            accept_json = accept.json()
            accept_jwt = accept_json.get("token")
            # 프로필 정보 업데이트 
            AuthUser.objects.filter(email=email).update(first_name=nickname,
                                                    email=email,
                                                    is_active=True
                                                    )

        except AuthUser.DoesNotExist:
            print('이메일중복x')
            # 서비스에 rest-auth 로그인
            data = {'code': user_token, 'access_token': access_token}
            session = requests.Session()
            accept = session.post("http://13.125.62.90/account/login/kakao/todjango/", data=data)
            print('accept')
            accept_json = accept.json()
            accept_jwt = accept_json.get("token")

            AuthUser.objects.filter(email=email).update(realname=nickname,
                                                    email=email,
                                                    user_type='kakao',
                                                    profile_image=profile_image,
                                                    is_active=True
                                                    )
        return redirect("http://13.125.62.90/")   # 메인 페이지

    except KakaoException:
        return redirect("http://13.125.62.90/account/login")

    except R:

        return redirect(f"http://13.125.62.90/api/{error_code}")
        
@permission_classes([permissions.AllowAny])
def kakao_login(request):
    app_rest_api_key = '97a132b9aa0807ebb166f18e1bae41f9'
    redirect_uri = "http://13.125.62.90/account/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )
       
class KakaoToDjangoLogin(SocialLoginView): 
    adapter_class = kakao_views.KakaoOAuth2Adapter  
    client_class = OAuth2Client 
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def request_user_activation(request, uid, token):
    """ 
    Intermediate view to activate a user's email. 
    """
    post_url = "http://13.125.62.90/api/v2/auth/users/activation/"
    post_data = {"uid": uid, "token": token}
    print(post_data)
    jsonData= json.dumps(post_data)
    headers = {'User-Agent': 'Mozilla/5.0'}
    connect_timeout, read_timeout = 5.0, 30.0
    print('직전')
    result = requests.post(post_url, data=post_data, headers=headers)

    return redirect(f'https://www.stockstorage.net')


@csrf_exempt
def signup(request):
    username = request.POST.get("username")
    try:
        user = User.objects.get(username=username)
    except:
        user= User.objects.create_user(username=username, email='', password='1234')
        user.first_name='회원'+str(user.id)
        user.save()   
    user.set_password('1234')
    user.save()
    return JsonResponse(
        {
            '됐':user.first_name
        }
    )
def Ads(request):
    return HttpResponse("google.com, pub-6925657557995580, DIRECT, f08c47fec0942fa0")


    