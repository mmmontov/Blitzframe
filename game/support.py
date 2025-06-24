from settings import *
import time
import json
import os


class Timer:

	def __init__(self, duration, repeat = False, autostart = False, func = None):
		self.duration = duration
		self.start_time = 0
		self.active = False
		self.repeat = repeat
		self.func = func
		
		if autostart:
			self.activate()

	def __bool__(self):
		return self.active

	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		if self.repeat:
			self.activate()

	def update(self):
		if self.active:
			if pygame.time.get_ticks() - self.start_time >= self.duration:
				if self.func and self.start_time != 0: self.func()
				self.deactivate()
    

def folder_importer(*path):
	surfs = {}
	for folder_path, _, file_names in walk(join(*path)):
		for file_name in file_names:
			full_path = join(folder_path, file_name)
			surfs[file_name.split('.')[0]] = pygame.image.load(full_path).convert_alpha()
	return surfs

def audio_importer(*path): 
	audio_dict = {}
	for folder_path, _, file_names in walk(join(*path)):
		for file_name in file_names:
			audio_dict[file_name.split('.')[0]] = pygame.mixer.Sound(join(folder_path, file_name))
	return audio_dict

def transition_effect(surface: pygame.Surface, callback: callable, fade_speed=20, hold_time=0.3, draw_callback=None):
    clock = pygame.time.Clock()
    fade_overlay = pygame.Surface(surface.get_size()).convert_alpha()

    # затемнение
    for alpha in range(0, 256, fade_speed):
        if draw_callback:
            draw_callback()  
        fade_overlay.fill((0, 0, 0, alpha))
        surface.blit(fade_overlay, (0, 0))
        pygame.display.update()
        clock.tick(60)

    # фкнции
    callback()

    # Задержка
    fade_overlay.fill((0, 0, 0, 255))
    surface.blit(fade_overlay, (0, 0))
    pygame.display.update()
    start_time = time.time()
    while time.time() - start_time < hold_time:
        clock.tick(60)

    # осветление
    for alpha in range(255, -1, -fade_speed):
        if draw_callback:
            draw_callback() 
        fade_overlay.fill((0, 0, 0, alpha))
        surface.blit(fade_overlay, (0, 0))
        pygame.display.update()
        clock.tick(60)
    
        
class FadeText:
	"""
	Класс для плавного появления и исчезновения текста без блокировки основного цикла игры.
	Используйте методы start() и update(surface) в игровом цикле.
	"""

	def __init__(self, text, font, color, pos, appear_speed=5, hold_time=1.0, disappear_speed=5, background_draw=None):
		self.text = text
		self.font = font
		self.color = color
		self.pos = pos
		self.appear_speed = appear_speed
		self.hold_time = hold_time
		self.disappear_speed = disappear_speed
		self.background_draw = background_draw

		self.base_surf = self.font.render(self.text, True, self.color)
		self.text_surf = self.base_surf.convert_alpha()
		self.text_rect = self.text_surf.get_rect(center=self.pos)

		self.state = 'idle'  # 'appearing', 'holding', 'disappearing', 'done'
		self.alpha = 0
		self.start_time = 0

	def start(self):
		self.state = 'appearing'
		self.alpha = 0
		self.start_time = time.time()

	def update(self, surface):
		if self.state == 'idle' or self.state == 'done':
			return

		if self.background_draw:
			self.background_draw()

		if self.state == 'appearing':
			self.alpha += self.appear_speed
			if self.alpha >= 255:
				self.alpha = 255
				self.state = 'holding'
				self.start_time = time.time()
			self.text_surf.set_alpha(self.alpha)
			surface.blit(self.text_surf, self.text_rect)

		elif self.state == 'holding':
			self.text_surf.set_alpha(255)
			surface.blit(self.text_surf, self.text_rect)
			if time.time() - self.start_time >= self.hold_time:
				self.state = 'disappearing'

		elif self.state == 'disappearing':
			self.alpha -= self.disappear_speed
			if self.alpha <= 0:
				self.alpha = 0
				self.state = 'done'
			self.text_surf.set_alpha(self.alpha)
			surface.blit(self.text_surf, self.text_rect)


def calculate_total_score(kills, waves):
	kills_mul = 2
	waves_mul = 10
	return kills * kills_mul + waves * waves_mul

def load_json(filepath) -> dict:
	with open(filepath, 'r', encoding='utf-8') as f:
		return json.load(f)


def write_json(filepath, data):
	with open(filepath, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=4)

def write_score(kills, waves, total):
    path = join('settings', 'score.json')
    stats = {'kills': kills,
			'waves': waves,
			'total': total}
    score = load_json(path)
    if score:
        best_scores = list(score.values())
        best_scores.append(stats)
        best_scores.sort(reverse=True, key=lambda x: x['total'])
        if len(best_scores) > 10: del best_scores[-1]
        
    else:
        best_scores = [stats]
    
    score = {key: value for key, value in enumerate(best_scores, start=1)}
    write_json(path, score)
        
def create_score_json():
	path = join('settings', 'score.json')
	if not os.path.exists(path):
		write_json(path, {})