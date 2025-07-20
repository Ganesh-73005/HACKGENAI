import os
import json
import re
from typing import List, Dict, Any, Optional
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class StoryService:
    def __init__(self):
        
        
        
        # Initialize Groq
        self.groq_client = Groq(api_key="")
        
        # Initialize Gemini
        genai.configure(api_key="")
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        

    def generate_story_from_prompt(self, prompt: str, theme: str, genre: str = None) -> str:
        """Generate a complete story from a prompt"""
        
        if not self.groq_client:
            return self._generate_fallback_story(prompt, theme, genre)

        system_prompt = f"""
        You are a professional screenwriter. Generate a compelling story based on the user's prompt.
        
        Requirements:
        - Theme: {theme}
        - Genre: {genre or 'General'}
        - Length: 800-1200 words
        - Structure: Clear beginning, middle, and end
        - Visual: Include vivid descriptions suitable for storyboarding
        - Cinematic: Write with visual storytelling in mind
        
        Make the story engaging and suitable for visual adaptation.
        """

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9,
            )
            
            story = completion.choices[0].message.content
            if not story or len(story.strip()) < 100:
                raise Exception("Generated story is too short")
            
            return story
            
        except Exception as e:
            st.warning(f"Groq API error: {e}. Using fallback story generation.")
            return self._generate_fallback_story(prompt, theme, genre)

    def split_story_into_scenes(self, story_text: str, theme: str, genre: str = None) -> List[Dict[str, Any]]:
        """Split story into 3-4 scenes with technical details"""
        
        if not self.groq_client:
            return self._create_fallback_scenes(story_text, theme, genre)

        system_prompt = f"""
        You are a professional film director and cinematographer. Split the following story into 3-4 cinematic scenes.
        
        For each scene, provide:
        1. Scene description (2-3 sentences, visual and action-focused)
        2. Camera angle (e.g., "Wide shot", "Close-up", "Medium shot", "Over-the-shoulder")
        3. Lens recommendation (e.g., "50mm", "24mm wide-angle", "85mm portrait", "200mm telephoto")
        4. Lighting setup (e.g., "Natural daylight", "Golden hour", "Low-key dramatic", "High-key bright")
        5. Scene number (1, 2, 3, or 4)

        Theme: {theme}
        Genre: {genre or 'General'}

        Return the response as a JSON array with this exact structure:
        [
            {{
                "scene_number": 1,
                "description": "Scene description here",
                "camera_angle": "Camera angle here",
                "lens": "Lens here",
                "lighting": "Lighting here"
            }}
        ]

        Make sure each scene is visually distinct and cinematically interesting.
        """

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Story to split into scenes:\n\n{story_text}"}
                ],
                temperature=0.6,
                max_tokens=1500,
                top_p=0.9,
            )
            
            response_text = completion.choices[0].message.content
            print(response_text)
            # Try to extract JSON from the response
            try:
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    scenes_data = json.loads(json_match.group())
                else:
                    scenes_data = json.loads(response_text)
                
                if not scenes_data or len(scenes_data) == 0:
                    raise Exception("No scenes generated")
                    
                return scenes_data
                
            except json.JSONDecodeError:
                return self._parse_scenes_manually(response_text)
                
        except Exception as e:
            st.warning(f"Scene splitting error: {e}. Using fallback method.")
            return self._create_fallback_scenes(story_text, theme, genre)

    def analyze_previous_scene(self, prev_scene_text: str, prev_scene_image_url: str = None) -> Dict[str, str]:
        """Analyze previous scene to recommend next scene's technical aspects"""
        
        if not self.gemini_model:
            return {
                "camera_angle": "Medium shot",
                "lens": "50mm",
                "lighting": "Natural daylight"
            }

        try:
            prompt = f"""
            Analyze this previous scene and recommend camera angle, lens, and lighting for the NEXT scene.

            Previous scene: {prev_scene_text}

            Provide recommendations in this exact format:
            Camera Angle: [recommendation]
            Lens: [recommendation]  
            Lighting: [recommendation]
            """

            response = self.gemini_model.generate_content(prompt)
            response_text = response.text

            # Parse the response
            recommendations = {}
            for line in response_text.split('\n'):
                if 'Camera Angle:' in line:
                    recommendations["camera_angle"] = line.split('Camera Angle:')[1].strip()
                elif 'Lens:' in line:
                    recommendations["lens"] = line.split('Lens:')[1].strip()
                elif 'Lighting:' in line:
                    recommendations["lighting"] = line.split('Lighting:')[1].strip()

            # Ensure we have all required fields
            if not recommendations.get("camera_angle"):
                recommendations["camera_angle"] = "Medium shot"
            if not recommendations.get("lens"):
                recommendations["lens"] = "50mm"
            if not recommendations.get("lighting"):
                recommendations["lighting"] = "Natural daylight"

            return recommendations

        except Exception as e:
            return {
                "camera_angle": "Medium shot",
                "lens": "50mm", 
                "lighting": "Natural daylight"
            }

    def _generate_fallback_story(self, prompt: str, theme: str, genre: str = None) -> str:
        """Generate a fallback story when AI is not available"""
        return f"""
        {theme} Story: {prompt}
        
        In a world where {theme.lower()} takes center stage, our story begins with an intriguing premise. 
        The protagonist finds themselves in a situation that challenges their understanding of the world around them.
        
        As the narrative unfolds, we witness a series of events that build tension and develop character. 
        Each moment is carefully crafted to advance the plot while maintaining the {genre or 'dramatic'} tone 
        that defines this particular story.
        
        The middle section introduces complications and obstacles that our main character must overcome. 
        These challenges serve to test their resolve and reveal deeper aspects of their personality, 
        creating opportunities for growth and transformation.
        
        The climax brings all story elements together in a powerful convergence of action and emotion. 
        Here, the themes of {theme.lower()} are most prominently displayed, creating a satisfying 
        resolution that speaks to the heart of the narrative.
        
        In the conclusion, we see how the journey has changed our protagonist and what lessons 
        have been learned. The story ends with a sense of completion while leaving room for 
        reflection on the deeper meanings embedded within the tale.
        """

    def _create_fallback_scenes(self, story_text: str, theme: str, genre: str = None) -> List[Dict[str, Any]]:
        """Create fallback scenes when AI processing fails"""
        paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
        
        scenes = []
        camera_angles = ["Wide shot", "Medium shot", "Close-up", "Over-the-shoulder"]
        lenses = ["24mm wide-angle", "50mm", "85mm portrait", "135mm telephoto"]
        lighting = ["Natural daylight", "Golden hour", "Dramatic lighting", "Soft lighting"]
        
        num_scenes = min(4, max(3, len(paragraphs)))
        paragraphs_per_scene = max(1, len(paragraphs) // num_scenes)
        
        for i in range(num_scenes):
            start_idx = i * paragraphs_per_scene
            end_idx = start_idx + paragraphs_per_scene if i < num_scenes - 1 else len(paragraphs)
            
            scene_text = ' '.join(paragraphs[start_idx:end_idx])
            if not scene_text:
                scene_text = f"Scene {i+1} of the {theme.lower()} story unfolds with dramatic tension."
            
            scenes.append({
                "scene_number": i + 1,
                "description": scene_text[:300] + "..." if len(scene_text) > 300 else scene_text,
                "camera_angle": camera_angles[i % len(camera_angles)],
                "lens": lenses[i % len(lenses)],
                "lighting": lighting[i % len(lighting)]
            })
        
        return scenes

    def _parse_scenes_manually(self, response_text: str) -> List[Dict[str, Any]]:
        """Fallback method to parse scenes manually"""
        scenes = []
        lines = response_text.split('\n')
        current_scene = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'scene' in line.lower() and any(char.isdigit() for char in line):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {"scene_number": len(scenes) + 1}
            elif 'description' in line.lower():
                current_scene["description"] = line.split(':', 1)[-1].strip()
            elif 'camera' in line.lower():
                current_scene["camera_angle"] = line.split(':', 1)[-1].strip()
            elif 'lens' in line.lower():
                current_scene["lens"] = line.split(':', 1)[-1].strip()
            elif 'lighting' in line.lower():
                current_scene["lighting"] = line.split(':', 1)[-1].strip()
        
        if current_scene:
            scenes.append(current_scene)
        
        if not scenes:
            scenes = [{
                "scene_number": 1,
                "description": "Opening scene establishing the setting and main character",
                "camera_angle": "Wide shot",
                "lens": "24mm wide-angle",
                "lighting": "Natural daylight"
            }]
        
        return scenes
