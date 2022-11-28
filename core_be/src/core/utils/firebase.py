import io
import json
import firebase_admin
import requests
import logging

from typing import Any
from django.db.models.query import QuerySet
from firebase_admin import auth, credentials, messaging, firestore

from ...celeryconf import app
from ...account.models import User

CREDENTIALS_FIREBASE_PATH = "src/core/utils/firebase-adminsdk.json"
PATH_STORE_FETCHED_REMOTE_CONFIG = 'src/core/utils/firebase_remote_config.json'


class ProviderId:
    EMAIL_AUTH = "password"


def firebase_initialize_app():
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(CREDENTIALS_FIREBASE_PATH)
        firebase_admin.initialize_app(cred)


def _get_access_token():
    cred = credentials.Certificate(CREDENTIALS_FIREBASE_PATH)
    token = cred.get_access_token().access_token
    return token


def _get_remmote_config():
    firebase_initialize_app()
    PROJECT_ID = firebase_admin.get_app().project_id
    print(">>>>>>>>>>>>>: ", PROJECT_ID)
    BASE_URL = 'https://firebaseremoteconfig.googleapis.com'
    REMOTE_CONFIG_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/remoteConfig'
    REMOTE_CONFIG_URL = BASE_URL + '/' + REMOTE_CONFIG_ENDPOINT

    headers = {
        'Authorization': 'Bearer ' + _get_access_token()
    }
    resp = requests.get(REMOTE_CONFIG_URL, headers=headers)

    if resp.status_code == 200:
        with io.open(PATH_STORE_FETCHED_REMOTE_CONFIG, 'wb') as f:
            f.write(resp.text.encode('utf-8'))

        print('Retrieved template has been written to config.json')
        print('ETag from server: {}'.format(resp.headers['ETag']))
    else:
        print('Unable to get template')
        print(resp.text)


def get_remote_config_by_tag(tag, default: Any = "") -> str:
    """
    Read config from local storage file.
    """
    try:
        with io.open(PATH_STORE_FETCHED_REMOTE_CONFIG, 'r') as f:
            data = json.load(f)

        return data["parameters"][tag]["defaultValue"]["value"]
    except (KeyError, FileNotFoundError):
        return default


def verify_id_token_and_get_detail_user(id_token):
    firebase_initialize_app()
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get("uid")
        user_info_on_firebase = auth.get_user(uid).__dict__
        return user_info_on_firebase
    except Exception as err:
        raise err
        # raise ValidationError({"firebase": ValidationError(
        #     "User is invalid on Firebase", code=AccountErrorCode.VERIFY_FAIL.value)})


def _check_fcm_token_valid(fcm_token):
    # TODO: all tokens is valid !!?
    firebase_initialize_app()
    message = messaging.Message(
        token=fcm_token,
    )
    try:
        messaging.send(message, dry_run=True)
    except firebase_admin.exceptions.FirebaseError as e:
        if e.code == "NOT_FOUND":
            return False
    return True


# def get_user_on_firestore(user):
#     if not user.firebase_uid:
#         return None
#     firebase_initialize_app()
#     db = firestore.client()
#     doc_ref = db.collection("Users").document(user.firebase_uid)
#     doc = doc_ref.get()
#     if doc.exists:
#         return doc.to_dict()
#     return None

# def get_badge_number(user):
#     user_on_firestore = get_user_on_firestore(user)
#     total_unread_chat = (
#         user_on_firestore.get("totalUnreadNotification", 0) if user_on_firestore else 0
#     )
#     total_unread_other = user.concat_notifications.unread().count()
#     return total_unread_chat + total_unread_other

# def get_badge_number(user):
    # TODO: get from db

@app.task
def notify_by_fcm_tokens_v1(
    fcm_tokens, message_title: str, message_body: str, data_message=None, **kwargs
):
    registration_tokens = list(filter(None, fcm_tokens))
    if len(registration_tokens) > 0:
        firebase_initialize_app()
        # Create a list containing up to 500 registration tokens.
        # These registration tokens come from the client FCM SDKs.
        notification = messaging.Notification(
            title=message_title, body=message_body, image=kwargs.get(
                "image", "")
        )
        success_ids = []
        failure_count = 0
        tracing_data_update = {
            "message_title": message_title, "message_body": message_body}
        # badge_number = get_badge_number(recipient)
        android = messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                priority="high",
                default_sound=True
                # , notification_count=badge_number
            )
        )
        apns = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    # badge=badge_number,
                    mutable_content=True
                )
            ),
            headers={
                "apns-priority": "10",
            },
        )
        try:
            message = messaging.MulticastMessage(
                tokens=registration_tokens,
                data=data_message,
                notification=notification,
                apns=apns,
                android=android,
            )
            batch_response = messaging.send_multicast(message)

            failure_count += batch_response.failure_count
        except Exception as e:
            tracing_data_update["responses"] = [{"exception": str(e)}]
            batch_response = None
            logging.error("::::: [notify_by_fcm_tokens_v1] Error send push notification :: " + str(e))
        return (success_ids, failure_count)
    else:
        # raise ValueError('No registration tokens')
        logging.warning("::::: [notify_by_fcm_tokens_v1] No registration tokens :::::")


@app.task    
def notify_by_user_ids_v1(
    user_ids, message_title: str, message_body: str, data_message={}, **kwargs
):
    registration_tokens = list(User.objects.filter(id__in=user_ids, fcm_token__isnull=False).values_list("fcm_token", flat=True))
    if len(registration_tokens) > 0:
        firebase_initialize_app()
        notification = messaging.Notification(
            title=message_title, body=message_body, image=kwargs.get(
                "image", "")
        )
        if data_message is None:
            data_message = {}
        data_message["click_action"] = "FLUTTER_NOTIFICATION_CLICK"
        data_message["channel"] = "message_channel"
        subtitle = kwargs.get("subtitle", "")
        data_message["subText"] = subtitle
        # badge_number = get_badge_number(recipient)
        android = messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                priority="high", default_sound=True
                # , notification_count=badge_number
            )
        )
        apns = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    # badge=badge_number,
                    alert=messaging.ApsAlert(subtitle=subtitle),
                    mutable_content=True,
                ),
                headers={
                    "apns-priority": "10",
                },
            )
        )
        multicast_message = messaging.MulticastMessage(
            tokens=registration_tokens,
            data=data_message,
            notification=notification,
            apns=apns,
            android=android,
        )
        messaging.send_multicast(multicast_message)
        
        
        if len(registration_tokens) < len(user_ids):
            logging.warning("::::: [notify_by_user_ids_v1] One or some users are missing fcm_token :::::")
    else:
        # raise ValueError('No registration tokens')
        logging.warning("::::: [notify_by_user_ids_v1] No registration tokens :::::")


@app.task
def notify_by_fcm_tokens(
    fcm_tokens, message_title: str, message_body: str, **kwargs
):
    """
    Push notification for chat with only TITLE and BODY (simplest data)
    """
    registration_tokens = list(filter(None, fcm_tokens))
    if len(registration_tokens) > 0:
        firebase_initialize_app()
        notification = messaging.Notification(
            title=message_title, body=message_body)
        android_notification = messaging.AndroidNotification(priority="high")
        android = messaging.AndroidConfig(notification=android_notification)
        apns = messaging.APNSConfig(
            payload=messaging.APNSPayload(aps=messaging.Aps(badge=1)),
            headers={
                "apns-priority": "10",
            },
        )
        multicast_message = messaging.MulticastMessage(
            tokens=registration_tokens,
            notification=notification,
            apns=apns,
            android=android,
        )
        messaging.send_multicast(multicast_message)
    else:
        # raise ValueError('No registration tokens')
        logging.warning("::::: [notify_by_fcm_tokens] No registration tokens :::::")
