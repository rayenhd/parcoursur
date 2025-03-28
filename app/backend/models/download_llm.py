from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "tiiuae/falcon-7b-instruct"
save_path = "backend/models/generated_models/falcon-7b-instruct"

# Télécharger le modèle et le tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Sauvegarder en local
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print("✅ Modèle téléchargé et sauvegardé dans :", save_path)
