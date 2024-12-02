# import ollama

# def tbot(prompt):
#     """
#     Tokens United Helpful Bot
#     """
#     # Construct the full prompt
    
#     try:
#         #ollama.pull('llama3.2')
#         text = ollama.generate(model='prakasharyan/qwen-arabic', prompt=prompt)
#         return text.response
    
#     except Exception as e:
#         print(f"Error using Ollama library: {e}")
#         return ""

# Sample usage

word = "Home"
context = "This word is used on a website navigation menu."

input_text = f"Translate '{word}' to Arabic in the context: {context}."

#print(tbot(input_text))

#print(f"Translated Text: {translated_text}")

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "bigscience/bloomz-7b1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# model_name = "facebook/mbart-large-50-many-to-many-mmt"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Contextual translation function
# def bloom_translate_with_context(text, context):
#     prompt = f"Translate '{text}' into Arabic. Context: {context}"
#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(**inputs, max_length=50)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

# # Example usage
# text = "Home"
# context = "Navigation label on a website"
# translation = bloom_translate_with_context(text, context)
# print(translation)  # Should output: الرئسية

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/Llama-2-7b-chat-hf"  # Change to your downloaded model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

context = "Translate the word 'Home' to Arabic, considering it's used as a navigation button on a website."
input_ids = tokenizer.encode(context, return_tensors="pt")
outputs = model.generate(input_ids, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))


