import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Delete all __pycache__ directories and clear the cache folder in the project."

    def handle(self, *args, **kwargs):
        base_dir = os.getcwd()  # Start from the current working directory
        pycache_count = 0
        cache_folder = os.path.join(base_dir, "cache")

        # Step 1: Remove all __pycache__ folders
        for root, dirs, files in os.walk(base_dir):
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)  # Delete the __pycache__ directory
                        pycache_count += 1
                        self.stdout.write(f"Deleted: {pycache_path}")
                    except Exception as e:
                        self.stderr.write(f"Failed to delete {pycache_path}: {e}")

        # Step 2: Clear the cache folder if it exists
        if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
            try:
                for filename in os.listdir(cache_folder):
                    file_path = os.path.join(cache_folder, filename)
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                self.stdout.write(f"Cleared all contents of the cache folder: {cache_folder}")
            except Exception as e:
                self.stderr.write(f"Failed to clear the cache folder: {e}")
        else:
            self.stdout.write("Cache folder not found.")

        # Final summary message
        if pycache_count == 0:
            self.stdout.write("No __pycache__ directories found.")
        else:
            self.stdout.write(f"Deleted {pycache_count} __pycache__ directories.")