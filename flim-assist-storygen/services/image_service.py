 # API version from your example
import os
import requests
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

class ImageService:
    def __init__(self):
        self.runway_api_key = ""  # Replace with your actual Runway API key
        self.runway_api_url = "https://api.dev.runwayml.com/v1"  # Development API URL
        self.api_version = "2024-11-06" 
        self.task_poll_interval = 5  # seconds between polling attempts
        self.max_poll_attempts = 60  # max attempts before timeout (5 mins)

    def generate_scene_image(
    self,
    prompt: str,
    style: str = "cinematic",
    aspect_ratio: str = "16:9",
    reference_images: Optional[List[str]] = None,
    scene_metadata: Optional[Dict[str, str]] = None,
    previous_scene: Optional[Dict] = None
) -> Dict[str, Any]:
     """Generate an image for a scene using Runway's text_to_image API"""
     print("\n=== Starting image generation ===")
     print(f"Prompt: {prompt}")
     print(f"Style: {style}")
     print(f"Aspect Ratio: {aspect_ratio}")
     print(f"Reference Images: {reference_images}")
    
     try:
        # Convert aspect ratio to Runway format
        resolution = self._convert_aspect_ratio_to_resolution(aspect_ratio)
        print(f"Converted aspect ratio {aspect_ratio} to resolution: {resolution}")

        # Prepare reference images - include previous scene if available
        runway_references = []
        if reference_images:
            print(f"Processing {len(reference_images)} reference images")
            for idx, img_url in enumerate(reference_images[:3]):  # Max 3 references
                runway_references.append({
                    "uri": img_url,
                    "tag": f"reference_{idx+1}"
                })
                print(f"Added reference image {idx+1}: {img_url}")
        
        # If no references but we have a previous scene, use its image
        if not runway_references and previous_scene and previous_scene.get('image_url'):
            runway_references.append({
                "uri": previous_scene['image_url'],
                "tag": "previous_scene"
            })
            print(f"Using previous scene image as reference: {previous_scene['image_url']}")

        # Prepare the request payload
        payload = {
            "promptText": prompt,
            "ratio": resolution,
            "seed": int(datetime.now().timestamp()) % 4294967295,
            "model": "gen4_image",
            "referenceImages": runway_references,
            "contentModeration": {
                "publicFigureThreshold": "auto"
            }
        }
        
        if style:
            payload["style"] = style
            print(f"Added style to payload: {style}")
        
        # Add scene metadata if available
        if scene_metadata:
            payload["scene_metadata"] = scene_metadata
            print(f"Added scene metadata: {scene_metadata}")

        headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": self.api_version
        }

        print("\nCreating generation task...")
        response = requests.post(
            f"{self.runway_api_url}/text_to_image",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            error_msg = f"API error: {response.status_code} - {response.text}"
            print(f"Error: {error_msg}")
            st.error(error_msg)
            return self._generate_placeholder_image(prompt)

        task_id = response.json().get("id")
        if not task_id:
            print("No task ID in response")
            st.warning("No task ID returned from Runway API")
            return self._generate_placeholder_image(prompt)

        print(f"Task created with ID: {task_id}")
        
        # Poll for task completion
        image_url = self._poll_task_result(task_id)
        if not image_url:
            return self._generate_placeholder_image(prompt)

        generation_metadata = {
            "model": "gen4_image",
            "prompt": prompt,
            "style": style,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "reference_images": runway_references,
            "task_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "previous_scene": previous_scene.get('image_url') if previous_scene else None
        }

        return {
            "image_url": image_url,
            "generation_metadata": generation_metadata
        }

     except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        print(f"Exception: {error_msg}")
        st.error(error_msg)
        return self._generate_placeholder_image(prompt)

    def _poll_task_result(self, task_id: str) -> Optional[str]:
        """Poll task status until completion and return image URL"""
        print(f"\nPolling task {task_id} for completion...")
        
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
                    print(f"Polling attempt {attempt+1} failed: {response.status_code}")
                    time.sleep(self.task_poll_interval)
                    continue
                
                task_data = response.json()
                status = task_data.get("status")
                
                print(f"Polling attempt {attempt+1}: Status = {status}")
                
                if status == "SUCCEEDED":
                    output = task_data.get("output")
                    if output and isinstance(output, list) and len(output) > 0:
                        image_url = output[0]
                        print(f"Generation succeeded! Image URL: {image_url}")
                        return image_url
                    return None
                elif status in ["FAILED", "CANCELLED"]:
                    print(f"Task failed with status: {status}")
                    return None
                
                time.sleep(self.task_poll_interval)
                
            except Exception as e:
                print(f"Error during polling attempt {attempt+1}: {str(e)}")
                time.sleep(self.task_poll_interval)
        
        print(f"Task polling timed out after {self.max_poll_attempts} attempts")
        return None

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

    def _generate_placeholder_image(self, prompt: str) -> Dict[str, Any]:
        """Generate a placeholder when image generation fails"""
        placeholder_url = f"https://picsum.photos/1920/1080?random={hash(prompt) % 1000}"
        
        return {
            "image_url": placeholder_url,
            "generation_metadata": {
                "model": "placeholder",
                "prompt": prompt,
                "generated_at": datetime.now().isoformat(),
                "note": "Placeholder image - API not available"
            }
        }

    def save_image_to_disk(self, image_url: str, filename: str) -> str:
        """Save image from URL to disk"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return None