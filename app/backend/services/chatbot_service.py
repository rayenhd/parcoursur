import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "backend/models/generated_models/chatbot_transformer_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

def generate_response(question):
    input_ids = tokenizer.encode(question, return_tensors="pt")
    output = model.generate(input_ids, max_length=150)
    return tokenizer.decode(output[0], skip_special_tokens=True)
