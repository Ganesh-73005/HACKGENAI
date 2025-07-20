import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st

class DatabaseService:
    def __init__(self):
        self.data_file = "stories_database.json"
        self.stories = self._load_stories()

    def _load_stories(self) -> List[Dict[str, Any]]:
        """Load stories from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.warning(f"Error loading stories: {e}")
        return []

    def _save_stories(self):
        """Save stories to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.stories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving stories: {e}")

    def create_story(self, story_data: Dict[str, Any]) -> str:
        """Create a new story"""
        story_id = f"story_{len(self.stories) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        story = {
            'id': story_id,
            'title': story_data.get('title', ''),
            'theme': story_data.get('theme', ''),
            'genre': story_data.get('genre', ''),
            'content': story_data.get('content', ''),
            'scenes': story_data.get('scenes', []),
            'created_at': story_data.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }
        
        self.stories.append(story)
        self._save_stories()
        
        return story_id

    def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a story by ID"""
        for story in self.stories:
            if story['id'] == story_id:
                return story
        return None

    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Get all stories"""
        return self.stories.copy()

    def get_recent_stories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent stories"""
        sorted_stories = sorted(
            self.stories, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        return sorted_stories[:limit]

    def update_story(self, story_id: str, updates: Dict[str, Any]) -> bool:
        """Update a story"""
        for i, story in enumerate(self.stories):
            if story['id'] == story_id:
                story.update(updates)
                story['updated_at'] = datetime.now().isoformat()
                self.stories[i] = story
                self._save_stories()
                return True
        return False

    def update_scene(self, story_id: str, scene_index: int, scene_data: Dict[str, Any]) -> bool:
        """Update a specific scene"""
        story = self.get_story(story_id)
        if story and 0 <= scene_index < len(story.get('scenes', [])):
            story['scenes'][scene_index] = scene_data
            story['updated_at'] = datetime.now().isoformat()
            return self.update_story(story_id, story)
        return False

    def update_scene_image(self, story_id: str, scene_index: int, image_url: str, metadata: Dict[str, Any]) -> bool:
        """Update scene image"""
        story = self.get_story(story_id)
        if story and 0 <= scene_index < len(story.get('scenes', [])):
            story['scenes'][scene_index]['image_url'] = image_url
            story['scenes'][scene_index]['generation_metadata'] = metadata
            story['updated_at'] = datetime.now().isoformat()
            return self.update_story(story_id, story)
        return False

    def delete_story(self, story_id: str) -> bool:
        """Delete a story"""
        for i, story in enumerate(self.stories):
            if story['id'] == story_id:
                del self.stories[i]
                self._save_stories()
                return True
        return False

    def clear_all_stories(self):
        """Clear all stories"""
        self.stories = []
        self._save_stories()
