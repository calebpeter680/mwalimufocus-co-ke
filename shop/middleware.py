from django.shortcuts import redirect

class DomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host == 'mwalimufocus.com':
            return redirect(f'https://mwalimufocus.co.ke{request.path}', permanent=True)
        response = self.get_response(request)
        return response
