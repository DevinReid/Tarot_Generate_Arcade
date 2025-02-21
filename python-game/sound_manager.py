import arcade
import resource_path
from fetch_utility import debug_mode

class SoundManager:
    def __init__(self, music_file_path):
        self.music_file_path = music_file_path
        self.music = None
        self.music_player = None
        self.sfx_sounds={}

        self.music_enabled = True
        self.music_volume = .8

        self.sfx_enabled = True
        self.sfx_volume = 1.0
        

    def load_music(self):
        """Load the music file."""
     
        self.music = arcade.Sound(self.music_file_path,streaming=True)


    def play_music(self, volume=0.5, loop=True):
        """Play the loaded music at specified volume, optionally looping."""
        
        if self.music_player:
            self.music_player.play()  # Resume music if it's paused??
        else:
            self.music_player = self.music.play(volume=volume, loop=loop)

    def pause_music(self):
        """Stop the music."""
        if self.music_player:
            self.music_player.pause()


    def toggle_music(self):
        if self.music_player:
            if self.music_enabled:
                self.pause_music()
                self.music_enabled = False
            else:
                self.play_music()
                self.music_enabled = True
    
    def change_music_volume(self, amount):
        self.music_volume = max(0.0, min(1.0, self.music_volume + amount))
        if self.music_player:
            self.music_player.volume = self.music_volume
        if debug_mode:
            print(f"New volume: {self.music_volume}") 

    
    def load_sfx(self, sfx_name, file_path):
        """
        Load an SFX sound into the dictionary.
        sfx_name (str): A key, e.g. 'card_draw'
        file_path (str): Path to the audio file, e.g. 'assets/sfx/card_draw.wav'
        """
        try:
            sfx_sound = arcade.load_sound(resource_path.path(file_path))
            self.sfx_sounds[sfx_name] = sfx_sound
        except Exception as e:
            if debug_mode:
                print(f"Failed to load SFX '{sfx_name}': {e}")

    def play_sfx(self, sfx_name, volume=None, speed=1.0):
        """Play a loaded SFX by name."""
        if sfx_name in self.sfx_sounds and self.sfx_enabled:
            volume=self.sfx_volume if volume is None else volume 
            arcade.play_sound(self.sfx_sounds[sfx_name], volume=volume, speed=speed)
        else:
            if debug_mode:
                print(f"SFX '{sfx_name}' not found. Make sure you've loaded it.")

    def toggle_sfx(self):
        """Toggle SFX on/off."""
        self.sfx_enabled = not self.sfx_enabled
        if debug_mode:
            print(f"SFX Enabled: {self.sfx_enabled}")

    def change_sfx_volume(self, amount):
        """Change SFX volume."""
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + amount))
        if debug_mode:
            print(f"New SFX volume: {self.sfx_volume}")
    
