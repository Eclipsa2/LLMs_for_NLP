from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch
import json
import math

max_length = 2048
adapter_path = "model/mgpt-lora-adapter"

tokenizer = AutoTokenizer.from_pretrained(adapter_path)
peft_config = PeftConfig.from_pretrained(adapter_path)

base_model = AutoModelForCausalLM.from_pretrained(
    peft_config.base_model_name_or_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

model = PeftModel.from_pretrained(base_model, adapter_path)
model.to("cuda")
model.eval()

content = json.load(open("moldova_dataset.json", "r"))

results_title = {
    "perplexity": [],
    "neg_log_likelihood": [],
}

results_content = {
    "perplexity": [],
    "neg_log_likelihood": [],
}

def ensure_json_serializable(obj):
    if hasattr(obj, 'item'):
        return obj.item()
    elif hasattr(obj, 'tolist'):
        return obj.tolist()
    else:
        return float(obj)

def get_perplexity(text, model, tokenizer):
    input = tokenizer(text, return_tensors="pt").to(model.device)
    input_ids = input["input_ids"].to(model.device)

    if input_ids.size(1) <= max_length:
        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)

        neg_log_likelihood = outputs.loss.item()
        perplexity = math.exp(neg_log_likelihood)

        return perplexity, neg_log_likelihood

    total_loss = 0
    total_tokens = 0

    stride = max_length // 2

    for i in range(0, input_ids.size(1), stride):
        end_idx = min(i + max_length, input_ids.size(1))
        chunk_input_ids = input_ids[:, i:end_idx]

        with torch.no_grad():
            outputs = model(chunk_input_ids, labels=chunk_input_ids)

        chunk_tokens = chunk_input_ids.size(1)
        total_loss += outputs.loss.item() * chunk_tokens
        total_tokens += chunk_tokens

        if end_idx == input_ids.size(1):
            break

    avg_neg_log_likelihood = total_loss / total_tokens
    perplexity = math.exp(avg_neg_log_likelihood)

    return perplexity, avg_neg_log_likelihood

for news in content:
    print("-" * 50)
    for key, value in news.items():
        if key =="metadata":
            continue

        if len(value) == 0:
            continue

        print(key, value)

        perplexity, neg_log_likelihood = get_perplexity(value, model, tokenizer)

        if key == "title":
            results_title['perplexity'].append(ensure_json_serializable(perplexity))
            results_title['neg_log_likelihood'].append(ensure_json_serializable(neg_log_likelihood))

        elif key == "content":
            results_content['perplexity'].append(ensure_json_serializable(perplexity))
            results_content['neg_log_likelihood'].append(ensure_json_serializable(neg_log_likelihood))

with open("results_title_moldova.json", "w") as file:
    json.dump(results_title, file, indent=4)

with open("results_content_moldova.json", "w") as file:
    json.dump(results_content, file, indent=4)
