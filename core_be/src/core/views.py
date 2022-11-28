from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..account.models import User
from ..core.utils.firebase import notify_by_user_ids_v1, notify_by_fcm_tokens_v1, notify_by_fcm_tokens

from ..core.utils.firebase import _check_fcm_token_valid

def healthcheck(request):
    return 'pong'


def testnoti1(request):
    test = _check_fcm_token_valid("1111-8SgKDZkKT0-NHEJ6wKTPRKm8qRcAwwJor93")
    fcm_tokens = list(User.objects.filter(fcm_token__isnull=False).values_list("fcm_token", flat=True))
    notify_by_fcm_tokens_v1.delay(
        fcm_tokens=fcm_tokens,
        message_title="tony fcm test 1 (notify_recipients)",
        message_body="tony test body. sorry for spam!",
        data_message=None
    )
    return JsonResponse(data={'testnoti1':test}, status=200)


def testnoti2(request):
    user_ids = list(User.objects.filter(fcm_token__isnull=False).values_list("id", flat=True))
    notify_by_user_ids_v1.delay(
        user_ids=user_ids,
        message_title="tony fcm test 2 (notify_by_fcm_tokens_v1)",
        message_body="tony test body. sorry for spam!",
        data_message={}
    )
    return JsonResponse(data={'testnoti2':'ok'}, status=200)


def testnoti3(request):
    # recipients = User.objects.filter(fcm_token__isnull=False, flat=True).values('fcm_token')
    fcm_tokens = list(User.objects.filter(fcm_token__isnull=False).values_list("fcm_token", flat=True))
    try:
        notify_by_fcm_tokens.delay(
            fcm_tokens=fcm_tokens,
            message_title="tony fcm test 3 (notify_by_fcm_tokens)",
            message_body="tony test body. sorry for spam!"
        )
    except Exception as e:
        print(str(e))
        print(':::::::::::::::::::::::::::::::::::::::::::;')
    return JsonResponse(data={'testnoti3':'ok'}, status=200)


def record_to_txt(data):
    with open("src/9pay.log", "a") as f:
        f.write(timezone.now().isoformat()+"\n")
        f.write(str(data)+"\n\n")
