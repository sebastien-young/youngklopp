import sys
import time
import json
from hashlib import sha256
from datetime import datetime
from copy import deepcopy
import functions_framework
from google.cloud import storage
from google.cloud.storage.blob import Blob
from googleapiclient.discovery import build
from flask import redirect

newline = "\n"

_yk_domain = 'youngklopp'
_yk_workbook = '1VwE6r8kHSUK9n93xpvZyqZ0aK9KEbhSVrOb0WFh87Ww'
_yk_sheet_id = 1256412268
_yk_sheet = 'Young Klopp Interest Form'

_yk_data = [
        (lambda f : datetime.now().strftime('%m/%d/%Y %H:%M:%S')),
        (lambda f : f['full_name']),
        (lambda f : f['email']),
        (lambda f : f['phone']),
        (lambda f : f['rsvp']),
        #(lambda f : f['']),
        ]

_api_value = {
    'userEnteredValue': {
        'stringValue': ''
        }
    }

def _api_build_value (string):
    value = deepcopy (_api_value)
    value['userEnteredValue']['stringValue'] = string
    return value

def _yk_form_values (form):
    data = []
    for function in _yk_data:
        try:
            string = function (form)
        except:
            string = ''
        value = _api_build_value (string)
        data.append (value)
    return data

_api_row = {
    'values': []
    }

def _api_build_row (values):
    row = deepcopy (_api_row)
    for value in values:
        row['values'].append(value)
    return row

_api_request = {
    'appendCells': {
        'fields': '*',
        'rows': [],
        'sheetId': _yk_sheet_id
        }
    }

def _api_build_request (rows):
    request = deepcopy (_api_request)
    for row in rows:
        request['appendCells']['rows'].append (row)
    return request

_api_body = {
    'includeSpreadsheetInResponse': False,
    'requests': [],
    }

def _api_build_body (requests):
    body = deepcopy (_api_body)
    for request in requests:
        body['requests'].append (request)
    return body

def _api_submit (workbook, body):
    service = build ('sheets', 'v4')
    collection = service.spreadsheets()
    request = collection.batchUpdate (spreadsheetId=workbook, body=body)
    response = request.execute ()
    service.close()
    return response

def create_blob (data, blob_path="gs://cdn.youngklopp.com/blob/"):
    blob_name = sha256(time.time().encode()).hexdigest()
    s_client = storage.Client()
    blob = Blob.from_string(blob_path + blob_name)
    blob.upload_from_string(json.dumps(data), content_type='application/json', client=s_client)
    return blob_name

def error_page ():
    return 'Error'

def success_page (blob="ERROR"):
    return redirect("https://cdn.youngklopp.com/rsvp2.html?id=" + blob, code=301)

def thanks_page ():
    return redirect("https://cdn.youngklopp.com/thanks.html", code=301)

def submit (form, debug=False):
    if form is None:
        return error_page()
    values = _yk_form_values (form)
    row = _api_build_row (values)
    request = _api_build_request ([row])
    body = _api_build_body ([request])
    if not debug:
        response = _api_submit (_yk_workbook, body)
    if form['rsvp'] == "Yes":
        register = create_blob({'full_name': form['full_name']})
        response = success_page (register)
    else:
        response = thanks_page ()
    return response

@functions_framework.http
def rsvp (request):
    req_form = request.form
    req_base = request.base_url
    response = error_page()
    if _yk_domain in req_base:
        response = submit (req_form)
    elif 'localhost' in req_base:
        response = submit (req_form, True)
    return response
