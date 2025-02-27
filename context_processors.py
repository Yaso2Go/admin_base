from django.conf import settings
import re
import os
from django.utils.translation import get_language
#sfrom .functions import filter_list_by_language

def check_apps():
    
    apps = []
    
    if 'cms' in settings.INSTALLED_APPS:
        apps.append("cms")
        
    if 'seo' in settings.INSTALLED_APPS:
        apps.append("seo")
        
    return apps
    
def cms_context_procces():
    # Initialize the list of names to return in the context
    cms_files = []

    # Check if 'cms' is in INSTALLED_APPS
    if 'cms' not in settings.INSTALLED_APPS:
        return {'cms_files': cms_files}  # Return an empty list if 'cms' is not installed

    # Define the directory where the files are stored
    cms_content_index_dir = os.path.join(settings.CONTENT_INDEX_PATH, get_language())

    # Check if the directory exists
    if not os.path.exists(cms_content_index_dir):
        return {'cms_files': cms_files}

    # Regular expression to match files like {{name}}_content_index.json
    name_pattern = re.compile(r'^(?P<name>.+)_content_index\.json$')

    # List all files in the directory and extract names
    for file in os.listdir(cms_content_index_dir):
        match = name_pattern.match(file)
        if match:
            # Extract the name part from the filename
            cms_files.append(match.group('name'))
            
    return {'cms_files': cms_files}

def base_context(request):
    return {
        "apps": check_apps(),
        "cms": cms_context_procces(),
        "defualt_language": settings.LANGUAGE_CODE
    }