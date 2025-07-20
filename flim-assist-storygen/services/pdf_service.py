import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import requests
from PIL import Image
import io
import streamlit as st
import weasyprint

class PDFService:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "film_assist_pdfs"
        self.temp_dir.mkdir(exist_ok=True)

    def generate_storyboard_pdf(self, story_data: Dict[str, Any]) -> str:
        """Generate a PDF storyboard from story data"""
        
        try:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"storyboard_{story_data.get('title', 'untitled').replace(' ', '_')}_{timestamp}.pdf"
            pdf_path = self.temp_dir / pdf_filename

            # For Streamlit, we'll create a simple HTML-based PDF
            html_content = self._generate_html_content(story_data)
            
            # Write HTML file
            html_filename = pdf_filename.replace('.pdf', '.html')
            html_path = self.temp_dir / html_filename
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Try to convert HTML to PDF using weasyprint or similar
            try:
                weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
            except ImportError:
                # Fallback: just return the HTML file path
                st.warning("PDF generation requires weasyprint. Returning HTML version.")
                return str(html_path)
            
            return str(pdf_path)

        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            raise Exception(f"Failed to generate PDF: {str(e)}")

    def _generate_html_content(self, story_data: Dict[str, Any]) -> str:
        """Generate HTML content for the storyboard"""
        
        title = story_data.get('title', 'Untitled Story')
        theme = story_data.get('theme', '')
        genre = story_data.get('genre', '')
        scenes = story_data.get('scenes', [])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title} - Storyboard</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f8f9fa;
                }}
                
                .header {{
                    text-align: center;
                    background: linear-gradient(90deg, #f59e0b 0%, #ea580c 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                }}
                
                .story-info {{
                    background: white;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .scene {{
                    background: white;
                    border: 2px solid #fbbf24;
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin: 2rem 0;
                    page-break-inside: avoid;
                }}
                
                .scene-header {{
                    color: #92400e;
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 1rem;
                }}
                
                .scene-image {{
                    max-width: 100%;
                    height: 300px;
                    object-fit: cover;
                    border-radius: 5px;
                    margin-bottom: 1rem;
                }}
                
                .scene-description {{
                    background: #fffbeb;
                    padding: 1rem;
                    border-radius: 5px;
                    margin-bottom: 1rem;
                    line-height: 1.6;
                }}
                
                .tech-specs {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 1rem;
                    background: #f3f4f6;
                    padding: 1rem;
                    border-radius: 5px;
                }}
                
                .tech-spec {{
                    text-align: center;
                }}
                
                .tech-spec-label {{
                    font-weight: bold;
                    color: #374151;
                    margin-bottom: 0.5rem;
                }}
                
                .tech-spec-value {{
                    color: #6b7280;
                }}
                
                @media print {{
                    body {{ background: white; }}
                    .scene {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <h2>Storyboard</h2>
            </div>
            
            <div class="story-info">
                <h3>Story Information</h3>
                <p><strong>Theme:</strong> {theme}</p>
                <p><strong>Genre:</strong> {genre}</p>
                <p><strong>Total Scenes:</strong> {len(scenes)}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y")}</p>
            </div>
        """
        
        # Add scenes
        for i, scene in enumerate(scenes, 1):
            scene_html = self._generate_scene_html(scene, i)
            html_content += scene_html
        
        html_content += """
            <div style="text-align: center; margin-top: 2rem; color: #6b7280;">
                <p>Generated by Film Assist Storyboard Generator</p>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def _generate_scene_html(self, scene: Dict[str, Any], scene_number: int) -> str:
        """Generate HTML content for a single scene"""
        
        description = scene.get('description', 'No description available')
        camera_angle = scene.get('camera_angle', 'Not specified')
        lens = scene.get('lens', 'Not specified')
        lighting = scene.get('lighting', 'Not specified')
        image_url = scene.get('image_url', '')
        
        scene_html = f"""
        <div class="scene">
            <div class="scene-header">Scene {scene_number}</div>
            
            {f'<img src="{image_url}" alt="Scene {scene_number}" class="scene-image">' if image_url else ''}
            
            <div class="scene-description">
                <h4>Description</h4>
                <p>{description}</p>
            </div>
            
            <div class="tech-specs">
                <div class="tech-spec">
                    <div class="tech-spec-label">📷 Camera Angle</div>
                    <div class="tech-spec-value">{camera_angle}</div>
                </div>
                <div class="tech-spec">
                    <div class="tech-spec-label">🔍 Lens</div>
                    <div class="tech-spec-value">{lens}</div>
                </div>
                <div class="tech-spec">
                    <div class="tech-spec-label">💡 Lighting</div>
                    <div class="tech-spec-value">{lighting}</div>
                </div>
            </div>
        </div>
        """
        
        return scene_html

pdf_service = PDFService()
