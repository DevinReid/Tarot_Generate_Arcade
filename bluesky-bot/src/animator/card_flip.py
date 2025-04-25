import arcade
import os
from typing import Dict
from PIL import Image
import numpy as np
import tempfile
import shutil
import cv2

class CardFlipAnimation:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.card_size = (300, 500)  # Match the CSS dimensions
        self.window = None
        self.card_front = None
        self.card_back = None
        self.background = None
        self.angle = 0
        self.flipping = False
        self.flip_duration = 2.0  # seconds
        self.current_time = 0
        self.frames = []
        self.recording = False
        self.temp_dir = None
        self.video_writer = None
        self.delay_counter = 0

    def setup(self):
        """Set up the animation window and load resources."""
        # Create a window
        self.window = arcade.Window(
            width=self.card_size[0] * 2,
            height=self.card_size[1] * 2,
            title="Card Flip Animation"
        )
        
        # Set background color
        arcade.set_background_color(arcade.color.WHITE)
        
        # Load textures
        self.load_textures()

    def load_textures(self, card_image_path: str = None):
        """Load all textures."""
        # Load background
        bg_path = os.path.join(self.assets_dir, "background.png")
        self.background = arcade.load_texture(bg_path)
        
        # Load back texture
        back_path = os.path.join(self.assets_dir, "cards", "back.png")
        self.card_back = arcade.load_texture(back_path)
        
        # Load front texture if provided
        if card_image_path:
            self.card_front = arcade.load_texture(card_image_path)
        else:
            # Default front texture
            front_path = os.path.join(self.assets_dir, "cards", "cups7.1.png")
            self.card_front = arcade.load_texture(front_path)

    def start_flip(self):
        """Start the card flip animation."""
        self.flipping = True
        self.current_time = 0
        self.angle = 0

    def update(self, delta_time: float):
        """Update the animation state."""
        if self.delay_counter < 15:  # Wait for 15 frames before starting
            self.delay_counter += 1
            return

        if not self.flipping:
            return

        self.current_time += delta_time
        progress = min(1.0, self.current_time / self.flip_duration)
        
        # Calculate rotation angle (0 to 180 degrees)
        self.angle = progress * 180
        
        if progress >= 1.0:
            self.flipping = False

    def draw(self):
        """Draw the current state of the animation."""
        # Clear the screen
        arcade.start_render()
        
        # Draw background
        arcade.draw_texture_rectangle(
            self.window.width // 2,
            self.window.height // 2,
            self.window.width,
            self.window.height,
            self.background
        )
        
        # Calculate center position
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        if self.angle < 90:
            # Draw back side
            scale = np.cos(np.radians(self.angle))
            arcade.draw_texture_rectangle(
                center_x, center_y,
                self.card_size[0] * scale,
                self.card_size[1],
                self.card_back,
                angle=0
            )
        else:
            # Draw front side
            scale = np.cos(np.radians(180 - self.angle))
            arcade.draw_texture_rectangle(
                center_x, center_y,
                self.card_size[0] * scale,
                self.card_size[1],
                self.card_front,
                angle=0
            )
        
        # If recording, capture the frame
        if self.recording:
            # Get the current frame as a numpy array
            frame = arcade.get_image()
            frame_array = np.array(frame)
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            # Ensure frame is in the correct format
            frame_bgr = cv2.resize(frame_bgr, (self.window.width, self.window.height))
            self.video_writer.write(frame_bgr)

    def start_recording(self, output_path: str, fps: int = 30):
        """Start recording the animation."""
        self.recording = True
        # Create video writer with H.264 codec
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Use H.264 codec
        self.video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (self.window.width, self.window.height),
            True  # isColor flag
        )
        
        if not self.video_writer.isOpened():
            raise RuntimeError("Could not open video writer")

    def stop_recording(self):
        """Stop recording."""
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def run(self, card_image_path: str = None, output_path: str = None):
        """Run the animation and optionally record it."""
        self.load_textures(card_image_path)
        self.setup()
        
        if output_path:
            self.start_recording(output_path)
        
        self.start_flip()
        
        def on_update(delta_time):
            self.update(delta_time)
            if not self.flipping and self.recording:
                self.window.close()
        
        def on_draw():
            self.draw()
        
        self.window.on_update = on_update
        self.window.on_draw = on_draw
        
        arcade.run()
        
        if output_path:
            self.stop_recording()

def create_card_flip_animation(card_image_path: str, output_path: str):
    """Create a card flip animation and save it as a video."""
    animation = CardFlipAnimation()
    animation.run(card_image_path, output_path)

if __name__ == "__main__":
    # Test the animation
    animation = CardFlipAnimation()
    animation.run(output_path="card_flip.mp4") 