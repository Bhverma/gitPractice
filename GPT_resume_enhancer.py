from huggingface_hub import snapshot_download
from pathlib import Path

mistral_models_path = Path.home().joinpath('mistral_models', '7B-Instruct-v0.3')
mistral_models_path.mkdir(parents=True, exist_ok=True)
print(f"Downloading Mistral 7B-Instruct-v0.3 models to {mistral_models_path}...")
# snapshot_download(repo_id="mistralai/Mistral-7B-Instruct-v0.3", allow_patterns=["params.json", "consolidated.safetensors", "tokenizer.model.v3"], local_dir=mistral_models_path)
##################################################My name is Bharat"##########################################################




###########################3Third Edit Completed##############################################
print("Download completed.")



# Now you can load the model from mistral_models_path using your preferred library (e.g., transformers, etc.)
#Changes to main branch to another branch