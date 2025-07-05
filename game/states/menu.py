from settings import *
from ui import *
from support import *

import pygame
import json
import os

class Intro:
    def __init__(self, image_path, duration=2.0, scale_start=1, scale_end=1.2):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.duration = duration
        self.elapsed = 0.0
        self.done = False
        self.display_surface = pygame.display.get_surface()
        self.center = self.display_surface.get_rect().center
        self.scale_start = scale_start
        self.scale_end = scale_end
        self.current_image = self.original_image
        self.image_rect = self.original_image.get_rect(center=self.center)

    def update(self, dt):
        if self.done:
            return
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.done = True

        # Scale calculation
        t = min(self.elapsed / self.duration, 1.0)
        scale = self.scale_start + (self.scale_end - self.scale_start) * t
        w = int(self.original_image.get_width() * scale)
        h = int(self.original_image.get_height() * scale)
        self.current_image = pygame.transform.smoothscale(self.original_image, (w, h))
        self.image_rect = self.current_image.get_rect(center=self.center)

    def draw(self):
        if not self.done:
            img = self.current_image.copy()
            img.set_alpha(255)
            self.display_surface.blit(img, self.image_rect)


class Background:
    def __init__(self, image_path, scale, screen_size, speed=20):
        bg = pygame.image.load(image_path).convert()
        size = (bg.get_width() * scale, bg.get_height() * scale)
        self.image = pygame.transform.scale(bg, size)

        self.offset = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(1, 1).normalize()
        self.speed = speed

        self.screen_rect = pygame.Rect(0, 0, *screen_size)
        self.bg_rect = self.image.get_rect()

    def draw(self, surface):
        source = pygame.Rect(self.offset.x, self.offset.y, self.screen_rect.width, self.screen_rect.height)
        surface.blit(self.image, (0, 0), source)

    def update(self, dt):
        self.offset += self.direction * self.speed * dt

        if self.offset.x <= 0:
            self.offset.x = 0
            self.direction.x *= -1
        elif self.offset.x >= self.bg_rect.width - self.screen_rect.width:
            self.offset.x = self.bg_rect.width - self.screen_rect.width
            self.direction.x *= -1

        if self.offset.y <= 0:
            self.offset.y = 0
            self.direction.y *= -1
        elif self.offset.y >= self.bg_rect.height - self.screen_rect.height:
            self.offset.y = self.bg_rect.height - self.screen_rect.height
            self.direction.y *= -1

class MainMenu:
    music_state = 'main_menu'

    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()

    def on_enter(self):
        self.create_buttons()

    def draw(self):
        self.game.background.draw(self.display_surface)
        self.game.buttons_sprites.draw(self.display_surface)

    def update(self, dt):
        self.game.background.update(dt)
        self.game.buttons_sprites.update(dt)


class Menu(MainMenu):
    
    state_name = 'main_menu'
    
    def create_buttons(self):
        # new game
        self.start_game_button = Button(
            groups=(self.game.buttons_sprites),
            pos=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3),
            image=self.game.buttons_frames['new_game']
        )

        # settings
        self.settings_button = Button(
            groups=(self.game.buttons_sprites),
            pos=(self.start_game_button.rect.centerx, self.start_game_button.rect.centery + self.start_game_button.rect.height + 50),
            image=self.game.buttons_frames['settings']
        )

        # exit game
        self.exit_button = Button(
            groups=(self.game.buttons_sprites),
            pos=(self.settings_button.rect.centerx, self.settings_button.rect.centery + self.settings_button.rect.height + 50),
            image=self.game.buttons_frames['exit']
        )


    def input(self):
        # keys = pygame.key.get_just_pressed()

        if self.start_game_button.is_clicked():
            self.game.change_state('gameplay')
     
        if self.settings_button.is_clicked():
            self.game.change_state('settings')

        if self.exit_button.is_clicked():
            self.game.running = False
            

    def draw_score(self):
        # Размеры и позиция окна
        window_width = 480
        window_height = 400
        window_x = 0
        window_y = WINDOW_HEIGHT/2 - WINDOW_HEIGHT/5 
        self.window_rect = pygame.Rect(window_x, window_y, window_width, window_height)

        window_surf = pygame.Surface(self.window_rect.size, pygame.SRCALPHA)
        window_surf.fill((0, 0, 0, 0))
        rect = window_surf.get_rect()
        pygame.draw.rect(
            window_surf,
            (50, 50, 50, 150),
            rect,
            border_top_left_radius=0,
            border_bottom_left_radius=0,
            border_top_right_radius=20,
            border_bottom_right_radius=20
        )
        self.display_surface.blit(window_surf, self.window_rect.topleft)

        # Заголовок
        font = self.game.s_font 
        title_surf = font.render("Лучшие результаты", True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.window_rect.left + self.window_rect.width // 2, self.window_rect.top + 15))
        self.display_surface.blit(title_surf, title_rect)


        scores = load_json(join('settings', 'score.json'))


        # Отрисовка результатов
        entry_font = self.game.xs_font 
        start_y = self.window_rect.top + 90
        line_height = 46
        for i, (key, entry) in enumerate(sorted(scores.items(), key=lambda x: int(x[0]))):
            if i < 6:
                text = f"{key}. Волны: {entry['waves']}  Убийства: {entry['kills']}  Очки: {entry['total']}"
                entry_surf = entry_font.render(text, True, (220, 220, 220))
                entry_rect = entry_surf.get_rect(left=self.window_rect.left + 20, top=start_y + i * line_height)
                self.display_surface.blit(entry_surf, entry_rect)

    def draw(self):
        super().draw()
        self.draw_score()

    def update(self, dt):
        super().update(dt)
        self.input()
            
      
        
class Settings(MainMenu):
    state_name = 'settings'
    
    def create_buttons(self):
        
        # sounds volume
        self.sounds_volume_slider = Slider(
            groups=self.game.buttons_sprites,
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT//3),
            size=(300, 20),
            initial_value=self.game.sounds_volume,
            label_text='Громкость эффектов:',
            label_font=self.game.m_font
        )
        
        # music volume 
        self.music_volume_slider = Slider(
            groups=self.game.buttons_sprites,
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT//3 + 100),
            size=(300, 20),
            initial_value=self.game.music_volume,
            label_text='Громкость музыки:',
            label_font=self.game.m_font
        )
        
        # back to menu
        self.back_to_menu_button = Button(
            groups=(self.game.buttons_sprites),
            pos=(150, 100),
            image=self.game.buttons_frames['back']
        )


    def input(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_ESCAPE] or self.back_to_menu_button.is_clicked():
            self.game.change_state('main_menu')
            self.text = 'mian_menu'
            
        
        
        self.game.sounds_volume = self.sounds_volume_slider.get_value()
        self.game.music_volume = self.music_volume_slider.get_value()

    def update(self, dt):
        super().update(dt)
        self.input()