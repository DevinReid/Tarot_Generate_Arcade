import arcade
import os
from typing import Dict
from PIL import Image
import numpy as np
import tempfile
import shutil
import cv2
import threading
import sounddevice as sd
import wave
import queue
import time
import subprocess
import textwrap
from text_utility import (
    draw_outlined_line,
    set_paragraph_typing,
    typewriter_lines,
    update_typing_effect,
    reset_typing_state
)
from reading_generator import ReadingGenerator
from card_selector import CardSelector

class CardFlipAnimation(arcade.View):
    def __init__(self, assets_dir: str = "assets"):
        super().__init__()
        self.assets_dir = assets_dir
        self.card_size = (300, 500)  # Match the CSS dimensions
        self.card_front = None
        self.card_back = None
        self.background = None
        self.angle = 0
        self.flipping = False
        self.flip_duration = 4.0  # Increased from 2.0 seconds
        self.current_time = 0
        self.frames = []
        self.recording = False
        self.temp_dir = None
        self.video_writer = None
        self.delay_counter = 0
        self.show_text = True  # Show text immediately
        self.text_alpha = 255
        self.text_display_time = 0  # Track how long text has been shown
        self.initial_delay = 8.0  # Increased from 6.0 seconds
        self.total_time = 0  # Track total elapsed time
        self.flip_complete_time = 0  # Track time since flip completed
        self.flip_completed = False  # Track if flip has completed
        self.animation_complete = False  # Track if entire animation is complete
        self.card_text_alpha = 0  # Alpha for card name text
        self.phase2_started = False  # Track if phase 2 has started
        self.phase2_time = 0  # Track time in phase 2
        self.phase2_duration = 4.0  # Increased from 2.0 seconds
        self.card_scale = 1.0  # Current scale of the card
        self.card_y_offset = 0  # Current y offset of the card
        self.phase3_started = False  # Track if phase 3 has started
        self.phase3_time = 0  # Track time in phase 3
        self.description_alpha = 0  # Alpha for description text
        self.phase4_started = False  # Track if phase 4 has started
        self.phase4_time = 0  # Track time in phase 4
        self.fade_out_alpha = 255  # Alpha for fade out
        self.cta_alpha = 0  # Alpha for CTA text
        
        # Sound effect variables
        self.clonck_sound = None
        self.clonck_played = [False, False, False]  # Track if each clonck has been played
        self.clonck_times = [2.0, 4.0, 6.0]  # Times to play clonck sound (in seconds)
        
        # Audio recording variables
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.audio_start_time = None
        self.sample_rate = 44100
        self.channels = 2
        
        # Typewriter effect variables
        self.typing_speed = 0.1  # Increased from 0.05
        self.typing_timer = 0
        self.text_index = 0
        self.current_text = ""
        self.displayed_text = ""
        self.lines_to_type = []
        self.line_widths = []
        self.current_line_index = 0
        self.typing_complete = False
        self.typing_complete_time = 0  # Track time since typing completed
        
        # Card selection
        self.card_selector = CardSelector(assets_dir)
        self.card_name, self.card_orientation, self.card_image_path = self.card_selector.select_random_card()
        self.card_rotation = 180 if self.card_orientation == "Reversed" else 0
        
        # Reading generator
        self.reading_generator = ReadingGenerator()
        self.generated_reading = None
        self.reading_ready = False
        self.reading_error = False
        
        # Start generating reading in background thread
        self._start_reading_generation()

    def _start_reading_generation(self):
        """Start generating the reading in a background thread."""
        def generate_reading():
            try:
                reading, _ = self.reading_generator.generate_daily_reading(
                    self.card_name,
                    self.card_orientation
                )
                self.generated_reading = reading
            except Exception as e:
                print(f"Error generating reading: {e}")
                self.reading_error = True
                self.generated_reading = self.reading_generator.generate_placeholder_reading()
            finally:
                self.reading_ready = True

        thread = threading.Thread(target=generate_reading)
        thread.daemon = True
        thread.start()

    def setup(self):
        """Set up the animation window and load resources."""
        # Set background color
        arcade.set_background_color(arcade.color.WHITE)
        
        # Load textures
        self.load_textures()
        
        # Load sound effects
        sound_path = os.path.join(self.assets_dir, "sound", "clonck.wav")
        if os.path.exists(sound_path):
            self.clonck_sound = arcade.load_sound(sound_path)
        
        # Calculate background scale to fill window
        bg_width, bg_height = self.background.width, self.background.height
        window_width, window_height = self.window.width, self.window.height
        
        # Calculate scale to fill while maintaining aspect ratio
        scale_x = window_width / bg_width
        scale_y = window_height / bg_height
        self.bg_scale = max(scale_x, scale_y)  # Use max instead of min to fill the window
        
        # Calculate centered position
        self.bg_x = window_width // 2
        self.bg_y = window_height // 2

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
        
        # Load front texture using the selected card
        self.card_front = arcade.load_texture(self.card_image_path)

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
            # Start fading text after 3 seconds
            if self.show_text and self.total_time > 3.0:
                self.text_alpha = max(0, self.text_alpha - (delta_time * 255))  # Fade over 1 second
            
            # Play clonck sounds during initial delay
            if self.clonck_sound:
                for i, (played, time) in enumerate(zip(self.clonck_played, self.clonck_times)):
                    if not played and self.total_time >= time:
                        print(f"Playing initial clonck {i+1} at {self.total_time:.2f} seconds")
                        self.play_sound(self.clonck_sound)
                        self.clonck_played[i] = True
            
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
            # Fade in card name text over 1 second
            self.card_text_alpha = min(255, self.card_text_alpha + (delta_time * 255))
            
            # Start phase 2 after 3 seconds of showing completed flip
            if self.flip_complete_time >= 3.0:
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
                # Use the pre-generated reading
                if self.reading_ready:
                    set_paragraph_typing(self, self.generated_reading, font_size=16)
                else:
                    # If reading isn't ready yet, use placeholder
                    set_paragraph_typing(self, self.reading_generator.generate_placeholder_reading(), font_size=16)
        elif self.phase3_started and not self.phase4_started:
            self.phase3_time += delta_time
            
            # Update typing effect
            self.typing_timer += delta_time
            if self.typing_timer >= self.typing_speed:
                if self.text_index < len(self.current_text):
                    self.text_index += 1
                    self.displayed_text = self.current_text[:self.text_index]
                    # Play typewriter sound every other character
                    if self.text_index % 2 == 0 and self.clonck_sound:
                        # Calculate the exact time when this character should appear
                        typing_start_time = self.phase3_time - (self.typing_timer - self.typing_speed)
                        print(f"Playing typewriter sound at {typing_start_time:.2f} seconds")
                        self.play_sound(self.clonck_sound)
                    self.typing_timer = 0
                else:
                    if self.current_line_index < len(self.lines_to_type) - 1:
                        self.current_line_index += 1
                        set_typing_text(self, self.lines_to_type[self.current_line_index])
                    else:
                        self.typing_complete = True
            
            # Track time since typing completed
            if self.typing_complete:
                self.typing_complete_time += delta_time
            
            # Start phase 4 only if:
            # 1. Typing has been complete for at least 3 seconds, AND
            # 2. Minimum time of 25 seconds has passed
            if self.typing_complete and self.typing_complete_time >= 3.0 and self.phase3_time >= 25.0:
                self.phase4_started = True
                self.phase4_time = 0
        elif self.phase4_started and not self.animation_complete:
            self.phase4_time += delta_time
            
            # Fade out everything over 1 second
            if self.phase4_time < 1.0:
                self.fade_out_alpha = max(0, self.fade_out_alpha - (delta_time * 255))
                self.card_text_alpha = self.fade_out_alpha
                self.description_alpha = self.fade_out_alpha
            
            # Fade in CTA text after fade out completes
            if self.phase4_time >= 1.0:
                self.cta_alpha = min(255, self.cta_alpha + (delta_time * 255))
            
            # End animation after 8 seconds of showing CTA (1s fade out + 7s CTA)
            if self.phase4_time >= 8.0:
                self.animation_complete = True
                if self.recording:
                    self.window.close()

    def _calculate_font_size(self, text: str, max_width: int = 250) -> int:
        """Calculate appropriate font size based on text length."""
        # Base font sizes for different text lengths
        if len(text) <= 10:
            return 34  # Default size for short names
        elif len(text) <= 15:
            return 30  # Slightly smaller for medium names
        elif len(text) <= 20:
            return 26  # Even smaller for long names
        else:
            return 22  # Smallest for very long names

    def draw(self):
        """Draw the current state of the animation."""
        # Clear the screen
        arcade.start_render()
        
        # Draw background maintaining aspect ratio
        arcade.draw_texture_rectangle(
            self.bg_x,
            self.bg_y,
            self.background.width * self.bg_scale,
            self.background.height * self.bg_scale,
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
                    alpha=int(self.fade_out_alpha)
                )
            else:
                # Draw front side
                scale = np.cos(np.radians(180 - self.angle)) * self.card_scale
                arcade.draw_texture_rectangle(
                    center_x, center_y,
                    self.card_size[0] * scale,
                    self.card_size[1] * self.card_scale,
                    self.card_front,
                    angle=self.card_rotation,  # Apply rotation for reversed cards
                    alpha=int(self.fade_out_alpha)
                )
        
        # Only draw text in appropriate phases
        if not self.phase4_started:  # Don't draw any text in phase 4
            # Draw text if visible (after the card)
            if self.show_text and not self.phase2_started:  # Only show before phase 2
                # Draw text with outline
                draw_outlined_line(
                    line="Daily Tarot",
                    x=self.window.width // 2,
                    y=center_y + self.card_size[1] // 2 + 50,
                    font_size=38,  # Increased from 36
                    color=(255, 255, 255, int(self.text_alpha)),
                    outline_color=(0, 0, 0, int(self.text_alpha)),
                    align="center"
                )

            # Draw card name and orientation after flip completes
            if self.flip_completed and self.card_text_alpha > 0:
                # Calculate text position that scales with card size
                text_offset = (self.card_size[1] * self.card_scale) // 2
                
                # Calculate dynamic font size for card name only
                card_name_size = self._calculate_font_size(self.card_name)
                
                # Draw card name with outline
                draw_outlined_line(
                    line=self.card_name,  # Use dynamic card name
                    x=self.window.width // 2,
                    y=center_y + text_offset + 90,
                    font_size=card_name_size,
                    color=(255, 255, 255, int(self.card_text_alpha)),
                    outline_color=(0, 0, 0, int(self.card_text_alpha)),
                    align="center"
                )
                
                # Draw orientation with outline (fixed size)
                draw_outlined_line(
                    line=self.card_orientation,  # Use dynamic orientation
                    x=self.window.width // 2,
                    y=center_y + text_offset + 40,
                    font_size=30,  # Fixed size for orientation
                    color=(255, 255, 255, int(self.card_text_alpha)),
                    outline_color=(0, 0, 0, int(self.card_text_alpha)),
                    align="center"
                )

            # Draw description text in phase 3
            if self.phase3_started and self.fade_out_alpha > 0:
                typewriter_lines(
                    self,
                    center_x=self.window.width // 2-30,
                    start_y=self.window.height // 2,
                    font_size=16,
                    color=(255, 255, 255, int(self.fade_out_alpha)),
                    outline_color=(0, 0, 0, int(self.fade_out_alpha)),
                    line_height=35  # Set specific line height instead of using multiplier
                )

        # Draw CTA text in phase 4
        if self.phase4_started and self.cta_alpha > 0:
            # Draw each line of CTA text separately with outline
            base_y = self.window.height // 2 + 100
            line_height = 60  # Space between lines
            
            # Draw "Visit"
            draw_outlined_line(
                line="Visit",
                x=self.window.width // 2,
                y=base_y + line_height + 20,
                font_size=48,
                color=(255, 255, 255, int(self.cta_alpha)),
                outline_color=(0, 0, 0, int(self.cta_alpha)),
                align="center"
            )
            
            # Draw "Mama Nyah"
            draw_outlined_line(
                line="Mama Nyah",
                x=self.window.width // 2,
                y=base_y,
                font_size=48,
                color=(255, 255, 255, int(self.cta_alpha)),
                outline_color=(0, 0, 0, int(self.cta_alpha)),
                align="center"
            )
            
            # Draw "Today"
            draw_outlined_line(
                line="Today",
                x=self.window.width // 2,
                y=base_y - line_height - 20,
                font_size=48,
                color=(255, 255, 255, int(self.cta_alpha)),
                outline_color=(0, 0, 0, int(self.cta_alpha)),
                align="center"
            )

    def start_recording(self, output_path: str, fps: int = 30):
        """Start recording the animation."""
        # Reset recording state
        self.recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        # Remove existing output file if it exists
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            print(f"Warning: Could not remove existing output file: {e}")
        
        # Start new recording
        self.recording = True
        # Create video writer with MJPG codec
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (self.window.width, self.window.height),
            True
        )
        
        if not self.video_writer.isOpened():
            raise RuntimeError("Could not open video writer")
            
        # Set up frame timing
        self.target_frame_time = 1.0 / (fps * 0.5)  # Slow down frame capture to half speed
        self.last_frame_time = time.time()
        self.accumulated_time = 0

    def on_update(self, delta_time: float):
        """Update the animation state."""
        # Scale the delta_time to control animation speed
        scaled_delta = delta_time * 0.25  # Slow down the animation to quarter speed
        self.update(scaled_delta)
        
        # If recording, accumulate time for frame capture
        if self.recording and self.video_writer is not None:
            current_time = time.time()
            self.accumulated_time += current_time - self.last_frame_time
            self.last_frame_time = current_time

    def on_draw(self):
        """Draw the current state of the animation."""
        self.draw()
        
        # If recording, capture the frame after drawing
        if self.recording and self.video_writer is not None and self.accumulated_time >= self.target_frame_time:
            # Get the current frame as a numpy array
            frame = arcade.get_image()
            frame_array = np.array(frame)
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            # Ensure frame is in the correct format
            frame_bgr = cv2.resize(frame_bgr, (self.window.width, self.window.height))
            self.video_writer.write(frame_bgr)
            self.accumulated_time = 0  # Reset accumulated time

    def play_sound(self, sound):
        """Play a sound."""
        if sound:
            sound.play()

    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop()
            self.audio_stream.close()

def create_card_flip_animation(
    card_name: str,
    card_orientation: str,
    output_path: str,
    fps: int = 30,  # Reduced from 60
    window_width: int = 600,
    window_height: int = 1000
) -> str:
    """Create a card flip animation with the given card and save it to the output path."""
    # Create a temporary file for the video
    temp_video_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as temp_file:
            temp_video_path = temp_file.name

        # Create the window with mobile dimensions
        window = arcade.Window(window_width, window_height, "Card Flip Animation")
        
        # Create and run the animation
        animation = CardFlipAnimation(assets_dir="assets")
        animation.setup()
        
        # Set the animation as the current view
        window.show_view(animation)
        
        # Start recording with the same dimensions
        animation.start_recording(temp_video_path, fps=fps)
        
        # Run the animation
        arcade.run()
        
        # Close the window to release resources
        window.close()
        
        # Get the absolute path to the music file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(script_dir, "..", "..", "assets", "sound", "Pixel 1.wav")
        
        if os.path.exists(music_path):
            try:
                # Check if ffmpeg is installed
                import shutil
                ffmpeg_path = shutil.which('ffmpeg')
                if not ffmpeg_path:
                    print("Error: FFmpeg is not installed or not in PATH.")
                    print("Please install FFmpeg and add it to your system PATH.")
                    print("You can install it using:")
                    print("1. Chocolatey: choco install ffmpeg")
                    print("2. Or download from: https://ffmpeg.org/download.html")
                    # Just use the original video without audio
                    shutil.copy2(temp_video_path, output_path)
                    return output_path

                print(f"Using FFmpeg at: {ffmpeg_path}")
                print(f"Adding music from: {music_path}")

                # FFmpeg command to convert to MP4 and add audio
                cmd = [
                    ffmpeg_path,
                    '-y',
                    '-i', temp_video_path,
                    '-i', music_path,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '18',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-shortest',
                    '-pix_fmt', 'yuv420p',
                    '-af', 'volume=2.0',  # Increase volume
                    output_path
                ]
                
                print("Running FFmpeg command to create final video:", " ".join(cmd))
                result = subprocess.run(cmd, check=False, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"FFmpeg error creating final video: {result.stderr}")
                    # If FFmpeg fails, just use the original video
                    shutil.copy2(temp_video_path, output_path)
                else:
                    print("Successfully created final video with audio")
                
            except Exception as e:
                print(f"Error processing video: {e}")
                print("Falling back to video without audio")
                # If anything fails, just use the original video
                shutil.copy2(temp_video_path, output_path)
        else:
            print(f"Music file not found at: {music_path}")
            print("Falling back to video without audio")
            # If music file doesn't exist, just use the original video
            shutil.copy2(temp_video_path, output_path)
        
        return output_path
        
    finally:
        # Clean up temporary files
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_video_path}: {e}")

def set_typing_text(game, new_text):
    """
    Sets the text to be typed dynamically.
    Only resets typing if the text is different.
    """
    if game.current_text != new_text:  # Only reset if the text is different
        game.current_text = new_text
        game.displayed_text = ""  # Reset displayed text
        game.text_index = 0       # Reset typing progress
        game.typing_timer = 0

def set_paragraph_typing(game, paragraph, font_size=18, font_name = "Old School Adventures", color=arcade.color.WHITE, width = 600):
    """
    Sets up the typing effect for a multi-line paragraph.
    """
    
    if not game.lines_to_type or game.current_text != paragraph:  # Prevent resetting
        lines = []
        for block in paragraph.split("\n\n"):  # Split into paragraphs
            wrapped_lines = textwrap.wrap(block, width= width // font_size)
            lines.extend(wrapped_lines + [""])  # Add wrapped lines and an empty line for spacing

        game.lines_to_type = lines  # Store all lines
        game.current_line_index = 0  # Start from the first line
        game.line_widths = []
        for line in game.lines_to_type:  ## This measure the pixel width of each line dynamically
            text_image = arcade.create_text_image(
                text=line,
                font_size=font_size,
                font_name=font_name,
                text_color=color,
                align= "center"
            )
            line_width = text_image.width * 1.5 ##Account for the fonts larger size and glyph boxes
          
            game.line_widths.append(line_width) 
            
        
        set_typing_text(game, game.lines_to_type[0])

if __name__ == "__main__":
    # Test the animation
    print("Starting main execution...")
    output_path = "card_flip.mp4"  # Changed back to .mp4
    print(f"Will save output to: {output_path}")
    
    # Create a card selector to get random card
    card_selector = CardSelector("assets")
    card_name, card_orientation, _ = card_selector.select_random_card()
    
    # Create the animation with the selected card
    create_card_flip_animation(
        card_name=card_name,
        card_orientation=card_orientation,
        output_path=output_path,
        fps=30,
        window_width=600,
        window_height=1000
    )
    print("Animation creation completed") 