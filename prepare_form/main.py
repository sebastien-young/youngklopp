import sys
from datetime import datetime
from copy import deepcopy
import functions_framework
from googleapiclient.discovery import build

newline = "\n"

_yk_domain = 'youngklopp'
_yk_workbook = '1VwE6r8kHSUK9n93xpvZyqZ0aK9KEbhSVrOb0WFh87Ww'
_yk_sheet_id = 644811057
_yk_sheet = 'Young Klopp Interest Form'

_yk_address = [
    (lambda f : '' if f['address'] is None else f['address']+newline),
    (lambda f : '' if f['line2'] is None else f['line2']+newline),
    (lambda f : '' if f['city'] is None else f['city']+', '),
    (lambda f : '' if f['state'] is None else f['state']+' '),
    (lambda f : '' if f['zip'] is None else f['zip'])
    ]

def _yk_compile_address (form):
    address = ''
    for function in _yk_address:
        try:
            string = function (form)
        except:
            string = ''
        address += string
    if not address:
        return None
    return address

_yk_data = [
    (lambda f : datetime.now().strftime('%m/%d/%Y %H:%M:%S')),
    (lambda f : f['email']),
    (lambda f : f['full_name']),
    (lambda f : _yk_compile_address(f)),
    (lambda f : f['phone']),
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

def error_page():
    return 'Error'

def success_page():
    return 'Submitted!'

def submit (form, debug=False):
    if form is None:
        return error_page()
    values = _yk_form_values (form)
    row = _api_build_row (values)
    request = _api_build_request ([row])
    body = _api_build_body ([request])
    if not debug:
        response = _api_submit (_yk_workbook, body)
        response = success_page ()
    else:
        response = body
    return response

@functions_framework.http
def guest (request):
    req_form = request.form
    req_base = request.base_url
    response = error_page()
    if _yk_domain in req_base:
        response = submit (req_form)
    elif 'localhost' in req_base:
        response = submit (req_form, True)
    return response
