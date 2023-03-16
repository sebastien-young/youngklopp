import sys
import time
import json
import threading
from hashlib import sha256
from datetime import datetime
import functions_framework
from google.cloud import storage
from google.cloud.storage.blob import Blob
from googleapiclient.discovery import build
from flask import abort, redirect

_yk_domain = 'youngklopp'

def create_blob (data, blob_path="gs://cdn.youngklopp.com/blob/"):
    blob_name = sha256(time.time().encode()).hexdigest()
    s_client = storage.Client()
    blob = Blob.from_string(blob_path + blob_name)
    blob.upload_from_string(json.dumps(data), content_type='application/json', client=s_client)
    return blob_name

def notify_topic (form, topic=None):
    if topic is None:
        if form['rsvp'] is None:
            _yk_topic = 'rsvp-selection'
        else:
            _yk_topic = 'rsvp-response'
        topic = ('projects/youngklopp/topics/'+_yk_topic).format(
            project_id=os.environ['GCP_PROJECT'],
            topic_name=_yk_topic
            )
    message = json.dumps(form).encode('utf-8')
    result = publisher.publish(topic, message)

def error_page ():
    return "Error"

def unauth_page ():
    return abort(403)

def success_page (blob="ERROR"):
    return redirect("https://cdn.youngklopp.com/rsvp.html?id=" + blob, code=301)

def thanks_page ():
    return redirect("https://cdn.youngklopp.com/thanks.html", code=301)

def submit (form, debug=False):
    if form is None:
        return error_page()
    if debug:
        return json.dumps(form)
    thread = threading.Thread(target=notify_topic, args=(form,))
    thread.start()
    if form['rsvp'] is not None and form['rsvp'] == "Yes":
        register = create_blob({'full_name': form['full_name']})
        response = success_page (register)
    else:
        response = thanks_page ()
    thread.join()
    return response

@functions_framework.http
def rsvp (request):
    req_form = request.form
    req_base = request.base_url
    response = unauth_page()
    if _yk_domain in req_base:
        response = submit (req_form)
    elif 'localhost' in req_base:
        response = submit (req_form, True)
    return response
