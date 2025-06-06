import pygame
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.current_music = None
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.sounds = {}

    def load_music(self, filepath):
        """Load background music file"""
        try:
            if os.path.exists(filepath):
                self.current_music = filepath
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                return True
            else:
                print(f"Music file not found: {filepath}")
                return False
        except Exception as e:
            print(f"Error loading music: {e}")
            return False

    def play_music(self, loops=-1):
        """Play the loaded music (loops=-1 for infinite)"""
        if self.current_music:
            pygame.mixer.music.play(loops)

    def stop_music(self, fadeout=1000):
        """Stop music with optional fadeout in milliseconds"""
        pygame.mixer.music.fadeout(fadeout)

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def load_sound(self, name, filepath):
        """Load a sound effect"""
        try:
            if os.path.exists(filepath):
                self.sounds[name] = pygame.mixer.Sound(filepath)
                self.sounds[name].set_volume(self.sound_volume)
                return True
            else:
                print(f"Sound file not found: {filepath}")
                return False
        except Exception as e:
            print(f"Error loading sound: {e}")
            return False

    def play_sound(self, name):
        """Play a loaded sound effect"""
        if name in self.sounds:
            self.sounds[name].play()

    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
