from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import translation
from django.conf import settings
from urllib.parse import urlparse
import re
from django.urls import clear_url_caches

def home(request):  
    return render(request, 'home_admin.html')

def change_language(request: HttpRequest):
    if request.method == 'POST':
        lang = request.POST.get('language')

        # Check if the selected language is valid
        if lang in dict(settings.LANGUAGES).keys():
            translation.activate(lang)
            request.session['preferred_language'] = lang

            referer_url = request.META.get('HTTP_REFERER', '/')
            
            if lang == settings.DEFAULT_LANGUAGE:
                # Remove any language code from the URL if it's the default language
                new_url = re.sub(
                    r'(/admin/)([a-z]{2}/)?',
                    r'\1',
                    referer_url
                )
            else:
                # Add the selected language code if it's not the default language
                new_url = re.sub(
                    r'(/admin/)([a-z]{2}/)?',
                    rf'\1{lang}/',
                    referer_url
                )

            response = redirect(new_url)

            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
            return response

    return redirect('/')