from django.http import HttpResponsePermanentRedirect

class WWWRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.get_host().startswith('www.'):
            new_host = request.get_host().replace('www.', '', 1)
            redirect_url = request.build_absolute_uri().replace(request.get_host(), new_host)
            return HttpResponsePermanentRedirect(redirect_url)
        
        return self.get_response(request)
