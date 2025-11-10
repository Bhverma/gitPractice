from transformers import AutoModelForCausalLM, AutoTokenizer

# Path to your locally saved model directory (offline)
# local_dir = "B:\\B_Programmer\\Build_AI\\Resume_enhancer\\ModelLocation\\zephyr-7b-beta-local"
local_dir = "B:/B_Programmer/Build_AI/Resume_enhancer/ModelLocation/zephyr-7b-beta-local"


# Load model and tokenizer from local disk
tokenizer = AutoTokenizer.from_pretrained(local_dir, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(local_dir, local_files_only=True)

print("Resume Assistant - type 'exit' to quit.")

while True:
    user_input = input("\nYou: ")
    if user_input.strip().lower() == "exit":
        print("Goodbye!")
        break

    # Add context for conversational feel, if desired
    prompt = (
        "Rewrite or improve this resume content:\n"
        + user_input
        + "\nAssistant:"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Print only the assistant's reply
    print("\nAssistant:", result.split("Assistant:", 1)[-1].strip())
