import json
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from PIL import Image
import numpy as np

load_dotenv()  # loads from .env by default

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def load_theme_data(path="D:/Projects/Programs/python/KIf/mood_board_ai/data/theme_map.json"):
    with open(path, "r") as f:
        return json.load(f)

def guess_top_themes_with_gemini(prompt: str, theme_data: dict) -> list:
    theme_descriptions = []
    for theme, data in theme_data.items():
        keywords = ", ".join(data.get("prompt_keywords", []))
        theme_descriptions.append(f"{theme} ({keywords})")

    theme_prompt = "\n".join(theme_descriptions)

    model = genai.GenerativeModel("models/gemini-2.5-pro")
    response = model.generate_content(f"""
You are given a user prompt: "{prompt}".

Here are available themes and their associated keywords:
{theme_prompt}

Identify the top 3 most relevant themes for the prompt.
Respond with a JSON list of objects like this:
[
  {{"theme": "war", "score": 0.91}},
  {{"theme": "desert", "score": 0.73}},
  {{"theme": "cyberpunk", "score": 0.65}}
]
Only respond with the JSON. No explanation.
""")
    print("[Gemini Raw Response]:", response)


    raw_text = response.text.strip()
    print("[Gemini Raw Response]:", raw_text)

    match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            result = json.loads(json_str)
            return [entry for entry in result if entry["theme"] in theme_data]
        except json.JSONDecodeError as e:
            print(f"[Error parsing Gemini JSON]: {e}")
    else:
        print("[Error]: No JSON block found in Gemini response.")

def recommend_attributes(theme_label: str, theme_data: dict) -> dict:
    return theme_data.get(theme_label, {
        "colors": ["#FF00FF"],
        "lighting": ["fallback lighting"],
        "costumes": ["unknown"]
    })


def extract_dominant_colors(image_path: str, num_colors=5) -> list:
    image = Image.open(image_path).convert("RGB")
    image = image.resize((200, 200))  # Resize for faster processing
    img_array = np.array(image).reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, n_init=10)
    kmeans.fit(img_array)
    centers = kmeans.cluster_centers_

    # Convert to hex color codes
    hex_colors = ['#%02x%02x%02x' % tuple(map(int, center)) for center in centers]
    return hex_colors

def guess_themes_from_colors(colors: list, theme_data: dict) -> list:
    theme_color_map = {
        theme: data.get("colors", []) for theme, data in theme_data.items()
    }

    # Prepare a string prompt for Gemini based on dominant colors
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    prompt = f"""
You are given a list of dominant colors from an image: {colors}

Here are available themes and their color palettes:
{json.dumps(theme_color_map, indent=2)}

Compare the dominant image colors to each theme's palette. Also think logically on what would be theme of the scene if the color palettes are as given and return the 3 most relevant theme matches with confidence scores. Condition is that the 3 themes should present in the available themes.
Respond ONLY with JSON in this format:
[
  {{"theme": "war", "score": 0.85}},
  {{"theme": "neo noir", "score": 0.79}},
  {{"theme": "surreal", "score": 0.69}}
]
"""
    response = model.generate_content(prompt)
    print("[Gemini Color Response]:", response.text)

    match = re.search(r"```json\s*(.*?)\s*```", response.text.strip(), re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(1))
            return [entry for entry in result if entry["theme"] in theme_data]
        except json.JSONDecodeError as e:
            print(f"[Gemini Color JSON Parse Error]: {e}")
    else:
        try:
            return json.loads(response.text.strip())  # fallback if no ```json block
        except:
            print("[Gemini Color Parse Error]: Response not JSON")
    return []
