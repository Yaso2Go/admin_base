import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = 'Collect only modified static files for a specified app'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='The name of the app to collect static files from')

    def handle(self, *args, **kwargs):
        app_name = kwargs['app_name']
        
        # Get the app config using the app name
        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f'App "{app_name}" not found.'))
            return

        # Construct the paths for the static and collected static directories
        static_dir = os.path.join(app_config.path, 'static')
        collected_static_dir = os.path.join(settings.BASE_DIR, 'production_static')

        for root, _, files in os.walk(static_dir):
            for file in files:
                static_file_path = os.path.join(root, file)
                # Get the destination path in collected_static
                relative_path = os.path.relpath(static_file_path, static_dir)
                collected_file_path = os.path.join(collected_static_dir, relative_path)

                # Check if the file needs to be copied (modified or new)
                if not os.path.exists(collected_file_path) or \
                   os.path.getmtime(static_file_path) > os.path.getmtime(collected_file_path):
                    os.makedirs(os.path.dirname(collected_file_path), exist_ok=True)
                    shutil.copy2(static_file_path, collected_file_path)
                    self.stdout.write(f"Copied {file} to collected_static from {app_name}.")