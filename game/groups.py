from settings import *
from support import Timer
import random

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.camera_speed = 0.1 
        self.shake_strength = 0
        self.shake_offset = pygame.Vector2()

    def shake(self, strength):
        self.shake_strength = strength

    def draw(self, target_pos):
        target_offset = pygame.Vector2()
        target_offset.x = -(target_pos[0] - WINDOW_WIDTH // 2)
        target_offset.y = -(target_pos[1] - WINDOW_HEIGHT // 2)

        # smooth camera
        self.offset += (target_offset - self.offset) * self.camera_speed

        # shake 
        if self.shake_strength > 0:
            self.shake_offset.x = random.uniform(-self.shake_strength, self.shake_strength)
            self.shake_offset.y = random.uniform(-self.shake_strength, self.shake_strength)
            # decay shake
            self.shake_strength *= 0.9
            if self.shake_strength < 0.1:
                self.shake_strength = 0
        else:
            self.shake_offset = pygame.Vector2()

        # Drawing
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        objects_sprites = sorted([sprite for sprite in self if not hasattr(sprite, 'ground')], key=lambda x: x.rect.centery)

        for sprite in ground_sprites + objects_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset + self.shake_offset)
            
            # отрисовка здоровья мобов
            if hasattr(sprite, 'draw_health'):
                sprite.draw_health(self.display_surface, self.offset + self.shake_offset)