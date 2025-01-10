import os
from pathlib import Path
import subprocess
from termcolor import colored
from django.core.management.base import BaseCommand
from admin_base.functions import SpinnerWithMessage

class Command(BaseCommand):
    help = "Initialize development environment"

    def handle(self, *args, **kwargs):
        # Set base directory to the parent folder of admin_base
        current_file_path = Path(__file__)

        # Find the base directory (website)
        base_dir = current_file_path.parents[3]

        print("Base directory:", base_dir)

        try:
            spinner = SpinnerWithMessage("Updating and initializing submodules")
            spinner.start()
            # Update and initialize submodules
            subprocess.run(["git", "submodule", "update", "--init", "--recursive"], check=True, cwd=base_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spinner.stop("Submodules updated and initialized", status="success")

            # Loop through each submodule and checkout main branch
            gitmodules_path = os.path.join(base_dir, ".gitmodules")
            if os.path.exists(gitmodules_path):
                with open(gitmodules_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip().startswith("path ="):
                            submodule_path = line.split("=")[1].strip()
                            submodule_full_path = os.path.join(base_dir, submodule_path)
                            spinner = SpinnerWithMessage(f"Checking out main branch in submodule: {submodule_path}")
                            spinner.start()
                            subprocess.run(["git", "checkout", "main"], check=True, cwd=submodule_full_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            spinner.stop(f"Checked out main branch in {submodule_path}", status="success")
            else:
                print(colored("No submodules found", "yellow"))
        except subprocess.CalledProcessError as e:
            print(colored(f"An error occurred: {e}", "red"))