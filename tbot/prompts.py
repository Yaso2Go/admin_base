is_translation_present = """
Does this string "{translated_str}" contain the Arabic translation for the string "{original_str}". 
If yes only reply with True, if no only reply with False. Only reply with True if you are 60% or more sure that 
its the right transaltion. Do not reply with anything except "True" or "False"
"""

is_right_translation = """
Is the string "{translated_str}" the Arabic translation for the string "{original_str}". 
If yes only reply with True, if no only reply with False. Only reply with True if you are 50% or more sure that 
its the right transaltion. Do not reply with anything except "True" or "False"
"""

# Database Content Promt
db_content = """
You are an experienced translator with expertise in {target_language} and a deep understanding of web design, user interface terminology, and website content localization.
Your task is to translate the following text into {target_language}, ensuring that it remains clear, culturally relevant, and user-friendly for a website audience.

Guidelines:
1. The translated text should be concise, clear, and representative of the original content, allowing users to easily understand the information.
2. Do not include any unnecessary characters, punctuation, or explanations.
3. Ensure the translation remains simple and direct, as it will appear as part of the website content.
4. Translate the text naturally into {target_language} while keeping it culturally relevant and user-friendly for website visitors.

Original Text:
"{original_str}"

The output should only include the translated text in {target_language} with no additional formatting or punctuation.
"""
             
# Content index Accoridition Title Promt  
nav_label = """
You are an experienced translator with expertise in {target_language} and a deep understanding of web design and user interface terminology. 
Your task is to translate the phrase "{original_str}" into {target_language}, ensuring that it remains suitable for use as an accordion section title in a backend user interface. 

Guidelines:
1. The accordion title should be concise, clear, and representative of the section it refers to, allowing users to easily understand what content is under that section when expanded.
2. Do not include any unnecessary characters, punctuation, or explanations.
3. Ensure the translation remains simple and direct, as it will appear as a clickable title in the backend UI.
4. Translate the text naturally into {target_language} while keeping it culturally relevant and user-friendly for backend users.

The output should only include the translated accordion title in {target_language} with no additional formatting or punctuation.
"""