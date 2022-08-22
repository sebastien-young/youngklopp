import functions_framework

_yk_domain = 'youngklopp'

@functions_framework.http
def guest (request):
    req_form = request.form
    if req_form is None:
        print (req_form)
        return 'Error'
    req_base = request.base_url
    if _yk_domain in req_base:
        return 'Hosted'
    elif 'localhost' in req_base:
        return 'Local'
    req_data = request.get_data()
    return req_base
