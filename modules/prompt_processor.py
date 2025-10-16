"""
OpenCLI Prompt Processor
Handles intelligent input processing for file paths, images, and pasted text
"""

import re
from pathlib import Path
from typing import Tuple, Optional

class PromptProcessor:
    def __init__(self):
        # Image file extensions
        self.image_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
            '.webp', '.ico', '.tiff', '.tif', '.heic', '.heif'
        }

        # Video file extensions
        self.video_extensions = {
            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv',
            '.wmv', '.m4v', '.mpg', '.mpeg', '.3gp'
        }

        # Combined media extensions for pattern matching
        image_exts = '|'.join(ext[1:] for ext in self.image_extensions)
        video_exts = '|'.join(ext[1:] for ext in self.video_extensions)
        all_media_exts = f'{image_exts}|{video_exts}'

        # File path patterns - match everything from / to media extension
        # Use non-greedy match to get full path including spaces (escaped or not)
        self.unix_path_pattern = re.compile(rf'(/[^\n]+?\.({all_media_exts}))(?:\s|$)', re.IGNORECASE)
        self.windows_path_pattern = re.compile(rf'([A-Z]:\\[^\n]+?\.({all_media_exts}))(?:\s|$)', re.IGNORECASE)

        # Text block thresholds
        self.paste_length_threshold = 200
        self.paste_line_threshold = 3

        # Storage for original content
        self.image_paths = {}  # {placeholder_id: actual_path}
        self.pasted_texts = {}  # {placeholder_id: actual_text}
        self.placeholder_counter = 0

    def process_input(self, text: str) -> Tuple[str, dict]:
        """
        Process input text, replacing images/videos and long pastes with placeholders

        Returns:
            (display_text, metadata) where metadata contains original content
        """
        metadata = {
            'images': [],
            'videos': [],
            'pasted_texts': [],
            'original_text': text
        }

        display_text = text

        # 1. Process media paths (images and videos)
        display_text, image_metadata, video_metadata = self._process_media_paths(display_text)
        metadata['images'] = image_metadata
        metadata['videos'] = video_metadata

        # 2. Process large pasted text blocks
        display_text, paste_metadata = self._process_pasted_text(display_text)
        metadata['pasted_texts'] = paste_metadata

        return display_text, metadata

    def _process_media_paths(self, text: str) -> Tuple[str, list, list]:
        """Detect and replace image/video file paths with placeholders"""
        images = []
        videos = []

        # Find Unix-style paths
        unix_matches = self.unix_path_pattern.finditer(text)
        for match in unix_matches:
            path = match.group(1)
            path_obj = Path(path)
            ext = path_obj.suffix.lower()

            if ext in self.image_extensions:
                placeholder_id = self._get_next_placeholder_id()
                placeholder = f"[image #{placeholder_id}]"

                images.append({
                    'id': placeholder_id,
                    'path': path,
                    'placeholder': placeholder,
                    'exists': path_obj.exists()
                })
                text = text.replace(path, placeholder)

            elif ext in self.video_extensions:
                placeholder_id = self._get_next_placeholder_id()
                placeholder = f"[video #{placeholder_id}]"

                videos.append({
                    'id': placeholder_id,
                    'path': path,
                    'placeholder': placeholder,
                    'exists': path_obj.exists()
                })
                text = text.replace(path, placeholder)

        # Find Windows-style paths
        windows_matches = self.windows_path_pattern.finditer(text)
        for match in windows_matches:
            path = match.group(1)
            path_obj = Path(path)
            ext = path_obj.suffix.lower()

            if ext in self.image_extensions:
                placeholder_id = self._get_next_placeholder_id()
                placeholder = f"[image #{placeholder_id}]"

                images.append({
                    'id': placeholder_id,
                    'path': path,
                    'placeholder': placeholder,
                    'exists': path_obj.exists()
                })
                text = text.replace(path, placeholder)

            elif ext in self.video_extensions:
                placeholder_id = self._get_next_placeholder_id()
                placeholder = f"[video #{placeholder_id}]"

                videos.append({
                    'id': placeholder_id,
                    'path': path,
                    'placeholder': placeholder,
                    'exists': path_obj.exists()
                })
                text = text.replace(path, placeholder)

        return text, images, videos

    def _process_pasted_text(self, text: str) -> Tuple[str, list]:
        """Detect and collapse large pasted text blocks"""
        pasted_texts = []

        # Check if text meets paste criteria
        line_count = text.count('\n') + 1
        char_count = len(text)

        # Multi-line paste detection
        if line_count >= self.paste_line_threshold:
            placeholder_id = self._get_next_placeholder_id()
            placeholder = f"[pasted text #{placeholder_id}: {line_count} lines]"

            pasted_texts.append({
                'id': placeholder_id,
                'text': text,
                'placeholder': placeholder,
                'lines': line_count,
                'chars': char_count
            })

            return placeholder, pasted_texts

        # Long single-line paste detection
        if char_count >= self.paste_length_threshold and line_count == 1:
            placeholder_id = self._get_next_placeholder_id()
            # Show preview of first 50 chars
            preview = text[:50] + '...' if len(text) > 50 else text
            placeholder = f'[pasted text #{placeholder_id}: "{preview}"]'

            pasted_texts.append({
                'id': placeholder_id,
                'text': text,
                'placeholder': placeholder,
                'lines': line_count,
                'chars': char_count
            })

            return placeholder, pasted_texts

        return text, pasted_texts

    def _is_valid_image_path(self, path: str) -> bool:
        """Check if path has a valid image extension"""
        try:
            path_obj = Path(path)
            return path_obj.suffix.lower() in self.image_extensions
        except:
            return False

    def _get_next_placeholder_id(self) -> int:
        """Get next placeholder ID"""
        self.placeholder_counter += 1
        return self.placeholder_counter

    def get_original_text(self, processed_text: str, metadata: dict) -> str:
        """Reconstruct original text from processed text and metadata"""
        original = processed_text

        # Restore images
        for image in metadata.get('images', []):
            original = original.replace(image['placeholder'], image['path'])

        # Restore videos
        for video in metadata.get('videos', []):
            original = original.replace(video['placeholder'], video['path'])

        # Restore pasted texts
        for paste in metadata.get('pasted_texts', []):
            original = original.replace(paste['placeholder'], paste['text'])

        return original

    def format_display(self, text: str, metadata: dict) -> str:
        """Format text for display with metadata annotations"""
        lines = [text]

        # Add image info
        if metadata.get('images'):
            lines.append("\n📷 Images detected:")
            for img in metadata['images']:
                status = "✓ exists" if img['exists'] else "✗ not found"
                lines.append(f"  • {img['placeholder']}: {img['path']} ({status})")

        # Add video info
        if metadata.get('videos'):
            lines.append("\n🎥 Videos detected:")
            for vid in metadata['videos']:
                status = "✓ exists" if vid['exists'] else "✗ not found"
                lines.append(f"  • {vid['placeholder']}: {vid['path']} ({status})")

        # Add pasted text info
        if metadata.get('pasted_texts'):
            lines.append("\n📄 Pasted content detected:")
            for paste in metadata['pasted_texts']:
                lines.append(f"  • {paste['placeholder']}: {paste['chars']} chars, {paste['lines']} lines")

        return '\n'.join(lines)

    def should_process_as_paste(self, text: str) -> bool:
        """Quick check if text should be treated as a paste"""
        line_count = text.count('\n') + 1
        char_count = len(text)

        return (line_count >= self.paste_line_threshold or
                char_count >= self.paste_length_threshold)

    def is_likely_command(self, text: str) -> bool:
        """Check if text is likely a command (not a file path or paste)"""
        # Check if it's a file path FIRST (before checking for /)
        if self._is_likely_file_path(text):
            return False

        # Check if it's a paste
        if self.should_process_as_paste(text):
            return False

        # Commands start with / or are short single words
        if text.startswith('/'):
            return True

        # Short text without spaces could be command
        if len(text) < 50 and ' ' not in text.strip():
            return True

        return False

    def _is_likely_file_path(self, text: str) -> bool:
        """Check if text looks like a file path"""
        # Strip the text for checking
        text_clean = text.strip()

        # Check for file extension (strong indicator)
        if '.' in text_clean:
            # Get potential extension
            parts = text_clean.split('.')
            if len(parts) >= 2:
                ext = '.' + parts[-1].lower()
                # Check if it's a known extension (image or other)
                if ext in self.image_extensions:
                    return True
                # Common file extensions
                if ext in {'.txt', '.pdf', '.doc', '.docx', '.json', '.xml', '.csv', '.log'}:
                    return True

        # Unix absolute path with slashes
        if text_clean.startswith('/') and '/' in text_clean[1:]:
            return True

        # Windows path
        if len(text_clean) > 2 and text_clean[1] == ':' and text_clean[2] == '\\':
            return True

        # Path with multiple directory separators
        if text_clean.count('/') > 2 or text_clean.count('\\') > 2:
            return True

        return False

    def extract_images_from_metadata(self, metadata: dict) -> list:
        """Extract list of image paths from metadata"""
        images = []
        for img in metadata.get('images', []):
            if img['exists']:
                images.append(img['path'])
        return images

    def create_message_with_images(self, text: str, metadata: dict) -> dict:
        """Create a message dict with text and image paths for API"""
        message = {
            'text': self.get_original_text(text, metadata),
            'images': self.extract_images_from_metadata(metadata)
        }

        return message
