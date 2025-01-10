from django import template
import os
from django.conf import settings
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag
def pfp_exist(file_path):
    """
    Checks if the Profile Picture exists and returns True or False.

    :param file_path: The path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    absolute_path = os.path.join(settings.BASE_DIR, "admin_base", file_path)
    return os.path.exists(absolute_path)

@register.simple_tag
def favicon_exist(filepath):
    """
    Checks if a file exists in the media or static directories.
    """
    media_path = os.path.join(settings.MEDIA_ROOT, filepath)
    static_path = os.path.join(settings.STATIC_ROOT, filepath)

    return os.path.exists(media_path) or os.path.exists(static_path)

@register.simple_tag
def message_translated(message_id):
    """
    Retrieves the translation for the given message ID from the .po file.
    """
    language = get_language()
    po_file_path = os.path.join(settings.BASE_DIR, 'admin_base', 'locale', language, 'LC_MESSAGES', 'django.po')
    
    if not os.path.exists(po_file_path):
        return message_id  # Return the original message if the .po file does not exist

    with open(po_file_path, 'r', encoding='utf-8') as po_file:
        lines = po_file.readlines()
    
    found_msgid = False
    for line in lines:
        
        if found_msgid:
            if line.startswith('msgstr'):
                return line.split('"', 1)[1].rsplit('"', 1)[0]
        if line.strip() == f'msgid "{message_id}"':
            found_msgid = True
         
    return message_id