from atproto import Client, models
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BlueskyPoster:
    def __init__(self):
        self.client = Client()
        self.handle = os.getenv('BLUESKY_HANDLE')
        self.password = os.getenv('BLUESKY_PASSWORD')
        
        if not self.handle or not self.password:
            raise ValueError("Bluesky credentials not found in environment variables")
        
        self.client.login(self.handle, self.password)

    def _upload_media(self, video_path: str) -> Optional[models.AppBskyEmbedExternal.Main]:
        """Upload video to Bluesky and return the media reference."""
        try:
            # Note: Bluesky currently only supports images, not videos
            # We'll need to convert the video to an image first
            # For now, we'll use the first frame of the video
            from moviepy.editor import VideoFileClip
            import tempfile
            
            # Extract first frame
            with VideoFileClip(video_path) as video:
                frame = video.get_frame(0)
                
                # Save frame as temporary image
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                    from PIL import Image
                    Image.fromarray(frame).save(temp_img.name)
                    
                    # Upload image
                    with open(temp_img.name, 'rb') as f:
                        upload = self.client.com.atproto.repo.upload_blob(f)
                        
                    # Clean up
                    os.unlink(temp_img.name)
                    
                    return models.AppBskyEmbedExternal.Main(
                        external=models.AppBskyEmbedExternal.External(
                            uri=upload.blob.ref.link,
                            title="Daily Tarot Reading",
                            description="Your daily tarot card reading"
                        )
                    )
        except Exception as e:
            print(f"Error uploading media: {e}")
            return None

    def post_reading(self, reading_data: dict, video_path: str) -> bool:
        """Post the reading to Bluesky."""
        try:
            # Create post text
            post_text = f"""🔮 Daily Tarot Reading for {reading_data['date']} 🔮

Card: {reading_data['card']} ({reading_data['position']})

{reading_data['reading']}

#tarot #dailytarot #tarotreading"""

            # Upload media
            media = self._upload_media(video_path)
            
            # Create post
            if media:
                self.client.send_post(
                    text=post_text,
                    embed=media
                )
            else:
                self.client.send_post(text=post_text)
            
            return True
            
        except Exception as e:
            print(f"Error posting to Bluesky: {e}")
            return False 