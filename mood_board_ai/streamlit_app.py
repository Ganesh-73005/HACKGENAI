import streamlit as st
from prompt_analysis.classify_prompt import classify_prompt
from prompt_analysis.recommend_color import (
    load_theme_data,
    recommend_attributes,
    guess_themes_from_colors,
)
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import os

st.set_page_config(page_title="Scene Theme & Color Advisor", layout="wide")
st.title("🎨 Moodboard Theme & Design Recommender")

theme_data = load_theme_data()

input_mode = st.radio("Choose input type:", ["Text Prompt", "Upload Image"])

if input_mode == "Text Prompt":
    prompt = st.text_area("Enter a prompt (e.g., A man walking in a sand-covered battlefield, 1917)", height=100)
    
    if st.button("Analyze Prompt"):
        if prompt.strip():
            from prompt_analysis.recommend_color import guess_top_themes_with_gemini
            top_themes = guess_top_themes_with_gemini(prompt, theme_data)

            if not top_themes:
                st.error("Couldn't guess any themes.")
            else:
                st.subheader("🎯 Top 3 Matched Themes:")

                for i, entry in enumerate(top_themes):
                    st.markdown(f"**{i+1}. {entry['theme'].title()}** — Score: `{entry['score']:.2f}`")

                st.divider()
                for entry in top_themes:
                    theme = entry["theme"]
                    score = entry["score"]
                    attributes = recommend_attributes(theme, theme_data)

                    st.subheader(f"🎭 Recommended Moodboard for: `{theme.title()}` (Score: `{score:.2f}`)")
                    st.markdown(f"**🎬 Lighting:** `{attributes['lighting']}`")

                    st.markdown("**🧥 Costumes:**")
                    for costume in attributes["costumes"]:
                        st.markdown(f"- {costume}")

                    st.markdown("**🎨 Color Palette:**")
                    color_strip_html = "".join(
                        f'<div style="flex:1; height:40px; background-color:{color};"></div>'
                        for color in attributes["colors"]
                    )
                    st.markdown(
                        f'<div style="display:flex; border-radius:8px; overflow:hidden; margin-bottom:1rem;">{color_strip_html}</div>',
                        unsafe_allow_html=True
                    )

                    st.divider()
        else:
            st.warning("Please enter a prompt.")

# --- PHOTO MODE ---

else:
    uploaded_file = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"])
    
    def extract_dominant_colors(image, n_clusters=5):
        image = image.resize((200, 200))
        img_np = np.array(image)
        img_np = img_np.reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(img_np)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]
        return hex_colors

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Extracting colors and analyzing..."):
                extracted_colors = extract_dominant_colors(image)

                st.subheader("🎨 Extracted Dominant Colors:")
                color_cols = st.columns(len(extracted_colors))
                for i, color in enumerate(extracted_colors):
                    with color_cols[i]:
                        st.color_picker(f"Color {i+1}", color, label_visibility="collapsed")

                # Call Gemini to guess themes from extracted colors
                top_themes = guess_themes_from_colors(extracted_colors, theme_data)

                if not top_themes:
                    st.error("Couldn't guess any themes from the image.")
                else:
                    st.subheader("🎯 Top 3 Matched Themes:")

                    for i, entry in enumerate(top_themes):
                        st.markdown(f"**{i+1}. {entry['theme'].title()}** — Score: `{entry['score']:.2f}`")

                    st.divider()
                    for entry in top_themes:
                        theme = entry["theme"]
                        score = entry["score"]
                        attributes = recommend_attributes(theme, theme_data)

                        st.subheader(f"🎭 Recommended Moodboard for: `{theme.title()}` (Score: `{score:.2f}`)")
                        st.markdown(f"**🎬 Lighting:** `{attributes['lighting']}`")

                        st.markdown("**🧥 Costumes:**")
                        for costume in attributes["costumes"]:
                            st.markdown(f"- {costume}")

                        st.markdown("**🎨 Extracted Color Palette:**")
                        color_strip_html = "".join(
                            f'<div style="flex:1; height:80px; background-color:{color};"></div>'
                            for color in extracted_colors
                        )
                        st.markdown(
                            f'<div style="display:flex; border-radius:8px; overflow:hidden; margin-bottom:1rem;">{color_strip_html}</div>',
                            unsafe_allow_html=True
                        )

                        st.divider()
