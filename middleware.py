import sqlite3
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from urllib.parse import urljoin
from django.urls import resolve
from django.core.management import call_command
from django.http import StreamingHttpResponse
from django.utils.cache import patch_cache_control
from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)
class CacheUpdateMiddleware(MiddlewareMixin):
    def __call__(self, request):
        # Only cache GET requests
        if request.method != 'GET':
            print("Method not get")
            return self.get_response(request)


        print("Method Get")
        # If not in cache or cache needs update, get new response
        print("")
        cache_status, version_key, version_value = self.reset_cache_check()
        print("")
            
        if cache_status:
            # Clear cache if version mismatch
            call_command("clear_cache")
            cache.set("latest_cache_index", version_value)
            
            print("RESETED SERVER_SIDE CACHE")
            
            if 'cache_reset' not in request.GET:
                print("Cache Reset Not in Header Confirmation")
                redirect_url = request.get_full_path() + ('&' if '?' in request.get_full_path() else '?') + 'cache_reset=true'
                return HttpResponseRedirect(redirect_url)
        
        response = self.get_response(request)
        
        if request.GET.get('cache_reset') == 'true':
            print("Applying Cache Busting Headers")
            patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
            
        return response

    def reset_cache_check(self):
        """
        Checks if the cache version stored in the database is different from the cache version
        stored in the user's session. If different, the cache is considered outdated and needs
        to be updated.
        """
        try:
            conn = sqlite3.connect('admin_base/general.db')
            cursor = conn.cursor()

            # Fetch the current content_update_index from the database
            cursor.execute('SELECT content_update_index FROM update_index')
            cache_version = cursor.fetchone()[0]
            conn.close()

            # Check if the user has cached data and a cache_index stored
            cache_key = f"latest_cache_index"
            session_cache_version = cache.get(cache_key)
            
            print(f"Current cache version: {session_cache_version}")
            print(f"Database version: {cache_version}")

            if session_cache_version is None or session_cache_version != cache_version:
                print("Cache version mismatch - triggering reset")
                return True, "latest_cache_index", cache_version
            
            else:
                print("Cache version match - no reset needed")
                return False, '', ''

        except Exception as e:
            print(f"Error checking cache version: {str(e)}")
            return False, '', ''
    
class TrailingSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"Processing request: {request.path}")
        # Check if the path does not end with a slash and is not a file
        if not request.path.endswith('/') and not request.path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico')):
            print(f"Trying")
            try:
                # Redirect to the same URL with a trailing slash
                print(f"Redirect: {request.path + '/'}")
                return HttpResponsePermanentRedirect(request.path + '/')
            except Exception:
                # If the URL does not resolve to a view, let the request proceed
                pass
        return None
    
from django.utils import translation
from django.conf import settings
import re
from django.shortcuts import redirect

class URLLanguageConfigMiddleware:
    """
    Middleware to handle language switching based on the URL structure.
    Only triggers if the user manually changes the language code in the URL.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        if path.startswith("/__reload__/"):
            return self.get_response(request)

        # Check if the path contains a language code
        url_lang_match = re.match(r'^/admin/([a-z]{2})(/.*)?$', path)
    
        current_lang = translation.get_language()
        
        # Non-Default Language Activate
        if url_lang_match:
            
            url_lang_match = url_lang_match.group(1)
            
            print("Not Default")
            print(url_lang_match)
            print(current_lang)

            # URL Language not changed            
            if current_lang == url_lang_match:
                return self.get_response(request)
            
            # URL Language Changed
            else:    
                if url_lang_match in dict(settings.LANGUAGES).keys():
                    print("Here is working")
                    translation.activate(url_lang_match)
                    request.session['preferred_language'] = url_lang_match

                    response = self.get_response(request)
                    
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, url_lang_match)
                    response.set_cookie('X-Reload', 'true')
                    
                    return response
                    
                else:
                    return self.get_response(request)

        
        # Default Language Activated
        else:
            print("Default Activated")
            print(current_lang)
            print(settings.DEFAULT_LANGUAGE)
            
            if current_lang != settings.DEFAULT_LANGUAGE:
                print("Changing")
                translation.activate(settings.DEFAULT_LANGUAGE)
                request.session['preferred_language'] = settings.DEFAULT_LANGUAGE

                response = self.get_response(request)
                
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, settings.DEFAULT_LANGUAGE)
                response.set_cookie('X-Reload', 'true')

                return response
                
            else:   
                return self.get_response(request)



