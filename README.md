# Moodboard Theme & Design Recommender

An AI-powered Streamlit application that analyzes text descriptions and images to recommend matching visual themes, color palettes, lighting styles, and costume ideas for creative projects.

## 🎨 Features

### Three Analysis Modes

1. **Text Prompt Analysis**
   - Describe a scene, mood, or setting in natural language
   - AI analyzes the description to suggest matching themes
   - Get recommendations for colors, lighting, and costumes

2. **Image Analysis**
   - Upload images to extract dominant colors
   - AI matches colors to appropriate moodboard themes
   - Discover themes that complement your visual content

3. **Color Correction Mode**
   - Compare your image's colors with a target theme
   - Get professional suggestions for better visual matching
   - Receive specific recommendations for lighting, styling, and color grading

### Key Capabilities

- **AI-Powered Theme Matching**: Uses Google's Gemini AI for intelligent scene analysis
- **Color Extraction**: Advanced K-means clustering for dominant color identification
- **Reference Links**: Automatic fetching of lighting references and costume shopping links
- **Interactive Color Palettes**: Visual color swatches with hover effects
- **Session History**: Track and review all your analyses
- **Responsive Design**: Modern orange-themed UI with transparent cards and gradients

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Required Dependencies

\`\`\`bash
pip install streamlit
pip install pillow
pip install numpy
pip install scikit-learn
pip install google-generativeai
pip install duckduckgo-search
\`\`\`

### Environment Variables

Create a \`.env\` file in your project root:

\`\`\`env
GEMINI_API_KEY=your_google_gemini_api_key_here
\`\`\`

## 📁 Project Structure

\`\`\`
moodboard-recommender/
├── streamlit_app.py          # Main Streamlit application
├── prompt_analysis/
│   ├── classify_prompt.py    # Prompt classification logic
│   └── recommend_color.py    # Color recommendation functions
├── README.md
├── requirements.txt
└── .env                      # Environment variables (create this)
\`\`\`

## 🔧 Setup Instructions

1. **Clone or download the project files**

2. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set up Google Gemini API**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your \`.env\` file

4. **Prepare your theme data**:
   - Ensure your \`prompt_analysis\` module contains the required functions:
     - \`load_theme_data()\`
     - \`recommend_attributes()\`
     - \`guess_themes_from_colors()\`
     - \`guess_top_themes_with_gemini()\`

5. **Run the application**:
   \`\`\`bash
   streamlit run streamlit_app.py
   \`\`\`

## 🎯 Usage Guide

### Text Prompt Analysis

1. Select "Text Prompt" mode
2. Enter a detailed description of your scene or mood
3. Click "Analyze Scene"
4. Review the top 3 matched themes with fit scores
5. Explore moodboards for lighting, costumes, and color palettes

**Example Prompts**:
- "A mysterious figure walking through a foggy Victorian street at midnight, gas lamps casting eerie shadows"
- "Bright summer festival with colorful decorations and joyful crowds dancing"
- "Futuristic cyberpunk cityscape with neon lights reflecting on wet streets"

### Image Analysis

1. Select "Upload Image" mode
2. Upload a JPG, JPEG, or PNG file
3. Click "Analyze Image Colors"
4. View extracted color palette
5. Explore matching themes based on your image's colors

### Color Correction

1. Select "Color Correction" mode
2. Upload an image for analysis
3. Enter your target theme (e.g., "Film Noir", "Vintage", "Cyberpunk")
4. Click "Analyze Color Matching"
5. Review comprehensive recommendations for achieving your desired aesthetic

## 🎨 UI Features

### Modern Design Elements

- **Orange Gradient Theme**: Consistent orange color scheme throughout
- **Transparent Cards**: Clean, modern card design with orange borders
- **Interactive Elements**: Hover effects and smooth animations
- **Progress Indicators**: Visual feedback during AI processing
- **Responsive Layout**: Optimized for desktop and mobile viewing

### Session Management

- **Real-time Statistics**: Track your analysis count and history
- **Detailed History**: Review all previous analyses with timestamps
- **Easy Navigation**: Intuitive button-based mode switching
- **Data Persistence**: Session data maintained during your visit

## 🔍 Technical Details

### AI Integration

- **Google Gemini AI**: Advanced language model for scene analysis
- **DuckDuckGo Search**: Automatic reference link fetching
- **K-means Clustering**: Scientific color extraction from images

### Color Processing

- **Dominant Color Extraction**: Uses scikit-learn's K-means algorithm
- **Color Palette Generation**: Creates visual color swatches
- **Theme Matching**: Intelligent color-to-theme correlation

### Error Handling

- **Graceful Degradation**: Continues working even if external APIs fail
- **Type Safety**: Robust handling of different data types
- **User Feedback**: Clear error messages and warnings

## 🛠️ Customization

### Adding New Themes

Extend your theme data in the \`prompt_analysis\` module:

\`\`\`python
# Example theme structure
new_theme = {
    "name": "steampunk",
    "colors": ["#8B4513", "#CD853F", "#DAA520", "#2F4F4F"],
    "lighting": "Warm amber lighting with dramatic shadows",
    "costumes": ["Victorian-era clothing", "Brass accessories", "Goggles"]
}
\`\`\`

### Styling Modifications

Update the CSS in \`streamlit_app.py\` to change:
- Color schemes (modify gradient values)
- Card styling (adjust border radius, padding)
- Typography (change fonts, sizes)

## 📊 Performance Considerations

- **Image Processing**: Images are resized to 200x200 for faster processing
- **API Rate Limits**: Built-in error handling for API limitations
- **Memory Management**: Efficient color extraction algorithms
- **Caching**: Session state management for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source. Please check the license file for details.

## 🆘 Troubleshooting

### Common Issues

**"Module not found" errors**:
- Ensure all dependencies are installed: \`pip install -r requirements.txt\`
- Check that your \`prompt_analysis\` module is properly structured

**API Key errors**:
- Verify your \`.env\` file contains the correct Gemini API key
- Ensure the API key has proper permissions

**Image upload issues**:
- Supported formats: JPG, JPEG, PNG
- Maximum recommended size: 10MB
- Ensure images are not corrupted

**Theme matching problems**:
- Check that your theme data is properly formatted
- Verify the \`load_theme_data()\` function returns valid data

### Getting Help

1. Check the error messages in the Streamlit interface
2. Review the console output for detailed error information
3. Ensure all environment variables are properly set
4. Verify your internet connection for API calls

## 🔮 Future Enhancements

- **Export Functionality**: Save moodboards as PDF or image files
- **Theme Comparison**: Side-by-side theme analysis
- **User Favorites**: Save and organize favorite themes
- **Social Sharing**: Share moodboard results
- **Dark Mode Toggle**: Alternative color schemes
- **Advanced Filters**: More granular theme filtering options

---

**Made with ❤️ using Streamlit and AI**

For questions or support, please refer to the troubleshooting section or check the project documentation.
