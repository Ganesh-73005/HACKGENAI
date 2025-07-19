# classify_prompt.py

import torch
import clip
from PIL import Image
import os
import json

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def load_labels():
    with open("D:/Projects/Programs/python/KIf/mood_board_ai/data/theme_map.json", "r") as f:
        theme_map = json.load(f)
    return list(theme_map.keys())

def classify_prompt(user_prompt: str) -> str:
    labels = load_labels()
    text_inputs = torch.cat([clip.tokenize(f"This is a {label} scene") for label in labels]).to(device)

    with torch.no_grad():
        prompt_features = model.encode_text(clip.tokenize(user_prompt).to(device))
        label_features = model.encode_text(text_inputs)

        prompt_features /= prompt_features.norm(dim=-1, keepdim=True)
        label_features /= label_features.norm(dim=-1, keepdim=True)

        similarities = (100.0 * prompt_features @ label_features.T).softmax(dim=-1)
        predicted_index = similarities.argmax().item()

    return labels[predicted_index]

def classify_image(image_path: str) -> str:
    labels = load_labels()
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"This is a {label} scene") for label in labels]).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_inputs)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarities = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        predicted_index = similarities.argmax().item()

    return labels[predicted_index]
