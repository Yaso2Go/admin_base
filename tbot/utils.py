import re
import time
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from deep_translator import GoogleTranslator
import logging
import os

# Reletive importing for local running
try:
    from llms import tbot, tbot_backup, tbot_advanced, tbot_gemma2
    import prompts as prompt

# Local importing for CLI running
except:
    from admin_base.tbot.llms import tbot, tbot_backup, tbot_advanced
    import admin_base.tbot.prompts as prompt
    from django.conf import settings

def translation_logger():
    # Define the log file path
    
    log_file = os.path.join(settings.BASE_DIR, 'log', f"translation_18-1-2025.log")
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Set up the logging configuration
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # You can use DEBUG, WARNING, ERROR, etc., as needed
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w',  # Open in write mode to overwrite the file each time
        encoding='utf-8' 
    )

def translate_text_api(text, dest_language):
    return GoogleTranslator(source='auto', target=dest_language).translate(text)

def format_text(text):
    """
    Formats the input text by applying various cleaning and normalization steps.

    Args:
        text (str): The input text to format.

    Returns:
        str: The formatted and cleaned text.
    """
    # Remove leading and trailing whitespace
    formatted_text = text.strip()
    
    # Remove unnecessary special characters (keep basic punctuation and Arabic letters)
    formatted_text = re.sub(r"[^\w\s.,!?()،ء-ي]+", "", formatted_text)
    
    # Remove all double and single quotes
    formatted_text = formatted_text.replace('"', "").replace("'", "")
    
    # Normalize multiple spaces and newlines
    formatted_text = re.sub(r"\s+", " ", formatted_text)
    
    # Ensure the text does not start with a period or unwanted characters
    if formatted_text.startswith("."):
        formatted_text = formatted_text[1:].strip()
    
    # Ensure the first letter is capitalized (if the text is not empty)
    if formatted_text:
        formatted_text = formatted_text[0].capitalize() + formatted_text[1:]
    
    # Additional formatting: Remove excess whitespace around punctuation
    formatted_text = re.sub(r"\s+([.,!?])", r"\1", formatted_text)
    formatted_text = re.sub(r"([.,!?])\s+", r"\1 ", formatted_text)

    return formatted_text

def detect_language(text):
    """
    Detects the language of the input text based on Unicode character ranges and langdetect.
    """
    
    # Ensure consistent results from langdetect
    DetectorFactory.seed = 0

    # Define Unicode ranges for supported languages
    language_ranges = {
        "ar": r"[\u0600-\u06FF]",  # Arabic
        "en": r"[a-zA-Z]",         # English
        # Add other languages as needed
    }

    # Extract alphabetic characters from text
    def extract_alphabetic_words(text):
        return re.findall(r"[^\W\d_]+", text)  # Matches only words, excluding numbers and symbols

    # Detect the language of the input text
    detected_languages = set()

    # Process each word in the text
    for word in extract_alphabetic_words(text):
        detected = None

        # Check against supported language patterns
        for lang_code, lang_pattern in language_ranges.items():
            if re.fullmatch(lang_pattern + "+", word):  # If the word matches the pattern for a language
                detected = lang_code
                break
        
        # Use langdetect as a fallback if no pattern matches
        if not detected:
            try:
                detected = detect(word)
                if detected not in language_ranges:
                    detected = "not_supported"  # Mark unsupported languages
            except LangDetectException:
                detected = "not_supported"
        
        # Add the detected language to the set
        detected_languages.add(detected)

    try:
        # Determine the result based on detected languages
        if len(detected_languages) > 1:
            if all(lang in language_ranges for lang in detected_languages):
                return "mixed"  # Multiple supported languages detected
            else:
                return "not_supported"  # Contains unsupported language(s)
        else:
            return detected_languages.pop()  # Return the single detected language
        
    except:
        #print("An Error occured while detecting language. Most likely an empty string has been passed to the function")
        return "not_supported"

def str_translation_check(original_translated_text, original_text, language_code, bots, database_query=False, advanced=False):
    """
    Checks the validity of a translated text against the original text and ensures it is in the target language.
    
    Args:
        original_translated_text (str): The text that has been translated.
        original_text (str): The original text before translation.
        language_code (str): The target language code (e.g., 'ar' for Arabic).
        llm_model (object): The primary language model used for generating responses.
        backup_llm_model (object): The backup language model used for generating responses if needed.
        
    The function performs the following checks and actions:
    1. Checks if the translated text is empty.
    2. Detects the language of the translated text using `detect_language`.
    3. If the detected language matches the target language, it proceeds without changes.
    4. If the detected language is "mixed", it checks if the translated text contains the translation of the original text:
        - If it does, it extracts the translated text using `llm_model.generate_response`.
        - If it does not, it re-generates the translation using `backup_llm_model.generate_response`.
    5. If the detected language is unsupported or different from the target language, it re-generates the translation using `backup_llm_model.generate_response`.
    The function also logs various steps and errors encountered during the process.
    """
    
    if not advanced:
        llm_model, backup_llm_model = bots[0], bots[1]
        
        
    else:
        llm_model = bots[2]
        backup_llm_model = bots[2]
    
    # print("\n\nSTARTING\n\n")
    # print(f'Original Translated: {original_translated_te xt}')
    # print(f'Original Text: {original_text}')
    language = "Arabic"
    
    # Format original input
    text = format_text(original_translated_text)
    
    errors = []
    
    # 1. Check if string is empty
    if text == "":
        errors.append("Field is empty.")

    # 2. Translated text Check
    try:
        # Language Check
        detected_language = detect_language(text)
        
        # Detected language is the same as the target language, continue
        if detected_language == language_code:
            
            # Maybe result is the same as target language, but is it the right translation?
            right_transaltion = prompt.is_right_translation.format(translated_str=text, original_str=original_text)
            
            right_transaltion = backup_llm_model.generate_response(right_transaltion)
            
            if right_transaltion == "True":
                pass
            
            else:
                if database_query == True:
                    translate_text_prompt = prompt.db_content.format(target_language=language, original_str=original_text)
                    
                else:
                    translate_text_prompt = prompt.nav_label.format(target_language=language, original_str=original_text)
                
                new_translated_text = backup_llm_model.generate_response(translate_text_prompt)
                
                text = new_translated_text
                
                errors.append("Translated text not right")
                
        
        # Detected langaues in string is "mixed".
        # Scenario 1: Translation inside the string, extract
        # Scenario 2: Translation not in string, re-generate
        elif detected_language == "mixed":
            # Check if string contasins the translted text of the original text
            #print("\nDetecting Text\n")
            
            translation_present_promtpt = prompt.is_translation_present.format(translated_str=text, original_str=original_text)
            
            translation_present = backup_llm_model.generate_response(translation_present_promtpt)
            
            # Check if string Contains Translation
            if translation_present == "True":
                #print("\nExtracting Text\n")
                
                extract_text_prompt = f"Extract only the Arabic text from this string \"{text}\""
                
                extracted_text = llm_model.generate_response(extract_text_prompt)
                #print(extracted_text)
                
                text = extracted_text
                
                errors.append("Text extracted from string")

            # String dosent contain translation. Translate original text using Aya23
            else:   
                #print("\nText not present translating\n")
                
                if database_query == True:
                    translate_text_prompt = prompt.db_content.format(target_language=language, original_str=original_text)
                    
                else:
                    translate_text_prompt = prompt.nav_label.format(target_language=language, original_str=original_text)
                
                new_translated_text = backup_llm_model.generate_response(translate_text_prompt)
                
                text = new_translated_text
                
                errors.append("Text translated again")
        
        # Translated text is either unsupported or in another language than target language
        else:
            #print("\nText not present translating\n")
            language = "Arabic"
            
            if database_query == True:
                    translate_text_prompt = prompt.db_content.format(target_language=language, original_str=original_text)
                    
            else:
                translate_text_prompt = prompt.nav_label.format(target_language=language, original_str=original_text)
                    
            new_translated_text = backup_llm_model.generate_response(translate_text_prompt)
            #print(new_translated_text)
            
            text = new_translated_text
            
            errors.append("Text Translated Agaian")
            
            
    except LangDetectException as e:
        errors.append(f"Language detection error: {e}")
    
    if errors:
        # print("ACHIVED FALSE STATUS") 
        # print("String had didnt go through the translation check, Please Check it")
        # print("Errors Raised:")
        
        # for i in errors:
        #     print(i)
            
        return False, text
            
    else:
        #print("Achived true status")
        return True, text



def translation_check(original_translated_text, original_text, language_code, bots, database_query=False):
    """
    This function refines a translated string repeatedly by passing it through
    the str_translation_check function until the translation meets the criteria (status is True).
    """
    translation_logger()
    # Trigger for advanced bot
    advanced = False
    
    # Initialize the variables
    text = original_translated_text
    trials = 0
    
    logging.info(f"Starting translation for string \"{original_text}\"")

    while True:  # Infinite loop that will break when the status is True
        # Pass the current text through the str_translation_check function
        s1 = time.time()
        # Level 1 check
        str_pass, refined_text = str_translation_check(text, original_text, language_code, bots, database_query, advanced)
        e1 = time.time()
        # Level 2 check
        # If the status is True, return the final refined text
        if str_pass:
            logging.info(f"Succesfully translated string \"{original_text}\" to \"{refined_text}\" in {round((e1-s1), 2)} seconds")
            return str_pass, refined_text
        
        else:
            # If it reached here while advanced is true that means that the model couldnt give us the best result.
            if advanced == True:
                logging.info(f"Maximum trials reached. Result is string \"{original_text}\" translated to \"{refined_text}\"")
                return True, refined_text
            # If status is False, refine the text further
            trials += 1
            logging.info(f"Attempt {trials}, Original: {original_text}, Variation: {refined_text} in {round((e1-s1), 2)} seconds")
            
            # Pass in new (refined) text variable
            text = refined_text
            
            # Optional: Safeguard against infinite loops
            if trials > 6:
                advanced = True
  
# original_translated_text = """منطقة النص الساقطة"""
# original_text = "Text Area DropDown"
# language_code = 'ar'
# bots = tbot(), tbot_backup(), tbot_advanced()

# print(translation_check(original_translated_text, original_text, language_code, bots))

