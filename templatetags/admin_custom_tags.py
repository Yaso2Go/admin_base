from django import template
import os
from django.conf import settings

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