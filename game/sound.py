from settings import *
from support import audio_importer
from states.menu import Menu, Settings
from states.gameplay import Gameplay, Pause, Shop

class Sound:
    def __init__(self, game):
        self.game = game
        self.load_sounds()
        
        # states
        self.prev_state = None
        self.state = Menu.music_state
        
        self.current_music = None
    
    def load_sounds(self):
        self.music: dict[str, pygame.mixer.Sound] = audio_importer(join('sounds', 'music'))
        self.sounds: dict[str, pygame.mixer.Sound] = audio_importer(join('sounds', 'sounds'))
        self.step_sounds: dict[str, pygame.mixer.Sound] = audio_importer(join('sounds', 'sounds', 'steps'))
        
    def play_music(self):
        if self.state != self.prev_state:
            if self.current_music:
                self.current_music.fadeout(1000)
            if self.state == Menu.music_state:
                self.current_music = self.music['menu']
                self.current_music.play(loops=-1)
            if self.state == Gameplay.music_state:
                self.current_music = self.music['gameplay']
                self.current_music.play(loops=-1)
            if self.state == Shop.music_state:
                self.current_music = self.music['shop']
                self.current_music.play(loops=-1)
        
        
    def update(self, dt):
        self.play_music()
        self.prev_state = self.state
        self.state = self.game.current_state.music_state
        
        for music in self.music.values():
            music.set_volume(self.game.music_volume*1.5)
            
        for sound in self.sounds.values():
            sound.set_volume(self.game.sounds_volume*1.5)
            
        for sound in self.step_sounds.values():
            sound.set_volume(self.game.sounds_volume*1.5 * 5)