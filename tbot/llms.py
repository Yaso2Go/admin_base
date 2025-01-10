import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

import transformers
import torch
import gc
#model_name = "facebook/mbart-large-50"

class tbot_gemma2:
    def __init__(self):
        # Optimization settings
        torch.backends.cudnn.benchmark = True
        os.environ["OMP_NUM_THREADS"] = "24"
        os.environ["MKL_NUM_THREADS"] = "24"
        
        gc.collect()
        torch.cuda.empty_cache()
        
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        os.environ["PYTORCH_PINNED_MEMORY"] = "True"
        os.environ["XFORMERS_VERBOSE"] = "0"

        # Model settings
        self.model_id = "google/gemma-2-9b-it"
        self.max_batch_size = 32
        
        self.quantization_config = transformers.BitsAndBytesConfig(
            load_in_4bit=True,  # Use 4-bit quantization
            bnb_4bit_compute_dtype=torch.float16,  # Compute in FP16
            bnb_4bit_use_double_quant=True,  # Double quantization for efficiency
            bnb_4bit_quant_type="nf4",  # Optimized quantization type
        )

        # Load model and tokenizer with quantization
        self.model = transformers.AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=self.quantization_config,
            device_map="auto",
            trust_remote_code=True,
            offload_folder="./offload",
        )
        
        self.model = self.model.to("cuda")
        self.model.config.use_xformers = True

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_id)
        self.tokenizer.padding_side = "right"
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_response(self, input_text):
        # Pre-tokenize input for faster inference
        input_ids = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=False)
        attention_mask = input_ids.attention_mask.to("cuda")
        
        input_ids = input_ids.input_ids.to("cuda", non_blocking=True)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids.to("cuda"),
                attention_mask=attention_mask,
                max_new_tokens=512,
                temperature=0.5,
                do_sample=True,
                use_cache=True,
                cache_implementation="offloaded",
            )

        # Decode output while skipping special tokens and original prompt
        input_length = input_ids.shape[1]  # Length of the original prompt
        response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True).strip()

        # Further cleanup: remove leading/trailing whitespace, empty lines, and punctuation like dots
        response = response.strip()
        response = response.replace("\n", "").strip()
        return response
    
class tbot_aya23:
    def __init__(self):
        pass
    
    def generate_response(self, input_text):
        import ollama
        from ollama import chat
        from ollama import ChatResponse
        
        model = "aya:8b"
        
        ollama.pull(model)
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        
        return response['message']['content']


class tbot_aya_expanse:
    def __init__(self):
        pass
    
    def generate_response(self, input_text):
        import ollama
        from ollama import chat
        from ollama import ChatResponse

        model = "aya-expanse"
        
        ollama.pull(model)
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        
        return response['message']['content']

class tbot_aya_expanse_32b:
    def __init__(self):
        pass
    
    def generate_response(self, input_text):
        import ollama
        from ollama import chat
        from ollama import ChatResponse

        model = 'aya-expanse:32b'
        
        ollama.pull(model)
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        
        return response['message']['content']
    
class tbot(tbot_aya_expanse):
    pass

class tbot_backup(tbot_aya23):
    pass

class tbot_advanced(tbot_aya_expanse_32b):
    pass


# Target Language: {language_code}
# Text to translate: {text_no_functions}
# Text context OR Position In Page: {context_description}
# """


# Content Promt
# promt = f"""
# You’re a skilled translator with expertise in Arabic and a deep understanding of web design terminology. 
# You specialize in providing precise translations for website content to ensure 
# clarity and cultural relevance. Your task is to translate the sentence/paragraph "{sentence}" into Arabic. 
# Keep in mind that you may translate the phrase into more characters or words than it originally contains to better match the context. 
# Output only the translated phrase in Arabic with no special characters or punctuation.
# """


# Sidebar Navigation Label
# promt = """
# You’re a skilled translator with expertise in Arabic and a deep understanding of web design terminology. 
# You specialize in providing precise translations for navigation labels and other user interface elements to 
# ensure clarity and cultural relevance. Your task is to translate the phrase "Contact page" into Arabic. 
# This phrase is the navigation label for the backend sidebar. Keep in mind that you may translate the phrase into 
# more characters or words than it originally contains to better match the context. 
# Output only the translated phrase in Arabic with no special charecters or punctuation.
# """


# Input Field Title
# prompt = f"""
# You are a skilled translator with expertise in {language} and a deep understanding of web design and user interface terminology. 
# Your task is to translate the phrase "{text_no_functions}" into {language}, ensuring that it works effectively as a field title (label) above an input box in a backend user interface.

# Guidelines:
# 1. The field title should clearly describe the input required from the user, making it intuitive and easy to understand for backend users.
# 2. Avoid long, complicated phrases. Keep the translation clear and concise.
# 3. Do not include any unnecessary characters, punctuation, or explanations.
# 4. Ensure that the translation reflects the field's purpose, without altering the intent of the original text.
# 5. Translate the text naturally into {language}, ensuring cultural appropriateness and clarity for backend users.

# The output should only include the translated field title in {language} with no additional formatting or punctuation.
# """



# Accordition Title Backend
# prompt = f"""
# You are an experienced translator with expertise in {language} and a deep understanding of web design and user interface terminology. 
# Your task is to translate the phrase "{text_no_functions}" into {language}, ensuring that it remains suitable for use as an accordion section title in a backend user interface. 

# Guidelines:
# 1. The accordion title should be concise, clear, and representative of the section it refers to, allowing users to easily understand what content is under that section when expanded.
# 2. Do not include any unnecessary characters, punctuation, or explanations.
# 3. Ensure the translation remains simple and direct, as it will appear as a clickable title in the backend UI.
# 4. Translate the text naturally into {language} while keeping it culturally relevant and user-friendly for backend users.

# The output should only include the translated accordion title in {language} with no additional formatting or punctuation.
# """


# import time

# start1 = time.time()
# bot = tbot_testing()
# end1 = time.time()

# avg_time = []

# # for i in range(20):
# text_no_functions = "Lorem Ipsumsss and this too"
# language = "Arabic"

# # Field
# promt = f"""
# You’re a skilled translator with expertise in Arabic and a deep understanding of web design terminology. 
# You specialize in providing precise translations for website content to ensure 
# clarity and cultural relevance. Your task is to translate the sentence/paragraph "{text_no_functions}" into Arabic. 
# Keep in mind that you may translate the phrase into more characters or words than it originally contains to better match the context. 
# Output only the translated phrase in Arabic with no special characters or punctuation.
# """
# start2 = time.time()
# resp = bot.generate_response(promt)
# print(f"Response: {resp}")
# end2 = time.time() 

# # time_taken = round(end2-start2, 2)

# # avg_time.append(time_taken)

# # print(f"Avg time: {sum(avg_time)/len(avg_time)}")

# print(f"Model Initiation: {round(end1-start1, 2)}")
# print(f"Response Generation: {round(end2-start2, 2)}")