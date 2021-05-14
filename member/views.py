from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests


class UserActivationView(APIView):
    permission_classes = [AllowAny]
    def get (self, request, uid, token):
        protocol = 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/api/v2/auth/users/activation/"
        post_data = {'uid': uid, 'token': token}
        result = requests.post(post_url, data = post_data)
        content = result.text()
        return Response(content)