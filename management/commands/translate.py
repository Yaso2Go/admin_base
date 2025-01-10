import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
import json
import importlib.util
import os
from django.apps import apps
from termcolor import colored
from admin_base.functions import traceback_error, SpinnerWithMessage
import time
from django.contrib.auth.models import User
from admin_base.tbot.utils import translate_text_api
import shutil

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCALE_PATH = os.path.join(BASE_DIR, "locale")  # Adjust as needed

class Command(BaseCommand):
    help = "Extracts translation strings, auto-translates, and compiles them."

    def add_arguments(self, parser):
        parser.add_argument(
            "-l", "--language", type=str, help="Specify the language code for translations (e.g., 'ar').", required=True
        )
        parser.add_argument(
            "remove", nargs='?', default=None, help="Optional argument to remove the specified language from all."
        )

    def handle(self, *args, **options):
        # Define paramaters
        s1 = time.time()
        language = options["language"]
        remove = bool(options["remove"])
        
        # Get language full name from code
        for languages in settings.LANGUAGES:
            code, language_name = languages
            if code == language:
                language_name = language_name
                break
        
        if remove:
            admin_locale_path = os.path.join(settings.BASE_DIR, "admin_base", 'locale', language)
            
            if os.path.exists(admin_locale_path):
                shutil.rmtree(admin_locale_path)  
                
            self.apps_translating(language, remove=True)
            
            print(colored(f'\nSuccesfully removed {language_name} ({language}) language from the website\n', 'green'))
            
            return
        
        print('')   
        print(colored(f"Starting translation for {language_name} ({language})", "white", 'on_magenta', attrs=['bold']))
        print('')

        self.ensure_locale_path() #Insure "locale" folder exists
        if self.translation_present(language):
            print(f"Translation found for {language}")
            
        else:
            while True:
                # Translate Static Labels and Messages defined by Django Translate Library
                print(colored(f"Starting static label translation using ", "light_cyan", attrs=['bold']) + colored("Django's Translation Library\n", 'blue', attrs=['bold']))
                
                spinner = SpinnerWithMessage('Starting translation...')
                spinner.start()
                
                self.makemessages(language, spinner) # Extract static text that needs translation
                self.auto_translate_locale_folders(language, spinner) #Translates .po file with desired language
                self.compilemessages(spinner) # Transforms .po into .mo
                
                #self.add_language_to_choices(language, spinner) # Adds language to language_selection.html
                
                spinner.stop("Finished !\n")
                break
            
        self.apps_translating(language)
        
        print('\n')
        print(colored("Successfully translated website :)", 'white', 'on_light_green', attrs=['bold']))
        
        e1 = time.time()
        
        print(f"Time taken for website transaltion is {round((e1-s1), 2)/60}")

    def ensure_locale_path(self):
        """Ensure the locale directory exists."""
        if not os.path.exists(LOCALE_PATH):
            os.makedirs(LOCALE_PATH)

    def translation_present(self, language):
        """Check if the specified language has already been translated."""
        po_file_path = os.path.join(LOCALE_PATH, language)
        
        if os.path.exists(po_file_path):
            return True
        
        return False
    
    def makemessages(self, language, spinner):
        """Extract translation strings for the specified language."""
        
        spinner.update("Extracting translations from templates... ")
        time.sleep(2)
        try:
            subprocess.run(
                ["python", "manage.py", "makemessages", "-l", language],
                cwd=settings.BASE_DIR,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            # Mark translations for conditional toast
            locale_path = os.path.join(settings.BASE_DIR, "admin_base", 'locale', language, 'LC_MESSAGES', 'django.po')

            # Get the admin user (superuser)
            admin_user = User.objects.filter(is_superuser=True).first()
            admin_name = admin_user.get_full_name() or admin_user.get_username()
            
            with open(locale_path, 'a', encoding='utf-8') as po_file:
                name = f""
                message = f"""#: .\\admin_base\\templates\\base\\base.html:79
msgid "Welcome back, {admin_name.capitalize()}"
msgstr \"\""""
                po_file.write(f'\n{message}\n')
            
        except subprocess.CalledProcessError as e:
            spinner.stop(f"Error extracting translations for '{language}': {e}, working dir at {settings.BASE_DIR}", 'error')
            return False

    def auto_translate_locale_folders(self, language, spinner):
        """Auto-translate the extracted .po file using Google Translate."""
        
        spinner.update(f"Auto-translating .po file...")
        
        BASE_DIR = os.getcwd()  # Your base directory

        locale_dirs = []

        # List all folders in the BASE_DIR
        for item in os.listdir(BASE_DIR):
            
            item_path = os.path.join(BASE_DIR, item)
            
            if os.path.isdir(item_path):  # Check if it's a folder
                
                folder_path = os.path.join(BASE_DIR, item)
                
                for folders in os.listdir(folder_path):
                    if folders == 'locale':
                        locale_dirs.append(item)
                        
        for directory in locale_dirs:
            
            locale_path = os.path.join(os.getcwd(), directory, 'locale', language)
            
            if os.path.exists(locale_path):
                pass
            
            else:
                return
            
            po_file_path = os.path.join(locale_path, "LC_MESSAGES", "django.po")
                
            if not os.path.exists(po_file_path):
                spinner.stop(f"No .po file found for '{language}'. Skipping auto-translation.", 'error')
                return False

            # Read the .po file
            with open(po_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Translate relevant lines
            translated_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.startswith('msgid "'):
                    original_text = line[7:-2]  # Extract text inside quotes
                    if original_text:  # Skip empty strings
                        
                        translation = translate_text_api(original_text, language)
                        translated_lines.append(line)  # Keep msgid
                        # Check if the next line is 'msgstr ""' and remove it
                        if i + 1 < len(lines) and lines[i + 1] == 'msgstr ""\n':
                            i += 1  # Skip the empty msgstr line
                        translated_lines.append(f'msgstr "{translation}"\n')  # Add translation
                    else:
                        translated_lines.append(line)
                else:
                    translated_lines.append(line)
                
                i += 1  # Move to the next line

            # Write the translated lines back to the .po file
            with open(po_file_path, "w", encoding="utf-8") as file:
                file.writelines(translated_lines)

    def compilemessages(self, spinner):
        """Compile all translation files."""
        spinner.update("Compiling translation files...")
        time.sleep(2)
        try:
            subprocess.run(
                ["python", "manage.py", "compilemessages"], 
                cwd=settings.BASE_DIR,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            spinner.stop(f"Error compiling messages: {e}", "error")
            return False
            
    def add_language_to_choices(self, code, spinner):
        # Get the absolute path of the JSON and HTML files
        json_path = settings.BASE_DIR + "/admin_base/locale/languages.json"
        html_path = settings.BASE_DIR + "/admin_base/templates/base/components/language_selection.html"
        
        spinner.update("Addding language to choice selection dropdown...")

        # Load the JSON file containing language data
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                languages_data = json.load(file)
        except FileNotFoundError:
            spinner.stop(f"Error: The JSON file was not found.", 'error')
            return False

        languages = languages_data.get("languages", {})

        # Generate the `elif` blocks and dropdown items for the specified languages
        button_elif_code = ""
        dropdown_items_code = ""

        details = languages.get(code)
        if details:
            # Add the `elif` block for the button
            button_elif_code += (
                f"  {{% elif request.LANGUAGE_CODE == '{code}' %}}\n"
                f"  <span class=\"{details['flag_code']}\"></span> {details['name']}\n"
            )

            # Add the dropdown item for the language
            dropdown_items_code += (
                f"    <li>\n"
                f"        <button class=\"dropdown-item\" type=\"submit\" name=\"language\" value=\"{code}\" "
                f"{{% if request.LANGUAGE_CODE == '{code}' %}}disabled{{% endif %}}>\n"
                f"            <span class=\"{details['flag_code']}\"></span> {details['name']}\n"
                f"        </button>\n"
                f"    </li>\n"
            )

        # Read the existing HTML file
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
        except FileNotFoundError:
            spinner.stop(f"Error: The HTML file was not found.", 'error')
            return False

        # Check if the language is already present in the HTML file
        if f"request.LANGUAGE_CODE == '{code}'" in html_content:
            spinner.stop(f"Language '{code}' is already present in the HTML file.", 'error')
            return False

        # Find the position to insert the elif blocks and dropdown items
        if_marker = "{% if request.LANGUAGE_CODE == 'en' %}"
        else_marker = "{% else %}"
        dropdown_marker = "<ul class=\"dropdown-menu\" aria-labelledby=\"languageDropdown\">"

        # Insert the dropdown items inside the dropdown
        if dropdown_marker in html_content:
            # Locate the position of the dropdown list
            start_index = html_content.find(dropdown_marker) + len(dropdown_marker)
            end_index = html_content.find('</ul>', start_index)

            # Extract the part of the HTML content between the dropdown and the closing </ul>
            existing_dropdown_items = html_content[start_index:end_index]

            # Insert the new languages at the end of the list
            updated_dropdown_content = existing_dropdown_items + "\n" + dropdown_items_code

            # Replace the old dropdown content with the new content
            html_content = html_content[:start_index] + updated_dropdown_content + html_content[end_index:]

        # Now handle the button change for the languages
        if if_marker in html_content and else_marker in html_content:
            html_content = html_content.replace(
                else_marker, f"{button_elif_code}{else_marker}"
            )

        # Write the updated HTML content back to the file
        try:
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
        except Exception as e:
            print()
            spinner.stop(f"Error writing to the HTML file: {e}", 'error')
            return False
            
    def apps_translating(self, language, remove=False):
        
        if not remove:
            print(colored("Starting translation for indvidiual apps\n", "light_cyan", attrs=['bold']))
        
        # Fetch all local apps
        project_base_dir = settings.BASE_DIR

        # Fetch all local apps in the same directory as the project's base folder
        for app_config in apps.get_app_configs():
            app_path = app_config.path
            if app_path.startswith(project_base_dir):  # Check if the app is in the project's base directory
                translate_file = os.path.join(app_path, "translate.py")

                # Check if Translate.py exists in the app
                if os.path.exists(translate_file):

                    try:
                        # Dynamically import the translate_app function
                        module_name = f"{app_config.name}.translate"
                        translate_module = importlib.import_module(module_name)
                        
                        if remove == True:
                            translate_func = getattr(translate_module, "remove", None)
                            
                        else:
                            translate_func = getattr(translate_module, "translate_app", None)

                        # Check if the translate_app function exists and is callable
                        if callable(translate_func):
                            if remove == True:
                                translate_func(language)  # Call remove function for app
                                
                            else:
                            
                                print(colored(f"\nRunning translate.py for app: {app_config.name}\n", "light_green", attrs=['bold']))
                                translate_func(language)  # Call the function with the provided argument
                                print(colored(f"\nEnding translate.py for app: {app_config.name}\n", "light_green", attrs=['bold']))
                        
                        else:
                            self.stderr.write(
                                
                            )
                            print(colored(f"'translate_app' function not found or not callable in {app_config.name}.Translate", 'red'))
                            
                    except ModuleNotFoundError:
                        print(colored(f"Module {module_name} not found.", 'red'))
                        traceback_error()

                        
                    except Exception as e:
                        print(colored(f"\nError while running translate.py in {app_config.name}:", "red"))
                        traceback_error()
                        
                else:
                    if not remove:
                        print(colored(f"No translate.py found in {app_config.name}", "dark_grey"))