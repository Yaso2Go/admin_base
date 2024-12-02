import os
import subprocess
from django.core.management.base import BaseCommand
from googletrans import Translator
from django.conf import settings
import json
import importlib.util
import os
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCALE_PATH = os.path.join(BASE_DIR, "locale")  # Adjust as needed

class Command(BaseCommand):
    help = "Extracts translation strings, auto-translates, and compiles them."

    def add_arguments(self, parser):
        parser.add_argument(
            "-l", "--language", type=str, help="Specify the language code for translations (e.g., 'ar').", required=True
        )

    def handle(self, *args, **options):
        language = options["language"]
        # Admin Base Translation
        # Add language to settings and config it
        # self.ensure_locale_path() #Insure "locale" folder exists
        # self.makemessages(language) # Extract static text that needs translation
        # self.auto_translate(language) #Translates .po file with desired language
        # self.compilemessages() # Transforms .po into .mo
        
        # Apps Translation
        #self.add_language_to_choices(language) # Adds language to language_selection.html
        
        self.apps_translating(language)
        #self.stdout.write(self.style.SUCCESS(f"Translations for '{language}' completed!"))

    def ensure_locale_path(self):
        """Ensure the locale directory exists."""
        if not os.path.exists(LOCALE_PATH):
            os.makedirs(LOCALE_PATH)
        self.stdout.write(f"Locale directory ensured at: {LOCALE_PATH}")

    def makemessages(self, language):
        """Extract translation strings for the specified language."""
        self.stdout.write(f"Extracting translations for: {language}")
        
        try:
            subprocess.run(
                ["python", "manage.py", "makemessages", "-l", language],
                cwd=settings.BASE_DIR
            )
            self.stdout.write(f"Translation strings extracted for: {language}")
        except subprocess.CalledProcessError as e:
            self.stderr.write(f"Error extracting translations for '{language}': {e}, working dir at {settings.BASE_DIR}")

    def auto_translate(self, language):
        """Auto-translate the extracted .po file using Google Translate."""
        translator = Translator()
        po_file_path = os.path.join(LOCALE_PATH, language, "LC_MESSAGES", "django.po")

        if not os.path.exists(po_file_path):
            self.stderr.write(f"No .po file found for '{language}'. Skipping auto-translation.")
            return

        self.stdout.write(f"Auto-translating {po_file_path}...")

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
                    translation = translator.translate(original_text, dest=language).text
                    print(translation)
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

        self.stdout.write(f"Auto-translation completed for: {po_file_path}")

    def compilemessages(self):
        """Compile all translation files."""
        self.stdout.write("Compiling translation files...")
        try:
            subprocess.run(
                ["python", "manage.py", "compilemessages"], 
                cwd=settings.BASE_DIR
            )
            self.stdout.write("Compilation complete.")
        except subprocess.CalledProcessError as e:
            self.stderr.write(f"Error compiling messages: {e}")
            
    def add_language_to_choices(self, code):
        # Get the absolute path of the JSON and HTML files
        
        json_path = settings.BASE_DIR + "/admin_base/locale/languages.json"
        html_path = settings.BASE_DIR + "/admin_base/templates/base/components/language_selection.html"

        # Load the JSON file containing language data
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                languages_data = json.load(file)
        except FileNotFoundError:
            print(f"Error: The JSON file was not found.")
            print(json_path)
            return

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
            print(f"Error: The HTML file was not found.")
            return

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
            if_marker = "{% if request.LANGUAGE_CODE == 'en' %}"
            else_marker = "{% else %}"

            if if_marker in html_content and else_marker in html_content:
                html_content = html_content.replace(
                    else_marker, f"{button_elif_code}{else_marker}"
                )

        # Write the updated HTML content back to the file
        try:
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            self.stdout.write(f"Translation strings extracted for: {code}")
        except Exception as e:
            print(f"Error writing to the HTML file: {e}")
            
    def apps_translating(self, language):

        # Fetch all local apps
        project_base_dir = settings.BASE_DIR

        # Fetch all local apps in the same directory as the project's base folder
        for app_config in apps.get_app_configs():
            app_path = app_config.path
            if app_path.startswith(project_base_dir):  # Check if the app is in the project's base directory
                translate_file = os.path.join(app_path, "translate.py")

                # Check if Translate.py exists in the app
                if os.path.exists(translate_file):
                    self.stdout.write(f"Found Translate.py in app: {app_config.name}")

                    try:
                        # Dynamically import the translate_app function
                        module_name = f"{app_config.name}.translate"
                        translate_module = importlib.import_module(module_name)
                        translate_func = getattr(translate_module, "translate_app", None)

                        # Check if the translate_app function exists and is callable
                        if callable(translate_func):
                            self.stdout.write(f"Running translate_app for app: {app_config.name}")
                            translate_func(language)  # Call the function with the provided argument
                        else:
                            self.stderr.write(
                                f"'translate_app' function not found or not callable in {app_config.name}.Translate"
                            )
                            
                    except ModuleNotFoundError:
                        self.stderr.write(f"Module {module_name} not found.")
                        
                    except Exception as e:
                        self.stderr.write(
                            f"Error while executing translate_app in {app_config.name}: {e}"
                        )
                        
                else:
                    self.stdout.write(f"No Translate.py found in {app_config.name}")
