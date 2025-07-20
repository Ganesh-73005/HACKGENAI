import os
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import requests
class VideoService:
    def __init__(self):
        self.runway_api_key = ""  # Replace with your actual Runway API key
        self.runway_api_url = "https://api.runwayml.com/v1"  # Runway API URL
        self.api_version = "2024-11-06" 
        self.task_poll_interval = 5  # seconds between polling attempts
        self.max_poll_attempts = 60  # max attempts before timeout (5 mins)

    def generate_scene_video(
        self,
        scenes: List[Dict[str, Any]],
        duration: int = 5,
        fps: int = 24,
        resolution: str = "1080p",
        aspect_ratio: str = "16:9",
        camera_fixed: bool = False,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a video from multiple scenes using RunwayML's Gen4 Turbo"""
        
        try:
            # Create a comprehensive video prompt from scenes
            video_prompt = self._create_video_prompt(scenes)
            
            # Get the first scene's image as input if available
            input_image = self._get_input_image(scenes)
            
            if not input_image:
                raise ValueError("No input image found in scenes")
            
            # Convert aspect ratio to Runway format
            runway_ratio = self._convert_aspect_ratio_to_resolution(aspect_ratio)
            
            # Prepare the request payload
            payload = {
                "model": "gen3a_turbo",
                "promptImage": input_image,
                "promptText": video_prompt,
                "ratio": runway_ratio,
                "seed": seed if seed else int(datetime.now().timestamp()) % 4294967295,
                "contentModeration": {
                         "publicFigureThreshold": "auto"
    }
            }
            
            headers = {
                "Authorization": f"Bearer {self.runway_api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": '2024-11-06'
            }

            # Create the video generation task
            response = requests.post(
                f"{self.runway_api_url}/image_to_video",
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                error_msg = f"API error: {response.status_code} - {response.text}"
                st.error(error_msg)
                return self._generate_placeholder_video(scenes)

            task_id = response.json().get("id")
            if not task_id:
                st.warning("No task ID returned from Runway API")
                return self._generate_placeholder_video(scenes)

            # Poll for task completion
            video_url = self._poll_task_result(task_id)
            if not video_url:
                return self._generate_placeholder_video(scenes)

            generation_metadata = {
                "model": "gen4_turbo",
                "prompt": video_prompt,
                "scenes_count": len(scenes),
                "duration": duration,
                "fps": fps,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "input_image_used": input_image,
                "generated_at": datetime.now().isoformat(),
                "task_id": task_id
            }

            return {
                "video_url": video_url,
                "generation_metadata": generation_metadata
            }

        except Exception as e:
            st.error(f"Error generating video: {e}")
            return self._generate_placeholder_video(scenes)

    def _poll_task_result(self, task_id: str) -> Optional[str]:
        """Poll task status until completion and return video URL"""
        headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "X-Runway-Version": self.api_version
        }
        
        for attempt in range(self.max_poll_attempts):
            try:
                response = requests.get(
                    f"{self.runway_api_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    time.sleep(self.task_poll_interval)
                    continue
                
                task_data = response.json()
                status = task_data.get("status")
                
                if status == "SUCCEEDED":
                    output = task_data.get("output")
                    if output and isinstance(output, list) and len(output) > 0:
                        return output[0]
                    return None
                elif status in ["FAILED", "CANCELLED"]:
                    return None
                
                time.sleep(self.task_poll_interval)
                
            except Exception as e:
                time.sleep(self.task_poll_interval)
        
        return None

    def _create_video_prompt(self, scenes: List[Dict[str, Any]]) -> str:
        """Create a comprehensive video prompt from multiple scenes"""
        if not scenes:
            return "A cinematic sequence with smooth transitions"
        
        video_prompt = "A cinematic sequence showing: "
        scene_prompts = []
        
        for i, scene in enumerate(scenes):
            description = scene.get("description", f"Scene {i+1}")
            camera_angle = scene.get("camera_angle", "")
            lighting = scene.get("lighting", "")
            
            scene_text = description
            if camera_angle:
                scene_text += f" with {camera_angle.lower()} camera angle"
            if lighting:
                scene_text += f" in {lighting.lower()} lighting"
            
            scene_prompts.append(scene_text)
        
        if len(scene_prompts) == 1:
            video_prompt += scene_prompts[0]
        else:
            video_prompt += scene_prompts[0]
            for scene_prompt in scene_prompts[1:]:
                video_prompt += f", then {scene_prompt}"
        
        video_prompt += ". Smooth transitions, professional cinematography, high quality."
        return video_prompt

    def _convert_aspect_ratio_to_resolution(self, aspect_ratio: str) -> str:
        """Convert aspect ratio to resolution format expected by Runway API"""
        ratio_map = {
            "16:9": "1920:1080",
            "4:3": "1600:1200", 
            "1:1": "1024:1024",
            "9:16": "1080:1920",
            "3:4": "1200:1600",
            "21:9": "2560:1080"
        }
        return ratio_map.get(aspect_ratio, "1920:1080")

    def _get_input_image(self, scenes: List[Dict[str, Any]]) -> Optional[str]:
        """Get the first available image from scenes as input"""
        for scene in scenes:
            image_url = scene.get("image_url")
            if image_url and image_url.startswith("http"):
                return image_url
        return None

    def _validate_duration(self, duration: int) -> int:
        """Validate and adjust duration to allowed values"""
        return max(2, min(10, duration))  # Runway typically allows 2-10 second videos

    def _validate_resolution(self, resolution: str) -> str:
        """Validate resolution to allowed values"""
        allowed_resolutions = ["480p", "720p", "1080p"]
        return resolution if resolution in allowed_resolutions else "1080p"

    def _validate_aspect_ratio(self, aspect_ratio: str) -> str:
        """Validate aspect ratio to allowed values"""
        allowed_ratios = ["16:9", "4:3", "1:1", "9:16", "3:4", "21:9"]
        return aspect_ratio if aspect_ratio in allowed_ratios else "16:9"

    def _generate_placeholder_video(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a placeholder when video generation fails"""
        return {
            "video_url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
            "generation_metadata": {
                "model": "placeholder",
                "scenes_count": len(scenes),
                "generated_at": datetime.now().isoformat(),
                "note": "Placeholder video - API not available"
            }
        }

    def save_video_to_disk(self, video_url: str, filename: str) -> str:
        """Save video from URL to disk"""
        try:
            import requests
            response = requests.get(video_url)
            response.raise_for_status()
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
        except Exception as e:
            st.error(f"Error saving video: {e}")
            return None