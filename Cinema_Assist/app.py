import streamlit as st
import google.generativeai as genai
from utilities import generate_pdf
import json
import re
import pandas as pd
import time

# Streamlit page config - MUST BE FIRST
st.set_page_config(
    page_title="Cinematography Shot Recommender", 
    layout="wide",
    page_icon="🎬",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #00ffff;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(45deg, #1a0033 0%, #0d1421 50%, #000000 100%);
        color: #00ffff;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), 0 0 60px rgba(255, 0, 128, 0.3);
        border: 2px solid #00ffff;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }
    
    .main-header h1 {
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #1a0033 0%, #330066 100%);
        color: #00ffff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #ff0080;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(255, 0, 128, 0.4), inset 0 0 20px rgba(0, 255, 255, 0.1);
        font-family: 'Rajdhani', sans-serif;
    }
    
    .feature-card h3 {
        color: #ff0080;
        text-shadow: 0 0 10px rgba(255, 0, 128, 0.8);
        font-family: 'Orbitron', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .feature-card p {
        color: #00ffff;
        font-size: 1.1rem;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.6);
    }
    
    .shot-card {
        background: linear-gradient(135deg, #0d1421 0%, #1a0033 50%, #000000 100%);
        color: #00ffff;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(255, 0, 128, 0.1);
        margin: 1rem 0;
        border: 2px solid #00ffff;
        font-family: 'Rajdhani', sans-serif;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .shot-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }

    .shot-card:hover::before {
        left: 100%;
    }

    .shot-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 35px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(255, 0, 128, 0.2);
    }

    .shot-card h4 {
        color: #ff0080;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(255, 0, 128, 0.8);
        font-family: 'Orbitron', monospace;
    }

    .shot-card p {
        color: #00ffff;
        line-height: 1.6;
        margin: 0;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.6);
        font-size: 1rem;
    }
    
    .camera-card {
        border-color: #00ffff !important;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.4), inset 0 0 15px rgba(0, 255, 255, 0.1) !important;
    }

    .lighting-card {
        border-color: #ffff00 !important;
        box-shadow: 0 0 25px rgba(255, 255, 0, 0.4), inset 0 0 15px rgba(255, 255, 0, 0.1) !important;
    }

    .lighting-card h4 {
        color: #ffff00 !important;
        text-shadow: 0 0 10px rgba(255, 255, 0, 0.8) !important;
    }

    .lens-card {
        border-color: #ff0080 !important;
        box-shadow: 0 0 25px rgba(255, 0, 128, 0.4), inset 0 0 15px rgba(255, 0, 128, 0.1) !important;
    }
    
    .metric-card {
        background: linear-gradient(45deg, #ff0080, #00ffff, #8000ff);
        color: #000000;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
        font-family: 'Orbitron', monospace;
        font-weight: 700;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff0080 0%, #00ffff 50%, #8000ff 100%);
        color: #000000;
        border: 2px solid #00ffff;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-family: 'Orbitron', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
        text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.6), 0 0 50px rgba(255, 0, 128, 0.4);
        background: linear-gradient(45deg, #00ffff 0%, #ff0080 50%, #8000ff 100%);
    }
    
    .scene-input {
        border-radius: 15px;
        border: 2px solid #00ffff;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.7);
        color: #00ffff;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 100%);
    }

    /* Text styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', monospace;
        color: #00ffff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
    }

    p, div, span {
        font-family: 'Rajdhani', sans-serif;
        color: #00ffff;
    }

    /* Metrics styling */
    .metric-container {
        background: linear-gradient(135deg, #1a0033 0%, #330066 100%);
        border: 1px solid #ff0080;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.3);
    }

    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #003300 0%, #006600 100%);
        border: 1px solid #00ff00;
        color: #00ff00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
    }

    .stError {
        background: linear-gradient(135deg, #330000 0%, #660000 100%);
        border: 1px solid #ff0000;
        color: #ff0000;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.3);
    }

    .stWarning {
        background: linear-gradient(135deg, #332200 0%, #664400 100%);
        border: 1px solid #ffaa00;
        color: #ffaa00;
        box-shadow: 0 0 15px rgba(255, 170, 0, 0.3);
    }

    /* Footer styling */
    .footer-cyberpunk {
        text-align: center;
        color: #00ffff;
        padding: 2rem;
        background: linear-gradient(135deg, #1a0033 0%, #000000 100%);
        border-top: 2px solid #ff0080;
        margin-top: 2rem;
        font-family: 'Rajdhani', sans-serif;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
    }

    /* Glowing divider */
    .cyberpunk-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ffff, #ff0080, #00ffff, transparent);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎬 Cinematography Shot Recommender</h1>
    <p>Professional shot recommendations powered by AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.markdown("### 📋 How it works")
    st.markdown("""
    1. **Describe your scene** in detail
    2. **Click Generate** to get AI recommendations
    3. **Review** camera angles, lighting, and lens options
    4. **Download** your shot list as PDF
    """)
    
    st.markdown("### 🎯 Features")
    st.markdown("""
    - **Camera Angles**: Professional shot compositions
    - **Lighting Setups**: Mood and atmosphere guidance
    - **Lens Options**: Technical specifications
    - **PDF Export**: Professional shot lists
    """)
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Include **emotions** and **mood**
    - Mention **character actions**
    - Describe the **environment**
    - Note any **specific requirements**
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Scene Description")
    
    # Example scenes for inspiration
    example_scenes = [
        "A young girl walks through a dark forest, hearing whispers",
        "Two lovers meet secretly on a moonlit rooftop in Paris",
        "A detective examines evidence in a dimly lit crime scene",
        "Children play in a sunny meadow during golden hour",
        "A tense boardroom meeting with corporate executives"
    ]
    
    selected_example = st.selectbox(
        "Choose an example or write your own:",
        ["Write your own..."] + example_scenes
    )
    
    if selected_example != "Write your own...":
        scene_description = st.text_area(
            "Scene Description",
            value=selected_example,
            height=120,
            help="Describe your scene in detail including mood, characters, and setting"
        )
    else:
        scene_description = st.text_area(
            "Scene Description",
            placeholder="e.g., A young girl walks through a dark forest, hearing whispers...",
            height=120,
            help="Describe your scene in detail including mood, characters, and setting"
        )

with col2:
    st.markdown("### 🎥 Quick Stats")
    
    # Display some metrics
    if scene_description:
        word_count = len(scene_description.split())
        char_count = len(scene_description)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Words", word_count)
        with col_b:
            st.metric("Characters", char_count)
        
        # Scene analysis preview
        if word_count > 5:
            st.success("✅ Good detail level")
        elif word_count > 2:
            st.warning("⚠️ Add more details")
        else:
            st.info("💡 Describe your scene")

# Gemini API key
GEMINI_API_KEY = "AIzaSyDvUfn2DCjBHQn2p_DArEYRi6slWKH3dKM"

def get_shot_recommendations(scene_description, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    
    prompt = (
        "You are an expert cinematographer with knowledge of film school techniques and famous film breakdowns. "
        "Based on the following scene description, provide a concise shot list with:\n"
        "- 3-5 camera angles (e.g., Dutch tilt, over-the-shoulder, wide shot)\n"
        "- 2-3 lighting setups (e.g., low-key lighting, Rembrandt lighting)\n"
        "- 2-3 lens options (e.g., 85mm for portraits, 24mm for wide tension shots)\n"
        "Analyze the tone, emotion, and narrative focus of the scene to make recommendations.\n"
        f"Scene description: \"{scene_description}\"\n"
        "Format the response as a JSON object with fields: camera_angles, lighting_setups, lens_options. "
        "Each item in those lists should be an object with `name` and `description` fields. "
        "Respond ONLY with a JSON object and nothing else."
    )
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        return json.loads(json_str)
    else:
        raise ValueError("No valid JSON found in Gemini response.")

def display_recommendations(title, data, icon, card_class):
    if isinstance(data, list) and data:
        st.markdown(f"### {icon} {title}")
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                name = item.get('name', f'Option {i+1}')
                description = item.get('description', 'No description available')
                
                st.markdown(f"""
                <div class="shot-card {card_class}">
                    <h4>{name}</h4>
                    <p>{description}</p>
                </div>
                """, unsafe_allow_html=True)

# Generate button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🎬 Generate Shot List", use_container_width=True)

if generate_button:
    if not scene_description:
        st.error("⚠️ Please enter a scene description to continue.")
    else:
        # Show loading animation
        with st.spinner("🎭 Analyzing your scene and generating recommendations..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            try:
                shot_list = get_shot_recommendations(scene_description, GEMINI_API_KEY)
                
                # Clear progress bar
                progress_bar.empty()
                
                # Display scene info
                st.markdown("---")
                st.markdown(f"""
                <div class="feature-card">
                    <h3>🎬 Scene Analysis Complete</h3>
                    <p><strong>Scene:</strong> {scene_description}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display recommendations in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    display_recommendations(
                        "Camera Angles", 
                        shot_list.get("camera_angles", []), 
                        "📹", 
                        "camera-card"
                    )
                
                with col2:
                    display_recommendations(
                        "Lighting Setups", 
                        shot_list.get("lighting_setups", []), 
                        "💡", 
                        "lighting-card"
                    )
                
                with col3:
                    display_recommendations(
                        "Lens Options", 
                        shot_list.get("lens_options", []), 
                        "🔍", 
                        "lens-card"
                    )
                
                # Summary metrics
                st.markdown("---")
                st.markdown("### 📊 Shot List Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Camera Angles", len(shot_list.get("camera_angles", [])))
                with col2:
                    st.metric("Lighting Setups", len(shot_list.get("lighting_setups", [])))
                with col3:
                    st.metric("Lens Options", len(shot_list.get("lens_options", [])))
                with col4:
                    total_shots = sum(len(shot_list.get(key, [])) for key in shot_list.keys())
                    st.metric("Total Recommendations", total_shots)
                
                # PDF download
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    pdf_buffer = generate_pdf(scene_description, shot_list)
                    st.download_button(
                        label="📄 Download Shot List as PDF",
                        data=pdf_buffer,
                        file_name=f"shot_list_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                # Success message
                st.success("🎉 Shot list generated successfully! Your professional recommendations are ready.")
                
            except Exception as e:
                st.error(f"❌ Error generating shot list: {str(e)}")
                st.info("💡 Please try again or check your scene description.")

# Footer
st.markdown("---")
st.markdown("""
<div class="cyberpunk-divider"></div>
<div class="footer-cyberpunk">
    <p>🎬 CINEMATOGRAPHY SHOT RECOMMENDER | POWERED BY AI</p>
    <p>>>> CREATE PROFESSIONAL SHOT LISTS FOR YOUR FILM PROJECTS <<<</p>
    <p style="font-family: 'Orbitron', monospace; font-size: 0.8rem; color: #ff0080;">CYBERPUNK EDITION v2.0</p>
</div>
""", unsafe_allow_html=True)
