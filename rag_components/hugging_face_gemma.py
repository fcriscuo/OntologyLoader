from transformers import AutoTokenizer, AutoModelForCausalLM
import huggingface_hub

access_token = "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"
# Login using the access token
huggingface_hub.login(token=access_token)

# Optional: To check if you are logged in
whoami = huggingface_hub.whoami()
print(whoami)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b")
model = AutoModelForCausalLM.from_pretrained("google/gemma-7b")

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt")

outputs = model.generate(**input_ids)
print(tokenizer.decode(outputs[0]))
