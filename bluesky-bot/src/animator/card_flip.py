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
        self.flip_duration = 1  # seconds
        self.current_time = 0
        self.frames = []
        self.recording = False
        self.temp_dir = None
        self.video_writer = None
        self.delay_counter = 0
        self.show_text = True  # Show text immediately
        self.text_alpha = 255
        self.text_display_time = 0  # Track how long text has been shown
        self.initial_delay = 3.0  # 3 second delay before flip starts
        self.total_time = 0  # Track total elapsed time
        self.flip_complete_time = 0  # Track time since flip completed
        self.flip_completed = False  # Track if flip has completed
        self.animation_complete = False  # Track if entire animation is complete
        self.card_text_alpha = 0  # Alpha for card name text
        self.phase2_started = False  # Track if phase 2 has started
        self.phase2_time = 0  # Track time in phase 2
        self.phase2_duration = 1.0  # Duration of phase 2 animation
        self.card_scale = 1.0  # Current scale of the card
        self.card_y_offset = 0  # Current y offset of the card
        self.phase3_started = False  # Track if phase 3 has started
        self.phase3_time = 0  # Track time in phase 3
        self.description_alpha = 0  # Alpha for description text
        self.phase4_started = False  # Track if phase 4 has started
        self.phase4_time = 0  # Track time in phase 4
        self.fade_out_alpha = 255  # Alpha for fade out
        self.cta_alpha = 0  # Alpha for CTA text

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
        
        # Load font
        font_path = os.path.join(self.assets_dir, "fonts", "OldSchoolAdventures-42j9.ttf")
        arcade.load_font(font_path)
        
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
        self.total_time += delta_time
        
        # Don't start flipping until initial delay is over
        if self.total_time < self.initial_delay:
            # Start fading text after 2 seconds
            if self.show_text and self.total_time > 2.0:
                self.text_alpha = max(0, self.text_alpha - (delta_time * 255))  # Fade over 1 second
            return
            
        if not self.flipping and not self.flip_completed:
            self.flipping = True
            self.current_time = 0
            
        if self.flipping:
            self.current_time += delta_time
            progress = min(1.0, self.current_time / self.flip_duration)
            
            # Calculate rotation angle (0 to 180 degrees)
            self.angle = progress * 180
            
            if progress >= 1.0:
                self.flipping = False
                self.flip_completed = True
                self.flip_complete_time = 0
                self.angle = 180  # Keep card fully flipped
        elif self.flip_completed and not self.phase2_started:
            self.flip_complete_time += delta_time
            # Fade in card name text over 0.5 seconds
            self.card_text_alpha = min(255, self.card_text_alpha + (delta_time * 510))  # 510 = 255/0.5
            
            # Start phase 2 after 2 seconds of showing completed flip
            if self.flip_complete_time >= 2.0:
                self.phase2_started = True
                self.phase2_time = 0
        elif self.phase2_started and not self.phase3_started:
            self.phase2_time += delta_time
            progress = min(1.0, self.phase2_time / self.phase2_duration)
            
            # Animate scale from 1.0 to 0.5
            self.card_scale = 1.0 - (progress * 0.5)
            
            # Animate y offset from 0 to half screen height
            target_y_offset = self.window.height // 5
            self.card_y_offset = progress * target_y_offset
            
            # Start phase 3 after phase 2 completes
            if self.phase2_time >= self.phase2_duration:
                self.phase3_started = True
                self.phase3_time = 0
        elif self.phase3_started and not self.phase4_started:
            self.phase3_time += delta_time
            
            # Fade in description text over 0.5 seconds
            if self.phase3_time < 0.5:
                self.description_alpha = min(255, self.description_alpha + (delta_time * 510))
            
            # Start phase 4 after 6 seconds of showing description
            if self.phase3_time >= 6.0:
                self.phase4_started = True
                self.phase4_time = 0
        elif self.phase4_started and not self.animation_complete:
            self.phase4_time += delta_time
            
            # Fade out everything over 0.5 seconds
            if self.phase4_time < 0.5:
                self.fade_out_alpha = max(0, self.fade_out_alpha - (delta_time * 510))
                self.card_text_alpha = self.fade_out_alpha
                self.description_alpha = self.fade_out_alpha
            
            # Fade in CTA text after fade out completes
            if self.phase4_time >= 0.5:
                self.cta_alpha = min(255, self.cta_alpha + (delta_time * 510))
            
            # End animation after 3 seconds of showing CTA
            if self.phase4_time >= 3.5:  # 0.5s fade out + 3s CTA
                self.animation_complete = True
                if self.recording:
                    self.window.close()

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
        center_y = self.window.height // 2 + self.card_y_offset  # Apply y offset
        
        # Draw card if not faded out
        if self.fade_out_alpha > 0:
            if self.angle < 90:
                # Draw back side
                scale = np.cos(np.radians(self.angle)) * self.card_scale
                arcade.draw_texture_rectangle(
                    center_x, center_y,
                    self.card_size[0] * scale,
                    self.card_size[1] * self.card_scale,
                    self.card_back,
                    angle=0,
                    alpha=int(self.fade_out_alpha)  # Add alpha to card
                )
            else:
                # Draw front side
                scale = np.cos(np.radians(180 - self.angle)) * self.card_scale
                arcade.draw_texture_rectangle(
                    center_x, center_y,
                    self.card_size[0] * scale,
                    self.card_size[1] * self.card_scale,
                    self.card_front,
                    angle=0,
                    alpha=int(self.fade_out_alpha)  # Add alpha to card
                )
        
        # Draw text if visible (after the card)
        if self.show_text and self.text_alpha > 0 and self.fade_out_alpha > 0:
            # Create semi-transparent background for text
            arcade.draw_rectangle_filled(
                self.window.width // 2,
                center_y + self.card_size[1] // 2 + 50,  # Position above card
                self.window.width,
                60,  # Smaller height for smaller text
                (0, 0, 0, int(self.text_alpha * 0.5))
            )
            # Draw text in white with opacity
            opacity = int(self.text_alpha)
            arcade.draw_text(
                "Daily Tarot",
                self.window.width // 2,
                center_y + self.card_size[1] // 2 + 50,  # Position above card
                (255, 255, 255, opacity),  # White with opacity
                font_size=36,  # Smaller font size
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
            )

        # Draw card name and orientation after flip completes
        if self.flip_completed and self.card_text_alpha > 0 and self.fade_out_alpha > 0:
            # Calculate text position that scales with card size
            text_offset = (self.card_size[1] * self.card_scale) // 2
            
            # Draw card name
            arcade.draw_text(
                "Seven of Cups",
                self.window.width // 2,
                center_y + text_offset + 90,  # Position above card, scaled with card size
                (255, 255, 255, int(self.card_text_alpha)),  # White with fade in
                font_size=32,  # Slightly smaller font size
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
            )
            # Draw orientation
            arcade.draw_text(
                "Upright",
                self.window.width // 2,
                center_y + text_offset + 40,  # Position below card name, scaled with card size
                (255, 255, 255, int(self.card_text_alpha)),  # White with fade in
                font_size=28,  # Even smaller font size for orientation
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
            )

        # Draw description text in phase 3
        if self.phase3_started and self.description_alpha > 0 and self.fade_out_alpha > 0:
            # Draw description text
            description = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."""
            arcade.draw_text(
                description,
                self.window.width // 2,
                self.window.height // 2 - 180,
                (255, 255, 255, int(self.description_alpha)),
                font_size=16,
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures",
                width=self.window.width - 150,  # Width for text wrapping
                align="center"  # Center align text
            )

        # Draw CTA text in phase 4
        if self.phase4_started and self.cta_alpha > 0:
            # Draw each line of CTA text separately
            base_y = self.window.height // 2 + 100
            line_height = 60  # Space between lines
            
            # Draw "Visit"
            arcade.draw_text(
                "Visit",
                self.window.width // 2,
                base_y + line_height+20,
                (255, 255, 255, int(self.cta_alpha)),
                font_size=48,
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
            )
            
            # Draw "Mama Nyah"
            arcade.draw_text(
                "Mama Nyah",
                self.window.width // 2,
                base_y,
                (255, 255, 255, int(self.cta_alpha)),
                font_size=48,
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
            )
            
            # Draw "Today"
            arcade.draw_text(
                "Today",
                self.window.width // 2,
                base_y - line_height-20,
                (255, 255, 255, int(self.cta_alpha)),
                font_size=48,
                anchor_x="center",
                anchor_y="center",
                font_name="Old School Adventures"
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
        
        def on_update(delta_time):
            self.update(delta_time)
        
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