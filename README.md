
# Film Production AI Suite

![Banner Image](https://via.placeholder.com/1200x400?text=Film+Production+AI+Suite)

A comprehensive set of AI-powered tools for modern filmmakers, combining storyboard generation with visual theme recommendation capabilities.

## 🌟 Key Features

### 1. AI Storyboard Generator
**Transform scripts into visual storyboards with technical specifications**
- Automatic scene splitting with Llama Maverick
- Runway Gen4 for consistent image generation
- CLIP + QA-Former for technical recommendations (lens, lighting, angles)
- PDF export functionality
- MongoDB database integration

### 2. Moodboard & Design Recommender
**Create perfect visual themes for your scenes**
- Text-to-theme analysis using Gemini AI
- Image color extraction and matching
- Color correction recommendations
- Lighting and costume suggestions
- Interactive color palettes

[➡️ Explore Storyboard Generator](https://github.com/Ganesh-73005/HACKGENAI/flim-assist-storygen.git)  
[➡️ Explore Moodboard Recommender](https://github.com/Ganesh-73005/HACKGENAI/moodboard_ai.git)

## 🛠️ Unified Installation

### Prerequisites
- Python 3.8+
- MongoDB (for Storyboard Generator)
- Google Gemini API key (for Moodboard Recommender)
- RunwayML API key (for Storyboard Generator)

```bash
# Clone both repositories
git clone https://github.com/Ganesh-73005/HACKGENAI/flim-assist-storygen.git
git clone https://github.com/Ganesh-73005/HACKGENAI/moodboard_ai.git

# Install dependencies
pip install -r flim-assist-storygen/requirements.txt
pip install -r moodboard_ai/requirements.txt
```

## 📂 Project Architecture

```
film-production-ai/
├── storyboard-generator/      # AI Storyboard Generator
│   ├── app.py                 # Main Streamlit app
│   ├── services/              # AI services
│   └── ...
├── moodboard-recommender/     # Moodboard Designer      # Theme analysis
    └── ...
   
```

## 🎬 Workflow Integration

1. **Start with Storyboard Generator**
   - Split your script into scenes
   - Generate initial visual concepts
   - Get technical recommendations

2. **Refine with Moodboard Recommender**
   - Extract colors from generated images
   - Find matching themes
   - Get lighting/costume suggestions

3. **Iterate**
   - Update storyboards with refined themes
   - Maintain visual consistency
   - Export final materials

## 🌐 Web Interface

Access both tools through our unified dashboard:

```bash
# Run Storyboard Generator
streamlit run flim-assist-storygen/app.py

# Run Moodboard Recommender
streamlit run moodboard_ai/app.py
```



## ✨ Pro Edition (Coming Soon)

Upgrade to our upcoming Pro Edition for:
- Unified interface
- Cross-tool synchronization
- Advanced team collaboration
- Cloud storage integration
- Premium AI models

---


```

This README provides:

1. **Clear Navigation**: Direct links to both projects
2. **Unified Vision**: Presents them as complementary tools
3. **Technical Consistency**: Similar installation processes
4. **Workflow Integration**: Shows how they work together
5. **Future Roadmap**: Teases upcoming unified version

The design maintains each project's identity while positioning them as part of a larger ecosystem for filmmakers. The placeholder paths should be replaced with your actual repository paths.
