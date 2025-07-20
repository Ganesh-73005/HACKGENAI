import streamlit as st

# Page configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Film Assist - Storyboard Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import json
import base64
import requests
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io
from dataclasses import dataclass
from enum import Enum

# Import our services
from services.story_service import StoryService
from services.image_service import ImageService
from services.video_service import VideoService
from services.pdf_service import PDFService
from services.database_service import DatabaseService

# Configuration and Constants
class Config:
    """Application configuration constants"""
    PAGE_TITLE = "Film Assist - Storyboard Generator"
    PAGE_ICON = "🎬"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # UI Constants
    MAX_SCENES = 8
    MIN_SCENES = 3
    PREVIEW_TEXT_LENGTH = 1000
    MIN_STORY_LENGTH = 50
    MAX_RECENT_STORIES = 3
    
    # File constraints
    SUPPORTED_FILE_TYPES = ['txt']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # API URLs
    GROQ_CONSOLE_URL = "https://console.groq.com/"
    GEMINI_API_URL = "https://makersuite.google.com/"
    REPLICATE_URL = "https://replicate.com/"

class PageType(Enum):
    """Enum for page types"""
    HOME = "🏠 Home"
    CREATE_STORY = "📝 Create Story"
    MY_STORIES = "📚 My Stories"
    STORYBOARD_VIEWER = "🎨 Storyboard Viewer"
    SETTINGS = "⚙️ Settings"

class InputMethod(Enum):
    """Enum for story input methods"""
    PROMPT = "📝 Generate from Prompt"
    FILE_UPLOAD = "📁 Upload Text File"

@dataclass
class ValidationResult:
    """Data class for validation results"""
    is_valid: bool
    messages: List[str]

@dataclass
class StoryMetrics:
    """Data class for story metrics"""
    title: str
    theme: str
    genre: str
    scenes_count: int
    created_date: str

class StyleManager:
    """Manages CSS styles for the application"""
    
    @staticmethod
    def get_custom_css() -> str:
        """Returns custom CSS for the application"""
        return """
        <style>
            /* Main styling */
            .main-header {
                background: linear-gradient(90deg, #f59e0b 0%, #ea580c 100%);
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .scene-card {
                border: 2px solid #fbbf24;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .scene-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }
            
            .tech-specs {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid #f59e0b;
            }
            
            .story-title {
                color: #92400e;
                font-size: 2.5rem;
                font-weight: bold;
                text-align: center;
                margin: 1.5rem 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .upload-section {
                border: 2px dashed #fbbf24;
                border-radius: 12px;
                padding: 2rem;
                text-align: center;
                background: #fffbeb;
                margin: 1rem 0;
                transition: border-color 0.3s ease, background-color 0.3s ease;
            }
            
            .upload-section:hover {
                border-color: #f59e0b;
                background: #fef3c7;
            }
            
            .file-info {
                background: #dcfce7;
                border: 1px solid #16a34a;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
                animation: fadeIn 0.3s ease-in;
            }
            
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-left: 4px solid #f59e0b;
            }
            
            .status-success {
                background: #dcfce7;
                color: #166534;
                padding: 0.75rem;
                border-radius: 6px;
                border-left: 4px solid #16a34a;
            }
            
            .status-error {
                background: #fef2f2;
                color: #991b1b;
                padding: 0.75rem;
                border-radius: 6px;
                border-left: 4px solid #dc2626;
            }
            
            .status-warning {
                background: #fffbeb;
                color: #92400e;
                padding: 0.75rem;
                border-radius: 6px;
                border-left: 4px solid #f59e0b;
            }
            
            .status-info {
                background: #eff6ff;
                color: #1e40af;
                padding: 0.75rem;
                border-radius: 6px;
                border-left: 4px solid #3b82f6;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Responsive improvements */
            @media (max-width: 768px) {
                .main-header {
                    padding: 1rem;
                }
                .story-title {
                    font-size: 2rem;
                }
                .scene-card {
                    padding: 1rem;
                }
            }
        </style>
        """

class SessionManager:
    """Manages session state operations"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        defaults = {
            'current_scene': 0,
            'selected_story_id': None,
            'page': PageType.HOME.value,
            'default_genre': 'Adventure',
            'image_style': 'cinematic',
            'auto_generate_images': False,
            'max_scenes': 4
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get_session_value(key: str, default=None):
        """Get session state value with default"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_session_value(key: str, value):
        """Set session state value"""
        st.session_state[key] = value

class ValidationManager:
    """Handles input validation"""
    
    @staticmethod
    def validate_story_creation(title: str, theme: str, story_text: str, input_method: str) -> ValidationResult:
        """Validate story creation inputs"""
        messages = []
        
        if not title.strip():
            messages.append("❌ Story title is required")
        elif len(title.strip()) < 3:
            messages.append("⚠️ Story title should be at least 3 characters")
            
        if not theme.strip():
            messages.append("❌ Theme/Genre is required")
            
        if not story_text.strip():
            if input_method == InputMethod.PROMPT.value:
                messages.append("❌ Story prompt is required")
            else:
                messages.append("❌ Please upload a text file")
        elif len(story_text.strip()) < Config.MIN_STORY_LENGTH:
            messages.append(f"⚠️ Story content seems too short (minimum {Config.MIN_STORY_LENGTH} characters)")
        
        return ValidationResult(
            is_valid=len([msg for msg in messages if "❌" in msg]) == 0,
            messages=messages
        )
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> Tuple[bool, str, str]:
        """Validate uploaded file and return content"""
        if uploaded_file is None:
            return False, "", "No file uploaded"
        
        if uploaded_file.size > Config.MAX_FILE_SIZE:
            return False, "", f"File too large. Maximum size: {Config.MAX_FILE_SIZE // (1024*1024)}MB"
        
        try:
            file_content = uploaded_file.read()
            
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    story_text = file_content.decode(encoding)
                    return True, story_text, ""
                except UnicodeDecodeError:
                    continue
            
            return False, "", "Unable to decode file. Please ensure it's a valid text file."
            
        except Exception as e:
            return False, "", f"Error reading file: {str(e)}"

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def render_header():
        """Render main application header"""
        st.markdown(f"""
        <div class="main-header">
            <h1>{Config.PAGE_ICON} {Config.PAGE_TITLE}</h1>
            <p>Transform your stories into visual storyboards with AI-powered scene generation</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_story_metrics(metrics: StoryMetrics):
        """Render story metrics in a card layout"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="metric-card"><strong>Theme</strong><br>{metrics.theme}</div>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><strong>Genre</strong><br>{metrics.genre}</div>', 
                       unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><strong>Scenes</strong><br>{metrics.scenes_count}</div>', 
                       unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><strong>Created</strong><br>{metrics.created_date}</div>', 
                       unsafe_allow_html=True)
    
    @staticmethod
    def render_validation_messages(validation: ValidationResult):
        """Render validation messages with appropriate styling"""
        for msg in validation.messages:
            if "❌" in msg:
                st.markdown(f'<div class="status-error">{msg}</div>', unsafe_allow_html=True)
            elif "⚠️" in msg:
                st.markdown(f'<div class="status-warning">{msg}</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_tracker(step: int, total_steps: int, message: str):
        """Render progress tracking with better UX"""
        progress = step / total_steps
        st.progress(progress)
        st.markdown(f'<div class="status-info">{message}</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_file_upload_section():
        """Render enhanced file upload section"""
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("📁 **Upload your story as a text file**")
        st.markdown("Supported format: .txt files only")
        
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=Config.SUPPORTED_FILE_TYPES,
            help="Upload a .txt file containing your story. The file should contain the complete narrative you want to convert into a storyboard.",
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        return uploaded_file

class ServiceManager:
    """Manages service initialization and caching"""
    
    @staticmethod
    @st.cache_resource
    def initialize_services() -> Dict[str, Any]:
        """Initialize and cache all services"""
        return {
            'story': StoryService(),
            'image': ImageService(),
            'video': VideoService(),
            'pdf': PDFService(),
            'db': DatabaseService()
        }

class FilmAssistApp:
    """Main application class"""
    
    def __init__(self):
        self.services = ServiceManager.initialize_services()
        self.session_manager = SessionManager()
        self.validation_manager = ValidationManager()
        self.ui_components = UIComponents()
        
        # Initialize session state and apply styles
        self.session_manager.initialize_session()
        st.markdown(StyleManager.get_custom_css(), unsafe_allow_html=True)
    
    def render_navigation(self) -> str:
        """Render sidebar navigation"""
        with st.sidebar:
            st.title("Navigation")
            page = st.selectbox(
                "Choose a page:",
                [page.value for page in PageType]
            )
            
            # Add quick stats
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            try:
                stories_count = len(self.services['db'].get_all_stories())
                st.metric("Total Stories", stories_count)
            except Exception:
                st.metric("Total Stories", "N/A")
                
        return page
    
    def show_home_page(self):
        """Enhanced home page with better layout"""
        st.markdown("## Welcome to Film Assist Storyboard Generator")
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📝 Story Input
            - Upload text files (.txt)
            - Generate from prompts using AI
            - Support for multiple genres
            - Smart content validation
            """)
            
        with col2:
            st.markdown("""
            ### 🤖 AI Analysis
            - Smart scene splitting
            - Camera angle recommendations
            - Lens and lighting suggestions
            - Professional cinematography tips
            """)
            
        with col3:
            st.markdown("""
            ### 🎨 Visual Storyboard
            - Generated scene images
            - Professional layouts
            - PDF export capability
            - Video generation
            """)
        
        st.markdown("---")
        
        # Quick start section
        st.markdown("## Quick Start")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🚀 Create Your First Storyboard", type="primary", use_container_width=True):
                self.session_manager.set_session_value('page', PageType.CREATE_STORY.value)
                st.rerun()
        
        with col2:
            if st.button("📚 View My Stories", use_container_width=True):
                self.session_manager.set_session_value('page', PageType.MY_STORIES.value)
                st.rerun()
        
        # Recent stories with enhanced display
        self._render_recent_stories()
    
    def _render_recent_stories(self):
        """Render recent stories section"""
        st.markdown("## Recent Stories")
        recent_stories = self.services['db'].get_recent_stories(limit=Config.MAX_RECENT_STORIES)
        
        if recent_stories:
            for story in recent_stories:
                with st.expander(f"📖 {story['title']} - {story['theme']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Created:** {story['created_at'][:10]}")
                    with col2:
                        st.write(f"**Scenes:** {len(story.get('scenes', []))}")
                    with col3:
                        if st.button(f"View", key=f"view_{story['id']}", use_container_width=True):
                            self.session_manager.set_session_value('selected_story_id', story['id'])
                            self.session_manager.set_session_value('page', PageType.STORYBOARD_VIEWER.value)
                            st.rerun()
        else:
            st.info("No stories created yet. Create your first story to get started!")
    
    def show_create_story_page(self):
        """Enhanced story creation page"""
        st.markdown("## Create New Story")
        
        # Basic story information with better validation
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Story Title", 
                placeholder="Enter your story title",
                help="Give your story a descriptive title"
            )
            theme = st.text_input(
                "Theme/Genre", 
                placeholder="e.g., Adventure, Drama, Sci-Fi",
                help="Describe the main theme or mood of your story"
            )
            
        with col2:
            genre = st.selectbox(
                "Genre",
                ["Adventure", "Drama", "Comedy", "Horror", "Sci-Fi", "Fantasy", "Romance", "Thriller", "Action"],
                help="Select the primary genre for your story"
            )
            
            max_scenes = st.slider(
                "Maximum Scenes",
                min_value=Config.MIN_SCENES,
                max_value=Config.MAX_SCENES,
                value=self.session_manager.get_session_value('max_scenes', 4),
                help="Maximum number of scenes to generate"
            )
        
        st.markdown("---")
        
        # Story input method selection
        story_text = self._handle_story_input()
        
        st.markdown("---")
        
        # Create story with enhanced validation
        self._handle_story_creation(title, theme, genre, story_text, max_scenes)
    
    def _handle_story_input(self) -> str:
        """Handle story input method selection and processing"""
        st.markdown("### Story Input Method")
        input_method = st.radio(
            "Choose how you want to provide your story:",
            [InputMethod.PROMPT.value, InputMethod.FILE_UPLOAD.value],
            horizontal=True
        )
        
        story_text = ""
        
        if input_method == InputMethod.PROMPT.value:
            st.markdown("#### Story Prompt")
            story_text = st.text_area(
                "Describe your story idea:",
                placeholder="Describe your story idea and let AI generate the full narrative...\n\nExample: A young detective discovers a mysterious case that leads them through the dark streets of the city, uncovering secrets that challenge everything they believed about justice and truth.",
                height=150,
                help="Provide a detailed description of your story. The more specific you are, the better the AI can generate your story."
            )
        else:
            st.markdown("#### Upload Story File")
            uploaded_file = self.ui_components.render_file_upload_section()
            
            if uploaded_file is not None:
                is_valid, content, error_msg = self.validation_manager.validate_file_upload(uploaded_file)
                
                if is_valid:
                    story_text = content
                    self._render_file_info(uploaded_file, content)
                else:
                    st.error(f"❌ {error_msg}")
            else:
                st.info("👆 Please upload a .txt file to continue")
        
        return story_text
    
    def _render_file_info(self, uploaded_file, content: str):
        """Render file information after successful upload"""
        st.markdown('<div class="file-info">', unsafe_allow_html=True)
        st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"📊 File size: {len(uploaded_file.getvalue())} bytes")
        with col2:
            st.write(f"📝 Text length: {len(content)} characters")
        with col3:
            st.write(f"📄 Word count: ~{len(content.split())} words")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show preview
        with st.expander("👀 Preview uploaded content"):
            preview_text = content[:Config.PREVIEW_TEXT_LENGTH] + "..." if len(content) > Config.PREVIEW_TEXT_LENGTH else content
            st.text_area("File content preview:", value=preview_text, height=200, disabled=True)
    
    def _handle_story_creation(self, title: str, theme: str, genre: str, story_text: str, max_scenes: int):
        """Handle story creation with enhanced validation and error handling"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Validate inputs
            validation = self.validation_manager.validate_story_creation(
                title, theme, story_text, 
                InputMethod.PROMPT.value if "prompt" in str(type(story_text)) else InputMethod.FILE_UPLOAD.value
            )
            
            # Show validation messages
            if validation.messages:
                self.ui_components.render_validation_messages(validation)
            
            # Create story button
            if st.button(
                "🎬 Create Storyboard",
                type="primary",
                disabled=not validation.is_valid,
                use_container_width=True
            ):
                self._create_storyboard_with_progress(title, theme, genre, story_text, max_scenes)
    
    def _create_storyboard_with_progress(self, title: str, theme: str, genre: str, story_text: str, max_scenes: int):
        """Create storyboard with enhanced progress tracking"""
        progress_container = st.container()
        
        with progress_container:
            try:
                # Step 1: Process story content
                self.ui_components.render_progress_tracker(1, 4, "🤖 Processing story content...")
                
                if "prompt" in str(type(story_text)).lower():
                    story_content = self.services['story'].generate_story_from_prompt(story_text, theme, genre)
                else:
                    story_content = story_text
                
                # Step 2: Split into scenes
                self.ui_components.render_progress_tracker(2, 4, "🎬 Analyzing story and creating scenes...")
                
                scenes_data = self.services['story'].split_story_into_scenes(story_content, theme, genre)
                
                # Limit scenes if necessary
                if len(scenes_data) > max_scenes:
                    scenes_data = scenes_data[:max_scenes]
                
                # Step 3: Save to database
                self.ui_components.render_progress_tracker(3, 4, "💾 Saving your storyboard...")
                
                story_id = self.services['db'].create_story({
                    'title': title,
                    'theme': theme,
                    'genre': genre,
                    'content': story_content,
                    'scenes': scenes_data,
                    'created_at': datetime.now().isoformat()
                })
                
                # Step 4: Complete
                self.ui_components.render_progress_tracker(4, 4, "✅ Storyboard created successfully!")
                
                # Show success and preview
                self._show_creation_success(story_id, title, theme, genre, scenes_data)
                
            except Exception as e:
                st.error(f"❌ Error creating storyboard: {str(e)}")
                self._show_error_details(e)
    
    def _show_creation_success(self, story_id: str, title: str, theme: str, genre: str, scenes_data: List[Dict]):
        """Show success message and preview after story creation"""
        st.success("🎉 Your storyboard has been created successfully!")
        
        # Store story ID for navigation
        self.session_manager.set_session_value('selected_story_id', story_id)
        
        # Show preview
        st.markdown("### 📋 Storyboard Preview")
        
        metrics = StoryMetrics(
            title=title,
            theme=theme,
            genre=genre,
            scenes_count=len(scenes_data),
            created_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        self.ui_components.render_story_metrics(metrics)
        
        # Show first few scenes
        self._render_scene_previews(scenes_data[:2])
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎨 View Full Storyboard", type="primary", use_container_width=True):
                self.session_manager.set_session_value('page', PageType.STORYBOARD_VIEWER.value)
                st.rerun()
        
        with col2:
            if st.button("📝 Create Another Story", use_container_width=True):
                st.rerun()
    
    def _render_scene_previews(self, scenes: List[Dict]):
        """Render preview of first few scenes"""
        st.markdown("#### First Few Scenes:")
        for i, scene in enumerate(scenes):
            with st.expander(f"Scene {i+1}: {scene.get('camera_angle', 'Unknown angle')}"):
                st.write(f"**Description:** {scene.get('description', 'No description')[:200]}...")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write(f"📷 **Camera:** {scene.get('camera_angle', 'Not set')}")
                with col_b:
                    st.write(f"🔍 **Lens:** {scene.get('lens', 'Not set')}")
                with col_c:
                    st.write(f"💡 **Lighting:** {scene.get('lighting', 'Not set')}")
    
    def _show_error_details(self, error: Exception):
        """Show detailed error information"""
        with st.expander("🔍 Error Details"):
            st.code(str(error))
            st.write("**Possible solutions:**")
            st.write("- Check your API keys in the Settings page")
            st.write("- Ensure your story content is valid")
            st.write("- Try with a shorter story or different prompt")
            st.write("- Check your internet connection")
    
    def show_my_stories_page(self):
        """Enhanced stories management page"""
        st.markdown("## My Stories")
        
        stories = self.services['db'].get_all_stories()
        
        if not stories:
            self._render_empty_stories_state()
            return
        
        # Enhanced search and filter
        filtered_stories = self._render_stories_filter(stories)
        
        # Display stories with enhanced layout
        self._render_stories_list(filtered_stories)
    
    def _render_empty_stories_state(self):
        """Render empty state for stories page"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("📚 No stories found. Create your first story!")
            if st.button("📝 Create New Story", type="primary", use_container_width=True):
                self.session_manager.set_session_value('page', PageType.CREATE_STORY.value)
                st.rerun()
    
    def _render_stories_filter(self, stories: List[Dict]) -> List[Dict]:
        """Render stories filter and search interface"""
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search stories", placeholder="Search by title or theme...")
        with col2:
            sort_by = st.selectbox("Sort by", ["Created Date", "Title", "Theme"])
        with col3:
            sort_order = st.selectbox("Order", ["Newest First", "Oldest First"])
        
        # Apply filters
        filtered_stories = stories
        if search_term:
            filtered_stories = [
                story for story in stories 
                if search_term.lower() in story['title'].lower() or
                   search_term.lower() in story.get('theme', '').lower()
            ]
        
        # Apply sorting
        reverse_order = sort_order == "Newest First"
        if sort_by == "Created Date":
            filtered_stories.sort(key=lambda x: x.get('created_at', ''), reverse=reverse_order)
        elif sort_by == "Title":
            filtered_stories.sort(key=lambda x: x.get('title', '').lower(), reverse=reverse_order)
        elif sort_by == "Theme":
            filtered_stories.sort(key=lambda x: x.get('theme', '').lower(), reverse=reverse_order)
        
        st.write(f"📊 Showing {len(filtered_stories)} of {len(stories)} stories")
        
        return filtered_stories
    
    def _render_stories_list(self, stories: List[Dict]):
        """Render list of stories with enhanced layout"""
        for story in stories:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"### 📖 {story['title']}")
                    st.write(f"**Theme:** {story.get('theme', 'N/A')}")
                
                with col2:
                    st.write(f"**Genre:** {story.get('genre', 'N/A')}")
                    st.write(f"**Scenes:** {len(story.get('scenes', []))}")
                
                with col3:
                    created_date = self._format_date(story.get('created_at', 'N/A'))
                    st.write(f"**Created:** {created_date}")
                
                with col4:
                    if st.button("👁️ View", key=f"view_{story['id']}", use_container_width=True):
                        self.session_manager.set_session_value('selected_story_id', story['id'])
                        self.session_manager.set_session_value('page', PageType.STORYBOARD_VIEWER.value)
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{story['id']}", use_container_width=True):
                        self._handle_story_deletion(story)
                
                st.markdown("---")
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if date_str == 'N/A':
            return 'N/A'
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str[:10] if len(date_str) >= 10 else date_str
    
    def _handle_story_deletion(self, story: Dict):
        """Handle story deletion with confirmation"""
        confirm_key = f"confirm_delete_{story['id']}"
        
        if self.session_manager.get_session_value(confirm_key):
            self.services['db'].delete_story(story['id'])
            st.success("Story deleted!")
            # Clear confirmation state
            self.session_manager.set_session_value(confirm_key, False)
            st.rerun()
        else:
            self.session_manager.set_session_value(confirm_key, True)
            st.warning("Click again to confirm deletion!")
    
    def show_storyboard_viewer(self):
        """Enhanced storyboard viewer with better navigation"""
        st.markdown("## Storyboard Viewer")
        
        # Get selected story
        story_id = self.session_manager.get_session_value('selected_story_id')
        if not story_id:
            self._render_no_story_selected()
            return
        
        story = self.services['db'].get_story(story_id)
        if not story:
            st.error("❌ Story not found!")
            return
        
        # Render story header
        self._render_story_header(story)
        
        # Render export options
        self._render_export_options(story)
        
        # Render scene viewer
        self._render_scene_viewer(story)
    
    def _render_no_story_selected(self):
        """Render no story selected state"""
        st.warning("⚠️ No story selected. Please select a story from 'My Stories' page.")
        if st.button("📚 Go to My Stories"):
            self.session_manager.set_session_value('page', PageType.MY_STORIES.value)
            st.rerun()
    
    def _render_story_header(self, story: Dict):
        """Render story header with metrics"""
        st.markdown(f'<div class="story-title">{story["title"]}</div>', unsafe_allow_html=True)
        
        metrics = StoryMetrics(
            title=story["title"],
            theme=story.get('theme', 'N/A'),
            genre=story.get('genre', 'N/A'),
            scenes_count=len(story.get('scenes', [])),
            created_date=self._format_date(story.get('created_at', 'N/A'))
        )
        
        self.ui_components.render_story_metrics(metrics)
    
    def _render_export_options(self, story: Dict):
        """Render export options with enhanced UI"""
        st.markdown("### 📤 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as PDF", use_container_width=True):
                self._handle_pdf_export(story)
        
        with col2:
            self._render_video_export_option(story)
        
        with col3:
            if st.button("🔄 Refresh Story", use_container_width=True):
                st.rerun()
    
    def _handle_pdf_export(self, story: Dict):
        """Handle PDF export with progress tracking"""
        with st.spinner("Generating PDF..."):
            try:
                pdf_path = self.services['pdf'].generate_storyboard_pdf(story)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_file.read(),
                        file_name=f"{story['title']}_storyboard.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    def _render_video_export_option(self, story: Dict):
        """Render video export option with scene selection"""
        scenes = story.get('scenes', [])
        selected_scenes = st.multiselect(
            "Select scenes for video (3-4 scenes):",
            range(len(scenes)),
            format_func=lambda x: f"Scene {x+1}",
            max_selections=4
        )
        
        if st.button("🎥 Generate Video", disabled=len(selected_scenes) < 3, use_container_width=True):
            self._handle_video_generation(scenes, selected_scenes)
    
    def _handle_video_generation(self, scenes: List[Dict], selected_indices: List[int]):
        """Handle video generation with progress tracking"""
        with st.spinner("Generating video... This may take several minutes."):
            try:
                selected_scene_data = [scenes[i] for i in selected_indices]
                video_result = self.services['video'].generate_scene_video(selected_scene_data)
                st.success("Video generated successfully!")
                st.video(video_result['video_url'])
            except Exception as e:
                st.error(f"Error generating video: {str(e)}")
    
    def _render_scene_viewer(self, story: Dict):
        """Render enhanced scene viewer"""
        st.markdown("### 🎬 Scenes")
        
        scenes = story.get('scenes', [])
        if not scenes:
            st.warning("⚠️ No scenes found in this story.")
            return
        
        # Scene navigation
        current_scene = self._render_scene_navigation(scenes)
        
        # Current scene display
        self._render_current_scene(story, scenes, current_scene)
    
    def _render_scene_navigation(self, scenes: List[Dict]) -> int:
        """Render scene navigation controls"""
        if 'current_scene' not in st.session_state:
            st.session_state.current_scene = 0
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_scene <= 0):
                st.session_state.current_scene -= 1
                st.rerun()
        
        with col2:
            scene_num = st.selectbox(
                "Select Scene:",
                range(len(scenes)),
                index=st.session_state.current_scene,
                format_func=lambda x: f"Scene {x+1} - {scenes[x].get('camera_angle', 'Unknown')}"
            )
            st.session_state.current_scene = scene_num
        
        with col3:
            if st.button("➡️ Next", disabled=st.session_state.current_scene >= len(scenes) - 1):
                st.session_state.current_scene += 1
                st.rerun()
        
        return st.session_state.current_scene
    
    def _render_current_scene(self, story: Dict, scenes: List[Dict], current_scene_idx: int):
        """Render current scene with enhanced layout"""
        current_scene = scenes[current_scene_idx]
        
        st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
        st.markdown(f"## 🎬 Scene {current_scene_idx + 1}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_scene_image(story, current_scene, current_scene_idx, scenes)
        
        with col2:
            self._render_scene_details(story, current_scene, current_scene_idx)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_scene_image(self, story: Dict, scene: Dict, scene_idx: int, scenes: List[Dict]):
        """Render scene image with generation option"""
        if scene.get('image_url'):
            try:
                st.image(
                    scene['image_url'],
                    caption=f"Scene {scene_idx + 1}",
                    use_column_width=True
                )
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                st.info("Image not available")
        else:
            st.info("🖼️ No image generated yet")
        
        # Image generation button
        if st.button(f"🎨 Generate Image for Scene {scene_idx + 1}"):
            self._handle_image_generation(story, scene, scene_idx, scenes)
    
    def _handle_image_generation(self, story: Dict, scene: Dict, scene_idx: int, scenes: List[Dict]):
     """Handle image generation for a scene"""
     with st.spinner("Generating image... This may take a few minutes."):
        try:
            # Get previous scene for context
            reference_images = []
            if scene_idx > 0 and scenes[scene_idx - 1].get('image_url'):
                reference_images.append(scenes[scene_idx - 1]['image_url'])
                print(f"Using previous scene image as reference: {reference_images[0]}")
            
            # Generate image
            result = self.services['image'].generate_scene_image(
                prompt=scene['description'],
                style=self.session_manager.get_session_value('image_style', 'cinematic'),
                aspect_ratio="16:9",
                reference_images=reference_images,
                scene_metadata={
                    'camera_angle': scene.get('camera_angle'),
                    'lens': scene.get('lens'),
                    'lighting': scene.get('lighting')
                },
                previous_scene=scenes[scene_idx - 1] if scene_idx > 0 else None
            )
            
            # Update scene with image
            scene['image_url'] = result['image_url']
            scene['generation_metadata'] = result['generation_metadata']
            
            # Save to database
            self.services['db'].update_scene_image(
                story['id'],
                scene_idx,
                result['image_url'],
                result['generation_metadata']
            )
            
            st.success("✅ Image generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating image: {str(e)}")
    
    def _render_scene_details(self, story: Dict, scene: Dict, scene_idx: int):
        """Render scene details and editing interface"""
        # Scene description
        st.markdown("### 📝 Description")
        st.write(scene.get('description', 'No description available'))
        
        # Technical specifications
        st.markdown("### 🎥 Technical Specifications")
        st.markdown(f'<div class="tech-specs">', unsafe_allow_html=True)
        
        spec_col1, spec_col2, spec_col3 = st.columns(3)
        with spec_col1:
            st.write("**📷 Camera**")
            st.write(scene.get('camera_angle', 'Not specified'))
        with spec_col2:
            st.write("**🔍 Lens**")
            st.write(scene.get('lens', 'Not specified'))
        with spec_col3:
            st.write("**💡 Lighting**")
            st.write(scene.get('lighting', 'Not specified'))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Edit scene
        self._render_scene_editor(story, scene, scene_idx)
    
    def _render_scene_editor(self, story: Dict, scene: Dict, scene_idx: int):
        """Render scene editing interface"""
        with st.expander("✏️ Edit Scene"):
            new_description = st.text_area(
                "Description",
                value=scene.get('description', ''),
                key=f"desc_{scene_idx}",
                height=100
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                new_camera = st.text_input(
                    "Camera Angle",
                    value=scene.get('camera_angle', ''),
                    key=f"camera_{scene_idx}"
                )
                new_lens = st.text_input(
                    "Lens",
                    value=scene.get('lens', ''),
                    key=f"lens_{scene_idx}"
                )
            
            with col_b:
                new_lighting = st.text_input(
                    "Lighting",
                    value=scene.get('lighting', ''),
                    key=f"lighting_{scene_idx}"
                )
            
            if st.button("💾 Save Changes", key=f"save_{scene_idx}"):
                self._handle_scene_update(story, scene, scene_idx, {
                    'description': new_description,
                    'camera_angle': new_camera,
                    'lens': new_lens,
                    'lighting': new_lighting
                })
    
    def _handle_scene_update(self, story: Dict, scene: Dict, scene_idx: int, updates: Dict):
        """Handle scene update"""
        # Update scene
        updated_scene = scene.copy()
        updated_scene.update(updates)
        
        # Save to database
        if self.services['db'].update_scene(story['id'], scene_idx, updated_scene):
            st.success("✅ Scene updated successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to update scene")
    
    def show_settings_page(self):
        """Enhanced settings page"""
        st.markdown("## ⚙️ Settings")
        
        # API Configuration
        self._render_api_settings()
        
        st.markdown("---")
        
        # Application Settings
        self._render_app_settings()
        
        st.markdown("---")
        
        # Database Management
        self._render_database_management()
        
        st.markdown("---")
        
        # About section
        self._render_about_section()
    
    def _render_api_settings(self):
        """Render API settings section"""
        st.markdown("### 🔑 API Configuration")
        st.info("💡 These API keys are required for full functionality. You can still use the app with limited features if some keys are missing.")
        
        with st.form("api_settings"):
            groq_key = st.text_input(
                "Groq API Key",
                value=os.getenv("GROQ_API_KEY", ""),
                type="password",
                help=f"Required for story generation and scene analysis. Get your key from: {Config.GROQ_CONSOLE_URL}"
            )
            
            gemini_key = st.text_input(
                "Gemini API Key",
                value=os.getenv("GEMINI_API_KEY", ""),
                type="password",
                help=f"Required for scene analysis and recommendations. Get your key from: {Config.GEMINI_API_URL}"
            )
            
            replicate_token = st.text_input(
                "Replicate API Token",
                value=os.getenv("REPLICATE_API_TOKEN", ""),
                type="password",
                help=f"Required for image and video generation. Get your token from: {Config.REPLICATE_URL}"
            )
            
            if st.form_submit_button("💾 Save API Keys", type="primary"):
                self._handle_api_key_update(groq_key, gemini_key, replicate_token)
    
    def _handle_api_key_update(self, groq_key: str, gemini_key: str, replicate_token: str):
        """Handle API key updates"""
        # Update environment variables
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if replicate_token:
            os.environ["REPLICATE_API_TOKEN"] = replicate_token
        
        st.success("✅ API keys updated! Please restart the app for changes to take effect.")
        
        # Test API connections
        self._test_api_connections(groq_key, gemini_key, replicate_token)
    
    def _test_api_connections(self, groq_key: str, gemini_key: str, replicate_token: str):
        """Test API connections"""
        st.markdown("#### 🧪 Testing API Connections...")
        
        # Test Groq
        if groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                st.success("✅ Groq API: Connected")
            except Exception as e:
                st.error(f"❌ Groq API: {str(e)}")
        else:
            st.warning("⚠️ Groq API: No key provided")
        
        # Test Gemini
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                st.success("✅ Gemini API: Connected")
            except Exception as e:
                st.error(f"❌ Gemini API: {str(e)}")
        else:
            st.warning("⚠️ Gemini API: No key provided")
        
        # Test Replicate
        if replicate_token:
            try:
                import replicate
                os.environ["REPLICATE_API_TOKEN"] = replicate_token
                st.success("✅ Replicate API: Connected")
            except Exception as e:
                st.error(f"❌ Replicate API: {str(e)}")
        else:
            st.warning("⚠️ Replicate API: No token provided")
    
    def _render_app_settings(self):
        """Render application settings"""
        st.markdown("### 🎛️ Application Settings")
        
        with st.form("app_settings"):
            default_genre = st.selectbox(
                "Default Genre",
                ["Adventure", "Drama", "Comedy", "Horror", "Sci-Fi", "Fantasy", "Romance", "Thriller", "Action"],
                index=0
            )
            
            image_style = st.selectbox(
                "Default Image Style",
                ["cinematic", "dramatic", "natural", "stylized", "noir"],
                index=0
            )
            
            auto_generate_images = st.checkbox(
                "Auto-generate images for new scenes",
                value=False,
                help="Automatically generate images when creating new scenes (requires Replicate API)"
            )
            
            max_scenes = st.slider(
                "Maximum scenes per story",
                min_value=Config.MIN_SCENES,
                max_value=Config.MAX_SCENES,
                value=4,
                help="Maximum number of scenes to create when splitting a story"
            )
            
            if st.form_submit_button("💾 Save Settings", type="primary"):
                self._handle_app_settings_update(default_genre, image_style, auto_generate_images, max_scenes)
    
    def _handle_app_settings_update(self, default_genre: str, image_style: str, auto_generate_images: bool, max_scenes: int):
        """Handle application settings update"""
        self.session_manager.set_session_value('default_genre', default_genre)
        self.session_manager.set_session_value('image_style', image_style)
        self.session_manager.set_session_value('auto_generate_images', auto_generate_images)
        self.session_manager.set_session_value('max_scenes', max_scenes)
        st.success("✅ Settings saved!")
    
    def _render_database_management(self):
        """Render database management section"""
        st.markdown("### 🗄️ Database Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            stories_count = len(self.services['db'].get_all_stories())
            st.metric("Total Stories", stories_count)
        
        with col2:
            if st.button("🗑️ Clear All Stories", type="secondary"):
                self._handle_database_clear()
        
        with col3:
            if st.button("📊 Export Database"):
                self._handle_database_export()
    
    def _handle_database_clear(self):
        """Handle database clearing with confirmation"""
        confirm_key = 'confirm_clear'
        if self.session_manager.get_session_value(confirm_key):
            self.services['db'].clear_all_stories()
            st.success("✅ All stories cleared!")
            self.session_manager.set_session_value(confirm_key, False)
            st.rerun()
        else:
            self.session_manager.set_session_value(confirm_key, True)
            st.warning("⚠️ Click again to confirm deletion of all stories!")
    
    def _handle_database_export(self):
        """Handle database export"""
        try:
            stories = self.services['db'].get_all_stories()
            stories_json = json.dumps(stories, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Database",
                data=stories_json,
                file_name=f"film_assist_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Error exporting database: {str(e)}")
    
    def _render_about_section(self):
        """Render about section"""
        st.markdown("### ℹ️ About")
        st.info(f"""
        **{Config.PAGE_TITLE} v2.0**
        
        This application helps filmmakers and storytellers create visual storyboards using AI.
        
        **Features:**
        - 🤖 AI-powered story generation
        - 🎬 Automatic scene splitting
        - 🖼️ Image generation for scenes
        - 🎥 Video creation from scenes
        - 📄 PDF export functionality
        - 📷 Professional camera recommendations
        - 🎨 Enhanced user interface
        - 📱 Responsive design
        
        **Requirements:**
        - Groq API key for story generation
        - Gemini API key for scene analysis
        - Replicate API token for image/video generation
        
        **Support:**
        For issues or questions, please check the documentation or contact support.
        """)
    
    def run(self):
        """Main application runner"""
        # Render header
        self.ui_components.render_header()
        
        # Render navigation and get current page
        current_page = self.render_navigation()
        
        # Route to appropriate page
        page_handlers = {
            PageType.HOME.value: self.show_home_page,
            PageType.CREATE_STORY.value: self.show_create_story_page,
            PageType.MY_STORIES.value: self.show_my_stories_page,
            PageType.STORYBOARD_VIEWER.value: self.show_storyboard_viewer,
            PageType.SETTINGS.value: self.show_settings_page
        }
        
        handler = page_handlers.get(current_page)
        if handler:
            handler()
        else:
            st.error(f"Unknown page: {current_page}")

def main():
    """Application entry point"""
    app = FilmAssistApp()
    app.run()

if __name__ == "__main__":
    main()