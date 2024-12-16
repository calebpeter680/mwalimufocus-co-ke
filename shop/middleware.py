from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
import re
import logging

class DomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host == 'mwalimufocus.com':
            return redirect(f'https://mwalimufocus.co.ke{request.path}', permanent=True)
        response = self.get_response(request)
        return response


class RemoveCloudflareScriptMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            content = re.sub(r'<script.*src=["\'][^"\']*cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js.*<\/script>', '', content)
            response.content = content.encode('utf-8')

            logging.debug("Response Content After Script Removal: %s", content)

        return response

