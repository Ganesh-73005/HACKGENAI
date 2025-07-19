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
import google.generativeai as genai
import os

# ---- Setup ----
st.set_page_config(page_title="Moodboard Theme & Design Recommender", layout="wide")
st.markdown("<h1 style='text-align: center;'>Moodboard Theme & Design Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>AI-powered visual mood and color inspiration based on your text or image input.</p>", unsafe_allow_html=True)

theme_data = load_theme_data()
input_mode = st.radio("Choose input type:", ["Text Prompt", "Upload Image", "Color Correction"], horizontal=True)

# ---- TEXT PROMPT MODE ----
if input_mode == "Text Prompt":
    prompt = st.text_area("Enter a descriptive scene prompt:", height=100, placeholder="e.g., A man walking in a sand-covered battlefield, 1917")

    if st.button("Analyze Prompt"):
        if prompt.strip():
            from prompt_analysis.recommend_color import guess_top_themes_with_gemini
            top_themes = guess_top_themes_with_gemini(prompt, theme_data)

            if not top_themes:
                st.error("Couldn't guess any themes.")
            else:
                st.subheader("Top 3 Matched Themes")

                for i, entry in enumerate(top_themes):
                    st.markdown(f"### {i+1}. {entry['theme'].title()} — Score: `{entry['score']:.2f}`")

                    with st.expander(f"View Moodboard: {entry['theme'].title()}"):
                        attributes = recommend_attributes(entry["theme"], theme_data)

                        st.markdown(f"**Lighting:** `{attributes['lighting']}`")

                        st.markdown("**Costumes:**")
                        for costume in attributes["costumes"]:
                            st.markdown(f"- {costume}")

                        st.markdown("**Color Palette:**")
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

# ---- IMAGE MODE ----
elif input_mode == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image to extract colors and predict moodboard themes", type=["jpg", "jpeg", "png"])

    def extract_dominant_colors(image, n_clusters=5):
        image = image.resize((200, 200))
        img_np = np.array(image).reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(img_np)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Extracting dominant colors and analyzing..."):
                extracted_colors = extract_dominant_colors(image)

                st.subheader("Extracted Dominant Colors")
                color_strip_html = "".join(
                    f'<div style="flex:1; height:60px; background-color:{color};"></div>'
                    for color in extracted_colors
                )
                st.markdown(
                    f'<div style="display:flex; border-radius:8px; overflow:hidden; margin: 1rem 0;">{color_strip_html}</div>',
                    unsafe_allow_html=True
                )

                top_themes = guess_themes_from_colors(extracted_colors, theme_data)

                if not top_themes:
                    st.error("Couldn't guess any themes from the image.")
                else:
                    st.subheader("Top 3 Matched Themes")

                    for i, entry in enumerate(top_themes):
                        st.markdown(f"### {i+1}. {entry['theme'].title()} — Score: `{entry['score']:.2f}`")

                        with st.expander(f"View Moodboard: {entry['theme'].title()}"):
                            attributes = recommend_attributes(entry["theme"], theme_data)

                            st.markdown(f"**Lighting:** `{attributes['lighting']}`")

                            st.markdown("**Costumes:**")
                            for costume in attributes["costumes"]:
                                st.markdown(f"- {costume}")

                            st.markdown("**Theme Color Palette:**")
                            theme_strip_html = "".join(
                                f'<div style="flex:1; height:40px; background-color:{color};"></div>'
                                for color in attributes["colors"]
                            )
                            st.markdown(
                                f'<div style="display:flex; border-radius:8px; overflow:hidden; margin-bottom:1rem;">{theme_strip_html}</div>',
                                unsafe_allow_html=True
                            )
                        st.divider()

# ---- COLOR CORRECTION MODE ----
else:
    st.subheader("Color Correction Tool")
    uploaded_file = st.file_uploader("Upload an image to compare with a target theme", type=["jpg", "jpeg", "png"], key="correction")
    desired_theme = st.text_input("Enter your desired theme (e.g., Noir, Fairytale, Sci-Fi, Festival of Colors)")

    if uploaded_file and desired_theme:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        def extract_dominant_colors(image, n_clusters=5):
            image = image.resize((200, 200))
            img_np = np.array(image).reshape(-1, 3)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(img_np)
            dominant_colors = kmeans.cluster_centers_.astype(int)
            return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]

        extracted_colors = extract_dominant_colors(image)

        st.subheader("Extracted Colors from Image")
        color_strip_html = "".join(
            f'<div style="flex:1; height:60px; background-color:{color};"></div>'
            for color in extracted_colors
        )
        st.markdown(
            f'<div style="display:flex; border-radius:8px; overflow:hidden; margin-bottom:1rem;">{color_strip_html}</div>',
            unsafe_allow_html=True
        )

        st.subheader("Color Analysis")

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        prompt = f"""
        The uploaded image contains these dominant colors: {extracted_colors}.
        The user wants the scene to match the theme "{desired_theme}".

        1. Analyze how much the current costume and color style fits the desired theme.
        2. Recommend changes in costumes, lighting, background, and color grading to better match the theme.
        3. Provide a structured breakdown:
        - Fit Score (0–10)
        - Current Mood
        - Suggested Adjustments
        4. Additionally:
        - Mention at least 2 famous movies, artworks, or fashion examples that represent the "{desired_theme}" theme.
        - Suggest 3 search keywords or phrases the user can Google or search on Pinterest to explore matching visual references.
        """


        with st.spinner("Analyzing your theme and image"):
            response = model.generate_content([prompt, image])
            st.markdown(response.text)

    elif uploaded_file and not desired_theme:
        st.warning("Please enter a theme name.")
