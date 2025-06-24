from settings import *

import states.gameplay
import states.menu
from tilemap import Tilemap
from ui import *
from groups import AllSprites
from support import *
from sprites import *
from sound import Sound

class Game:
    def __init__(self):
        # game init
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('Blitzframe')
        self.clock = pygame.time.Clock()
        self.running = True
        create_score_json()
        
        self.reset_game()  # инициализация состояния игры
        
        # menu background
        screen_size = pygame.display.get_surface().get_size()
        self.background = states.menu.Background('images/menu_background.png', scale=2, screen_size=screen_size)

        
        # sounds
        self.sounds_volume = 0
        self.music_volume = 0
        self.sound = Sound(self)
        

    def reset_game(self):
        
        
        # Сбросить все игровые объекты и состояния
        self.game_paused = False
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.buttons_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        if hasattr(self, 'player'):
            delattr(self, 'player')
            
        self.available_weapons = {
            'pistol': Pistol
        }
        # tilemap
        self.tilemap = Tilemap(self.all_sprites, self.collision_sprites)
        self.tilemap.setup()
        
        # load assets
        self.load_assets()
        
        # game states
        self.states = {
            'main_menu': states.menu.Menu(self),
            'settings': states.menu.Settings(self),
            'gameplay': states.gameplay.Gameplay(self),
            'pause': states.gameplay.Pause(self),
            'shop': states.gameplay.Shop(self),
            'game_over': states.gameplay.GameOver(self)
        }
        self.current_state = self.states['main_menu']
        self.current_state.on_enter() 

    def change_gun(self, gun, sound=True):
        if gun in self.available_weapons:
            self.current_gun.kill()
            self.current_gun = self.available_weapons[gun]((self.all_sprites, self.bullet_sprites), self.player)
            if sound:
                self.play_sound('gun_swap')

    def play_sound(self, name):
        self.sound.sounds[name].play()

    def change_state(self, new_state: str, animation=True):
        def state_func():
            self.buttons_sprites.empty()
            self.current_state = self.states[new_state]
            self.current_state.on_enter()    
        if animation:
            transition_effect(
                    surface=self.display_surface,
                    callback=state_func,
                    draw_callback=lambda: self.current_state.draw())
        else:
            state_func()
        

    def load_assets(self):
        # graphics 
        def scale_frame(surf, scale=3):
            return pygame.transform.scale(
                surf,
                (surf.get_width() * scale, surf.get_height() * scale)
            )

        # ===== player ===========
        def load_and_scale_player_frames():
            directions = [
                'down', 'left_down', 'left', 'left_up',
                'up', 'right_up', 'right', 'right_down'
            ]
            player_frames = {}

            for direction in directions:
                frames = folder_importer('images', 'player', direction)

                if isinstance(frames, dict):
                    frames = [surf for _, surf in sorted(
                        frames.items(),
                        key=lambda item: int(item[0].split('_')[-1].split('.')[0])
                    )]

                scaled_frames = [scale_frame(surf) for surf in frames]
                player_frames[direction] = scaled_frames

            return player_frames
        self.player_frames = load_and_scale_player_frames()

        # ===== normal ========
        enemy_frames = folder_importer('images', 'enemies', 'normal')
        self.normal_enemy_frames = {
            name: scale_frame(surf, 1.5)
            for name, surf in enemy_frames.items()}
        
        # ====== fast ==============
        self.fast_enemy_frames = folder_importer('images', 'enemies', 'fast')
        
        # ====== heavy ==============
        self.heavy_enemy_frames = folder_importer('images', 'enemies', 'heavy')
        
        self.enemies_frames_dict = {
            'normal': self.normal_enemy_frames,
            'fast': self.fast_enemy_frames,
            'heavy': self.heavy_enemy_frames
        }
        
        # ===== buttons =====
        self.buttons_frames = folder_importer(join('images', 'buttons'))
        
        # ===== fonts =====
        self.m_font = pygame.font.Font(join('fonts', 'PixCyrillic.ttf'), 40)
        self.l_font = pygame.font.Font(join('fonts', 'PixCyrillic.ttf'), 80)
        self.s_font = pygame.font.Font(join('fonts', 'PixCyrillic.ttf'), 30)
        self.xs_font = pygame.font.Font(join('fonts', 'PixCyrillic.ttf'), 24)

        
    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # update
            if not self.game_paused:
                self.all_sprites.update(dt)
            self.current_state.update(dt)
            self.sound.update(dt)
            
            # draw
            self.display_surface.fill('black')
            self.current_state.draw()
            
            pygame.display.update()
        pygame.quit()
        

if __name__ == '__main__':
    game = Game()
    game.run()
