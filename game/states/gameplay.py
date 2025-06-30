from settings import *
from sprites import *
from tilemap import Tilemap
from support import *
from ui import *

from random import choice

class InGameStats:
    def __init__(self, game):
        self.game = game
        self.money = 0
        self.health = self.game.player.health
        self.wave = 1
        self.kills = 0
        
        # wave
        self.prev_enemies_count = self.enemies_counter = 0
        self.wave_active = False
        
        # upgrades
        self.heal_price = 30
        
        self.health_upgrade = 100
        self.health_upgrade_step = 20
        self.health_level = (self.health_upgrade - 100) // self.health_upgrade_step + 1
        self.health_upgrade_price = 30
        self.health_price_step = 10
        
        self.damage_upgrade = load_json(join('settings', 'gun_settings.json'))['base_damage']
        self.damage_upgrade_step = 4
        self.damage_level = (self.damage_upgrade - 50) // self.damage_upgrade_step + 1
        self.damage_upgrade_price = 40
        self.damage_price_step = 15
        
        self.speed_upgrade = 150
        self.speed_upgrade_step = 10
        self.speed_level = (self.speed_upgrade - 150) // self.speed_upgrade_step + 1
        self.speed_upgrade_price = 50
        self.speed_price_step = 20
        
    def update_skill_level(self):
        self.health_level = (self.health_upgrade - 100) // self.health_upgrade_step + 1
        self.damage_level = (self.damage_upgrade - 50) // self.damage_upgrade_step + 1
        self.speed_level = (self.speed_upgrade - 150) // self.speed_upgrade_step + 1
        
        
    def get_upgrade_price(self, skill):
        if skill == 'health':
            return self.health_upgrade_price + (self.health_level) * self.health_price_step
        elif skill == 'damage':
            return self.damage_upgrade_price + (self.damage_level) * self.damage_price_step
        elif skill == 'speed':
            return self.speed_upgrade_price + (self.speed_level) * self.speed_price_step
        
    def next_upgrage_price(self):
        self.next_health_upgrade_price = self.health_upgrade_price + (self.health_level) * self.health_price_step
        self.next_damage_upgrade_price = self.damage_upgrade_price + (self.damage_level) * self.damage_price_step
        self.next_speed_upgrade_price = self.speed_upgrade_price + (self.speed_level) * self.speed_price_step
    
    def update(self):
        self.health = self.game.player.health
        
        self.prev_enemies_count = self.enemies_counter
        self.enemies_counter = len(self.game.enemy_sprites)
        if self.prev_enemies_count > self.enemies_counter:
            self.money += random.randint(15, 20) * (self.prev_enemies_count - self.enemies_counter)
            self.kills += self.prev_enemies_count - self.enemies_counter


class Gameplay:
    state_name = 'gameplay'
    music_state = 'gameplay'
    def __init__(self, game):
        self.game = game

    def on_enter(self):
        if not hasattr(self.game, 'player'):
            self.game.gameplay = self
            self.game.player = Player((self.game.all_sprites), self.game.tilemap.player_spawner(), self.game.collision_sprites, self.game.player_frames, game=self.game)
            self.game.game_stats = self.game_stats = InGameStats(self.game)
            self.game.current_gun = Pistol((self.game.all_sprites, self.game.bullet_sprites), self.game.player)
            self.start_wave_timer()
        self.game.change_gun(self.game.current_gun.gun_name, sound=False)    
    
    def start_wave_timer(self):
        self.starting_wave_timer = Timer(2000, False, True, self.starting_wave)


    def input(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_ESCAPE]:
            self.game.change_state('pause', False)
        
        if keys[pygame.K_i]:
            for sprite in self.game.enemy_sprites:
                sprite.kill()
                
        if keys[pygame.K_q]:
            self.game.available_weapons[Shotgun.gun_name] = Shotgun
            self.game.available_weapons[SniperRifle.gun_name] = SniperRifle
            self.game.available_weapons[MachineGun.gun_name] = MachineGun
            print(self.game.available_weapons)
        if keys[pygame.K_1]:
            self.game.change_gun(Pistol.gun_name)
            print(Pistol.gun_name)
        if keys[pygame.K_2]:
            self.game.change_gun(Shotgun.gun_name)
            print(Shotgun.gun_name)
        if keys[pygame.K_3]:
            self.game.change_gun(SniperRifle.gun_name)
            print(SniperRifle.gun_name)
        if keys[pygame.K_4]:
            self.game.change_gun(MachineGun.gun_name)
            print(MachineGun.gun_name)

            
    def draw_game_ui(self):
        surface = pygame.display.get_surface()
        
        # ======== healthbar ========
        font = pygame.font.Font(None, 28)
        bar_width, bar_height = 200, 30
        x, y = 20, 20
        health = self.game.player.health
        max_health = self.game.player.max_health if hasattr(self.game.player, 'max_health') else 100

        # задний фон
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height), border_radius=8)
        # сколько хп
        fill_width = int(bar_width * (health / max_health))
        pygame.draw.rect(surface, (76, 184, 28), (x, y, fill_width, bar_height), border_radius=8)
        # обводка
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1, border_radius=8)

        # текст количества хп
        health_text = font.render(f'{health} / {max_health}', True, (255, 255, 255))
        text_rect = health_text.get_frect(center=(x + bar_width // 2, y + bar_height // 2))
        surface.blit(health_text, text_rect)

        # ======== player money ========
        font = pygame.font.Font(None, 40)
        x, y = 20, 70
        money_text = font.render(f'{self.game_stats.money} $', True, (0, 0, 0))
        text_rect = money_text.get_frect(topleft=(x, y))
        surface.blit(money_text, text_rect)


    def starting_wave(self):
        self.game_stats.wave_active = True
        # draw wave number
        surface = pygame.display.get_surface()
        font = self.game.l_font
        x, y = surface.width//2, 70
        self.fade_text = FadeText(f'Волна {self.game_stats.wave}', font, (82, 61, 80), (x, y))
        self.fade_text.start()
        self.game.play_sound('tick')
        
        # starting wave
        wave_settings = load_json('settings/waves.json')[str(self.game_stats.wave)]
        enemies_dict = {
            NormalEnemy.name: NormalEnemy,
            FastEnemy.name: FastEnemy,
            HeavyEmemy.name: HeavyEmemy
        }
        wave_multipliers = wave_settings['enemies_multiplier']
        
        # spawn enemies
        self.spawn_timers: list[Timer] = []
        for enemy_name, enemy_num in wave_settings['enemies'].items():
            for _ in range(enemy_num):
                
                # Фильтруем спавнеры, оставляя только те, что далеко от игрока
                def choice_spawner(min_distance=600):
                    player_pos = self.game.player.rect.center
                    spawners = [
                        pos for pos in self.game.tilemap.enemy_spawner()
                        if ((pos[0] - player_pos[0]) ** 2 + (pos[1] - player_pos[1]) ** 2) ** 0.5 > min_distance
                    ]
                    if not spawners:
                        spawners = self.game.tilemap.enemy_spawner()
                    spawner = choice(spawners)
                    return spawner
                
                self.spawn_timers.append(Timer(
                    random.randint(1000, self.game_stats.wave * 1000), 
                    False, 
                    True, 
                    lambda enemy_name = enemy_name: enemies_dict[enemy_name]((
                        self.game.all_sprites, self.game.enemy_sprites), 
                        choice_spawner(700),
                        self.game.enemies_frames_dict[enemy_name],
                        self.game.player,
                        self.game.collision_sprites,
                        health_multiplier=wave_multipliers['health'],
                        speed_multiplier=wave_multipliers['speed'],
                        damage_multiplier=wave_multipliers['damage']
                        )))
        
    
    def ending_wave(self):
        self.game_stats.wave_active = False
        # draw wave congradulation
        surface = pygame.display.get_surface()
        font = self.game.l_font
        x, y = surface.width//2, 70
        self.fade_text = FadeText(f'Волна {self.game_stats.wave} пройдена!', font, (82, 61, 80), (x, y))
        self.fade_text.start()
        
        # go to shop
        self.game_stats.wave += 1
        self.ending_wave_timer = Timer(2000, False, True, lambda: self.game.change_state('shop'))
    
                
    def collision(self):
        for bullet in self.game.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.game.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                bullet.kill()
                for sprite in sprite_collision:
                    if sprite.collision_active:
                        sprite.take_damage(bullet.damage)
        
        for enemy in self.game.enemy_sprites:
            if enemy.rect.colliderect(self.game.player.rect):
                self.game.player.take_damage(enemy)
                if not self.game.player.damage_delay_timer:
                    enemy.deal_damage()
        
    def check_player_alive(self):
        if self.game_stats.health <= 0:
            self.game.player.health = 0
            self.game.player.death()  
            self.game.current_gun.kill()
            if not hasattr(self, 'game_over_timer'):
                self.game_over_timer = Timer(2000, False, True, lambda: self.game.change_state('game_over'))
            
    
           
    def draw(self):
        self.game.all_sprites.draw(self.game.player.rect.center)
        self.draw_game_ui()
        
        if hasattr(self, 'fade_text'):
            self.fade_text.update(self.game.display_surface)

        if hasattr(self, 'spawn_timers') and not self.spawn_timers and self.game_stats.enemies_counter == 0 and self.game_stats.wave_active:
            self.ending_wave()

            
    def update(self, dt):
        self.input()
        self.game_stats.update()
        self.collision()
        self.check_player_alive()
        
        # timers
        self.starting_wave_timer.update()
        
        if hasattr(self, 'ending_wave_timer'):
            self.ending_wave_timer.update()
        
        if hasattr(self, 'game_over_timer'):
            self.game_over_timer.update()    
        
        
        if hasattr(self, 'spawn_timers'):
            for timer in self.spawn_timers:
                timer.update()
                if not timer: 
                    self.spawn_timers.remove(timer)
                    

class InGameWindow:
    def __init__(self, game, title='', size=(400, 300)):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = self.game.m_font
        self.width, self.height = size
        self.bg_color = (30, 30, 30, 180)
        self.window_rect = pygame.Rect(0, 0, *size)
        self.window_rect.center = self.display_surface.get_rect().center
        self.title = title

    def on_enter(self):
        self.create_buttons()

    def draw(self):
        # игровой фон
        self.game.all_sprites.draw(self.game.player.rect.center)
        # затемнение
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.display_surface.blit(overlay, (0, 0))
        # окно
        window_surf = pygame.Surface(self.window_rect.size, pygame.SRCALPHA)
        window_surf.fill((0, 0, 0, 0)) 
        pygame.draw.rect(
            window_surf,
            (50, 50, 50, 120),
            window_surf.get_rect(),
            border_radius=20  
        )
        self.display_surface.blit(window_surf, self.window_rect.topleft)
        self.menu_window_rect = window_surf.get_rect()
        # заголовок
        if self.title:
            title_surf = self.font.render(self.title, True, 'white')
            title_rect = title_surf.get_rect(center=(self.window_rect.centerx, self.window_rect.top - 50))
            self.display_surface.blit(title_surf, title_rect)
            
        # кнопки
        self.game.buttons_sprites.draw(self.display_surface)

    def update(self, dt):
        self.game.buttons_sprites.update(dt)


class Pause(InGameWindow):
    state_name = 'pause'
    music_state = 'gameplay'
    def __init__(self, game, title='Пауза', size=(400, 300)):
        super().__init__(game, title, size)

    def on_enter(self):
        super().on_enter()
        self.game.game_paused = True

    def create_buttons(self):
        # resume
        self.resume_game_button = Button(
            groups=self.game.buttons_sprites,
            pos=(self.window_rect.x + self.window_rect.width//2, self.window_rect.y + self.window_rect.height//3),
            image=self.game.buttons_frames['resume']
        )
        # main menu
        self.menu_button = Button(
            groups=self.game.buttons_sprites,
            pos=(self.window_rect.x + self.window_rect.width//2, self.window_rect.y + self.window_rect.height//3 + 100),
            image=self.game.buttons_frames['menu']
        )

    def input(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_ESCAPE] or self.resume_game_button.is_clicked():
            self.game.change_state('gameplay', False)
            self.game.game_paused = False

        if self.menu_button.is_clicked():
            self.game.change_state('main_menu')
            self.game.reset_game()

    def update(self, dt):
        super().update(dt)
        self.input()

       
class Shop(InGameWindow):
    state_name = 'shop'
    music_state = 'shop'
    def __init__(self, game, title='Магазин', size=(800, 520)):
        super().__init__(game, title, size)
        self.all_guns = {
                Pistol.gun_name: Pistol,
                Shotgun.gun_name: Shotgun,
                SniperRifle.gun_name: SniperRifle,
                MachineGun.gun_name: MachineGun
            }

    def on_enter(self):
        super().on_enter()
        self.game.game_paused = True

    def create_buttons(self):
        cols = 3
        rows = 4
        horizontal_margin = 40
        vertical_margin_top = 70
        vertical_margin_bottom = 70
        button_spacing_x = 20
        button_spacing_y = 20

        # размеры кнопок
        available_width = self.window_rect.width - 2 * horizontal_margin - (cols - 1) * button_spacing_x
        button_width = available_width // cols
        available_height = self.window_rect.height - vertical_margin_top - vertical_margin_bottom - (rows - 1) * button_spacing_y
        button_height = available_height // rows

        # матрица кнопок
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]

        for row in range(rows):
            for col in range(cols):
                x = self.window_rect.left + horizontal_margin + col * (button_width + button_spacing_x) + button_width // 2
                y = self.window_rect.top + vertical_margin_top + row * (button_height + button_spacing_y) + button_height // 2
                btn = None

                # Start wave
                if row == 0 and col == 1:
                    btn = Button(
                        groups=self.game.buttons_sprites,
                        pos=(x, y),
                        image=self.game.buttons_frames['start_wave'],
                        callback='next_wave'
                    )
                
                # heal player
                if row == 0 and col == 2:
                    btn = Button(
                        groups=self.game.buttons_sprites,
                        pos=(x, y),
                        image=self.game.buttons_frames['heal'],
                        callback='heal_player'
                    )

                # ====== upgrades ======
                # health upgrade
                if row == 1 and col == 2:
                    btn = Button(
                        groups=self.game.buttons_sprites,
                        pos=(x, y),
                        image=self.game.buttons_frames['health_upgrade'],
                        callback='health_upgrade'  
                    )
                # damage upgrade
                if row == 2 and col == 2:
                    btn = Button(
                        groups=self.game.buttons_sprites,
                        pos=(x, y),
                        image=self.game.buttons_frames['damage_upgrade'],
                        callback='damage_upgrade'  
                    )
                # speed upgrade
                if row == 3 and col == 2:
                    btn = Button(
                        groups=self.game.buttons_sprites,
                        pos=(x, y),
                        image=self.game.buttons_frames['speed_upgrade'],
                        callback='speed_upgrade'  
                    )
                
                # ====== guns ======
                gun_name = None
                if col == 0:
                    if row == 0:
                        gun_name = Pistol.gun_name
                    elif row == 1:
                        gun_name = Shotgun.gun_name
                    elif row == 2:
                        gun_name = SniperRifle.gun_name
                    elif row == 3:
                       gun_name = MachineGun.gun_name
                   
                if gun_name: 
                    if gun_name in self.game.available_weapons:
                        # выделяем выбранное оружие
                        if self.game.current_gun.gun_name == gun_name:
                            btn_image = self.game.buttons_frames[f'choosen_{gun_name}']
                        else:
                            btn_image = self.game.buttons_frames[f'open_{gun_name}']
                        btn = Button(
                            groups=self.game.buttons_sprites,
                            pos=(x, y),
                            image=btn_image,
                            callback=f'select_{gun_name}' 
                        )
                    else:
                        btn = Button(
                            groups=self.game.buttons_sprites,
                            pos=(x, y),
                            image=self.game.buttons_frames[f'locked_{gun_name}'],
                            callback=f'buy_{gun_name}' 
                        )
                
                
                if btn: self.buttons[row][col] = btn

    def can_buy(self, price):
        if price <= self.game.game_stats.money:
            self.game.game_stats.money -= price
            return True
        else:
            self.game.play_sound('not_money')
            return False
        
    def input(self):
        for row in self.buttons:
            for btn in row:
                btn: Button
                if btn and btn.is_clicked():
                    # Start wave
                    if btn.callback == 'next_wave':
                        self.game.change_state('gameplay')
                        self.game.game_paused = False
                        self.game.gameplay.start_wave_timer()
                        
                    # heal player
                    if btn.callback == 'heal_player':
                        if self.game.player.health != self.game.player.max_health:
                            if self.can_buy(self.game.game_stats.heal_price):
                                self.game.player.health = self.game.player.max_health
                                self.game.play_sound('heal')
                                
                    # ====== upgrades ======
                    if btn.callback == 'health_upgrade':
                        price = self.game.game_stats.get_upgrade_price('health')
                        if self.can_buy(price):
                            self.game.play_sound('skill_upgrade')
                            max_health = self.game.player.max_health == self.game.player.health
                            self.game.game_stats.health_upgrade += self.game.game_stats.health_upgrade_step
                            self.game.game_stats.update_skill_level()
                            self.game.player.max_health = self.game.game_stats.health_upgrade
                            if max_health:
                                self.game.player.health = self.game.game_stats.health_upgrade

                    if btn.callback == 'damage_upgrade':
                        price = self.game.game_stats.get_upgrade_price('damage')
                        if self.can_buy(price):
                            self.game.play_sound('skill_upgrade')
                            self.game.game_stats.damage_upgrade += self.game.game_stats.damage_upgrade_step
                            self.game.game_stats.update_skill_level()
                            self.game.current_gun.damage = self.game.game_stats.damage_upgrade

                    if btn.callback == 'speed_upgrade':
                        price = self.game.game_stats.get_upgrade_price('speed')
                        if self.can_buy(price):
                            self.game.play_sound('skill_upgrade')
                            self.game.game_stats.speed_upgrade += self.game.game_stats.speed_upgrade_step
                            self.game.game_stats.update_skill_level()
                            self.game.player.speed = self.game.game_stats.speed_upgrade

                    # ====== guns ======
                    if btn.callback.startswith(('select_', 'buy_')):
                        gun_name = btn.callback.split('_')[1]
                        if btn.callback.startswith('select_'):
                            self.game.change_gun(gun_name)
                        if btn.callback.startswith('buy_'):
                            price = self.all_guns[gun_name].price
                            if self.can_buy(price):
                                btn.image = self.game.buttons_frames[f'open_{gun_name}']
                                btn.custom_image = btn.image
                                btn.callback = f'select_{gun_name}'
                                self.game.available_weapons[gun_name] = self.all_guns[gun_name]
                                self.game.change_gun(gun_name)
                                self.game.play_sound('buy_gun')
                        # обновляем иконки
                        self.update_gun_buttons_icons()
        
        if pygame.key.get_just_pressed()[pygame.K_t]:
            self.game.game_stats.money += 100                    

    def update_gun_buttons_icons(self):
        for row in self.buttons:
            for btn in row:
                if btn and btn.callback.startswith(('select_', 'buy_')):
                    gun_name = btn.callback.split('_')[1]
                    if btn.callback.startswith('select_'):
                        if self.game.current_gun.gun_name == gun_name:
                            btn.image = self.game.buttons_frames[f'choosen_{gun_name}']
                        else:
                            btn.image = self.game.buttons_frames[f'open_{gun_name}']


    def draw_stats(self):
        
        font: pygame.Font = self.game.s_font
        color = (255, 255, 255)
        bttns_text_color = '#4B352A'
        
        col = 1
        start_row = 0
        line_spacing = 40

        base_btn = self.buttons[start_row][col]
        if base_btn:
            base_x = base_btn.rect.centerx
            base_y = base_btn.rect.bottom + line_spacing 
        else:
            base_btn = self.window_rect
            base_x = base_btn.center
            base_y = base_btn.center

        # Health upgrade
        self.health_level = self.game.game_stats.health_level = (self.game.game_stats.health_upgrade - 100) // self.game.game_stats.health_upgrade_step + 1
        
        health_text = font.render(f"Здоровье: {self.game.game_stats.health_level}", True, color)
        health_rect = health_text.get_rect(center=(base_x, base_y + line_spacing))
        self.display_surface.blit(health_text, health_rect)

        # Damage upgrade
        self.damage_level = self.game.game_stats.damage_level = (self.game.game_stats.damage_upgrade - 50) // self.game.game_stats.damage_upgrade_step + 1
        
        damage_text = font.render(f"Урон: {self.game.game_stats.damage_level}", True, color)
        damage_rect = damage_text.get_rect(center=(base_x, base_y + 2 * line_spacing))
        self.display_surface.blit(damage_text, damage_rect)

        # Speed upgrade
        self.speed_level = self.game.game_stats.speed_level = (self.game.game_stats.speed_upgrade - 150) // self.game.game_stats.speed_upgrade_step + 1
        
        speed_text = font.render(f"Скорость: {self.game.game_stats.speed_level}", True, color)
        speed_rect = speed_text.get_rect(center=(base_x, base_y + 3 * line_spacing))
        self.display_surface.blit(speed_text, speed_rect)


        
        # ===== skill upgrade prices & guns prices ======
        self.game.game_stats.next_upgrage_price()
        
        for row in range(0, 4):
            col = 2
            bttn = self.buttons[row][col]
            base_x = bttn.rect.centerx - 50
            base_y = bttn.rect.centery 
            if bttn.callback.split('_')[0] == 'heal':
                heal_text = font.render(f"{self.game.game_stats.heal_price}$", True, bttns_text_color)
                heal_rect = heal_text.get_rect(center=(base_x, base_y))
                self.display_surface.blit(heal_text, heal_rect)
            if bttn.callback.split('_')[0] == 'health':
                health_text = font.render(f"{self.game.game_stats.next_health_upgrade_price}$", True, bttns_text_color)
                health_rect = health_text.get_rect(center=(base_x, base_y))
                self.display_surface.blit(health_text, health_rect)
            if bttn.callback.split('_')[0] == 'damage':
                damage_text = font.render(f"{self.game.game_stats.next_damage_upgrade_price}$", True, bttns_text_color)
                damage_rect = damage_text.get_rect(center=(base_x, base_y))
                self.display_surface.blit(damage_text, damage_rect)
            if bttn.callback.split('_')[0] == 'speed':
                speed_text = font.render(f"{self.game.game_stats.next_speed_upgrade_price}$", True, bttns_text_color)
                speed_rect = speed_text.get_rect(center=(base_x, base_y))
                self.display_surface.blit(speed_text, speed_rect)


            col = 0
            bttn = self.buttons[row][col]
            base_x = bttn.rect.centerx
            base_y = bttn.rect.centery+30
            action, gun_name = bttn.callback.split('_') 
            if action == 'buy':
                gun_price = self.all_guns[gun_name].price
                if gun_price <= self.game.game_stats.money:
                    guns_price_text_color = "#2BCD3B"
                else:
                    guns_price_text_color = "#E21A1A"
                cost_text = font.render(f"{gun_price}$", True, guns_price_text_color)
                cost_rect = cost_text.get_rect(center=(base_x, base_y))
                self.display_surface.blit(cost_text, cost_rect)

        # ===== guns description =====
        for row in self.buttons:
            for btn in row:
                btn: Button
                if btn:
                    gun_name = btn.callback.split('_')[1]
                    # Обновляем иконку выбранного оружия
                    if btn.callback.startswith('select_'):
                        if self.game.current_gun.gun_name == gun_name:
                            btn.image = self.game.buttons_frames[f'choosen_{gun_name}']
                        else:
                            btn.image = self.game.buttons_frames[f'open_{gun_name}']
                        
                    if btn.was_hovered and btn.callback.startswith(('select_', 'buy_')):
                        alert_x = btn.rect.x - 20
                        alert_y = btn.rect.centery
                        text = self.all_guns[gun_name].description
                        draw_text_window(self.game.display_surface, (alert_x, alert_y), text)

    def draw(self):
        super().draw()
        self.draw_stats()
        
        # health & money
        self.game.states['gameplay'].draw_game_ui()
        
    def update(self, dt):
        super().update(dt)
        self.input()
        # обновляем иконки оружия
        self.update_gun_buttons_icons()
        
class GameOver(InGameWindow):
    state_name = 'game_over'
    music_state = 'gameplay'
    def __init__(self, game, title='GAME OVER', size=(400, 300)):
        super().__init__(game, title, size)
        
        
    def on_enter(self):
        super().on_enter()
        self.kills = self.game.game_stats.kills
        self.waves = self.game.game_stats.wave
        self.total = calculate_total_score(self.kills, self.waves)
        
        write_score(self.kills, self.waves, self.total)
        self.game.game_paused = True
        
    def create_buttons(self):
        # main menu
        self.menu_button = Button(
            groups=self.game.buttons_sprites,
            pos=(self.window_rect.x + self.window_rect.width//2, self.window_rect.y + self.window_rect.height//3 + 100),
            image=self.game.buttons_frames['menu']
        )
        
    def input(self):
        if self.menu_button.is_clicked():
            self.game.change_state('main_menu')
            self.game.reset_game()

    def draw_stats(self):
        
        font = self.game.s_font
        color = (255, 255, 255)

        kills = self.game.game_stats.kills
        waves = self.game.game_stats.wave
        total = calculate_total_score(kills, waves)
        
        line_spacing = 40
        base_x = self.window_rect.centerx


        # kills 
        base_y = self.window_rect.top + line_spacing*1 
        kills_text = font.render(f"Убийства: {self.kills}", True, color)
        kills_rect = kills_text.get_rect(center=(base_x, base_y))
        self.display_surface.blit(kills_text, kills_rect)
        
        # waves 
        base_y = self.window_rect.top + line_spacing*2 
        waves_text = font.render(f"Волны: {self.waves}", True, color)
        waves_rect = waves_text.get_rect(center=(base_x, base_y))
        self.display_surface.blit(waves_text, waves_rect)

        # total
        base_y = self.window_rect.top + line_spacing*3 
        total_text = font.render(f"Всего: {self.total}", True, color)
        total_rect = total_text.get_rect(center=(base_x, base_y))
        self.display_surface.blit(total_text, total_rect)


    def draw(self):
        super().draw()
        self.draw_stats()


    def update(self, dt):
        super().update(dt)
        self.input()