import json
import requests
import time

from firebase_admin import firestore

from ..account.models import User
from ..celeryconf import app

from .utils.firebase import firebase_initialize_app


dataRecordReplies = []
dataResponses = {}


def update_firestore(db):
    # print("Updating....")
    len_dataRecordReplies = len(dataRecordReplies)
    for index, record in enumerate(dataRecordReplies):
        # if round(index / len_dataRecordReplies*100) % 10==0:
        #     print("updating ...", round(index / len_dataRecordReplies*100))
        userID = record["id"]
        dataResponse = dataResponses.get(userID)
        data_update = {
            u"responseTime": record["timeTotal"] / record["count"] / 3600,
            u"responseRate": 0 if dataResponse is None else (100 * dataResponse["ok"]) / (dataResponse["ok"] + dataResponse["failed"])
        }
        db.collection(u"Users").document(userID).update(data_update)
    return


def testing_dataResponses():
    print("Checking...")
    firebase_initialize_app()
    db = firestore.client()
    f = open("src/core/dataResponses.json", "r")
    crawl_data = json.load(f)
    user_docs = db.collection(u'Users').stream()
    true_100 = 0
    true_99 = 0
    true_95 = 0
    true_90 = 0
    true_50 = 0
    fail = 0
    count = 0
    failed_user = 0
    users_zzz = []
    for doc in user_docs:
        if count % 100 == 0:
            print("Running: ", count)
        data_doc = doc.to_dict()
        responseRate = data_doc.get("responseRate", None)
        if responseRate is not None:
            raw_data = crawl_data.get(doc.id)
            if raw_data is None:
                # print(doc.id, data_doc["sssId"])
                users_zzz.append(doc.id)
                failed_user += 1
            else:
                new_responseRate = (
                    100 * raw_data["ok"]) / (raw_data["ok"] + raw_data["failed"])
                saiso = abs(new_responseRate-responseRate)
                if saiso == 0:
                    true_100 += 1
                elif saiso <= 1:
                    true_99 += 1
                elif saiso <= 5:
                    true_95 += 1
                elif saiso <= 10:
                    true_90 += 1
                elif saiso <= 50:
                    true_50 += 1
                else:
                    fail += 1
            count += 1
    with open("src/core/fail_user.text", "w") as f:
        f.write(str(users_zzz))
    print(true_100/count*100, true_99/count*100, true_95/count*100,
          true_90/count*100, true_50/count*100, fail/count*100, failed_user/count*100)
