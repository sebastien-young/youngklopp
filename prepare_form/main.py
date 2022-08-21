import functions_framework

@functions_framework.http
def guest(request):
    return 'OK'
