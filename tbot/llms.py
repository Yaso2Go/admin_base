import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

import transformers
import torch
import gc
import ollama
from ollama import chat
from ollama import ChatResponse
import time

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
        self.model = "aya:8b"
        pass
    
    def generate_response(self, input_text):
        
        ollama.pull(self.model)
        response: ChatResponse = chat(model=self.model, messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        
        return response['message']['content']


class tbot_aya_expanse:
    def __init__(self):
        self.model = "aya-expanse"
        pass
    
    def generate_response(self, input_text):
        
        ollama.pull(self.model)
        response: ChatResponse = chat(model=self.model, messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        
        return response['message']['content']

class tbot_aya_expanse_32b:
    def __init__(self):
        self.model = "aya-expanse:32b"
        pass
    
    def generate_response(self, input_text):
        
        ollama.pull(self.model)
        response: ChatResponse = chat(model=self.model, messages=[
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


# start1 = time.time()
# bot = tbot_advanced()
# print(bot.model)
# end1 = time.time()

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






# Test function to calculate average response time
# def test_models(models, prompt, iterations=20):
#     results = {}
#     for bot_class in models:
#         bot = bot_class()  # Initialize the bot
#         print(f"Testing {bot.model}...")
        
#         response_times = []
#         for _ in range(iterations):
#             start = time.time()
#             bot.generate_response(prompt)  # Call the function
#             end = time.time()
#             response_times.append(end - start)
        
#         # Calculate average time for this model
#         avg_time = sum(response_times) / iterations
#         results[bot.model] = avg_time

#         print(f"Average response time for {bot.model}: {round(avg_time, 4)} seconds\n")
    
#     return results

# # Define the models and the prompt
# models = [tbot, tbot_backup, tbot_advanced]

# text_no_functions = "Lorem Ipsumsss and this too"
# prompt = f"""
# You’re a skilled translator with expertise in Arabic and a deep understanding of web design terminology. 
# You specialize in providing precise translations for website content to ensure 
# clarity and cultural relevance. Your task is to translate the sentence/paragraph "{text_no_functions}" into Arabic. 
# Keep in mind that you may translate the phrase into more characters or words than it originally contains to better match the context. 
# Output only the translated phrase in Arabic with no special characters or punctuation.
# """

# # Run the test and display results
# results = test_models(models, prompt)

# # Compare the models
# print("Comparison of Models:")
# for model, avg_time in results.items():
#     print(f"{model}: {round(avg_time, 4)} seconds")

# # Calculate "Times" metrics
# sorted_results = sorted(results.items(), key=lambda x: x[1])  # Sort models by response time (ascending)
# fastest_model = sorted_results[0][0]  # Fastest model's name
# fastest_time = sorted_results[0][1]  # Fastest model's response time

# times_metrics = []
# for model, avg_time in sorted_results:
#     times_metric = avg_time / fastest_time
#     times_metrics.append((model, round(times_metric, 2)))

# # Print "Times" metrics
# print("\nTimes Metrics (relative to the fastest model):")
# for model, times_metric in times_metrics:
#     print(f"{model}: {times_metric}x slower than {fastest_model}")

# # Example comparison output
# print("\nDetailed Model Comparisons:")
# for i in range(len(sorted_results)):
#     for j in range(i + 1, len(sorted_results)):
#         model1, time1 = sorted_results[i]
#         model2, time2 = sorted_results[j]
#         relative_speed = round(time2 / time1, 2)
#         print(f"{model2} is {relative_speed}x slower than {model1}")