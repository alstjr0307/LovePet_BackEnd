from pyfcm import FCMNotification
from django.http import HttpResponse
APIKEY = "AAAAQ5V5t5g:APA91bHBM7LdQ1fjQOchQEf4FPNSMzs_-buTHkNKor8Qn50O6sf5piz-V1dPe2qYZCB4JmxR2z4ZdTKJIZl9XxhKaq4trx9m9mNuOxn0IyoL0blYwKUGtV8kfnmMBPwwz5M3LG50qN0m"
push_service = FCMNotification(APIKEY)
 
def sendMessage(body, title, token):
    # 메시지 (data 타입)
    data_message = {
        "body": body,
        "title": title
    }
     # 토큰값을 이용해 1명에게 푸시알림을 전송함
    result = push_service.notify_single_device(registration_id=token, message_title=title, message_body=body, data_message = data_message)

def send_noti(request, token, content):
    sendMessage(content,'새 댓글',token)
    return HttpResponse('완료')
