from sys import exit, platform as SYS_PLATFORM
import rgb
from os import listdir, path, environ, scandir, sep

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''
import pygame
from UIManager import ActionManager, TextLine, Sprite, TextBox
import csv
import vlc
from data_parser import get_config, ch_config, get_user_data, update_user_data, get_sys_config, get_achievements, \
	reset_config, get_users, new_user, get_curr_user, ch_user, del_user
from random import randint
from string import ascii_lowercase as ASCII_LOWERCASE, digits as DIGITS
import webbrowser as wb


class State_Manager:
	def __init__(self, config=get_config()):
		
		self.USER = get_curr_user()
		self.showHelp = False
		
		raw_paths = get_sys_config()
		self.ASSETS_DIR = path.join(*raw_paths["Assets"])
		self.WAV_DIR = path.join(*raw_paths["WAV Directory"])
		self.wav_files = {}
		for i in listdir(self.WAV_DIR):
			self.wav_files[i.rsplit('.', 1)[0]] = vlc.MediaPlayer(f"{self.WAV_DIR}{i}")
		self.curr_state = None
		pygame.display.init()
		pygame.font.init()
		
		self.SYSFONT = f"{self.ASSETS_DIR}ARCADE_R.TTF"
		
		pygame.display.set_caption("BACH TO THE FUTURE")
		self.icon = pygame.image.load(f"{self.ASSETS_DIR}quaver.png")
		pygame.display.set_icon(self.icon)
		self.fps_clock = pygame.time.Clock()
		
		self.SIZE = self.WIDTH, self.HEIGHT = 800, 600
		self.isFullScreen = eval(config["Fullscreen"]["Value"])
		if self.isFullScreen:
			self.screen = pygame.display.set_mode(self.SIZE, pygame.FULLSCREEN)
		else:
			self.screen = pygame.display.set_mode(self.SIZE)
		self.FPS = int(config["FPS"]["Value"])
		self.f_t = 1 / self.FPS
		self.time = 0
		self.lag = 0
		self.g_t = 0
		self.TRACKS_DIR = path.join(*raw_paths["CSV Directory"])
		
		self.bg_music = vlc.MediaPlayer(f"{self.ASSETS_DIR}Background.mp3")
		
		self.bg_vol= int(config["Background Volume"]["Value"])
		self.bg_music.audio_set_volume(self.bg_vol)
		self.bg_music.play()
	
	def update(self):
		self.curr_state.update(self.g_t, self.lag)
		self.curr_state.draw()
		pygame.display.update()
		self.time, self.lag = self.chk_slp()
		self.g_t += self.time
	
	def ch_state(self, new_state, args={}):
		self.curr_state.exit()
		print("Entering new state")
		self.curr_state = None
		self.curr_state = new_state
		self.curr_state.enter(args)
		self.g_t = 0
	
	def chk_slp(self):
		del_t = self.fps_clock.tick_busy_loop(self.FPS) / 1000 - self.f_t
		if del_t > 0:
			print(f"Lag : {del_t}s")
			
			return self.fps_clock.get_time() / 1000, del_t
		else:
			return self.fps_clock.get_time() / 1000, 0


class BaseState:
	def __init__(self, fsm):
		self.fsm = fsm
		self.action_manager = ActionManager()
		self.background = pygame.image.load(f"{self.fsm.ASSETS_DIR}background.png").convert()
	
	def enter(self, args):
		pass
	
	def exit(self):
		self.fsm.screen.blit(self.background, (0, 0))
	
	def update(self, game_time, lag):
		print("Updating base state")
	
	def draw(self):
		self.fsm.screen.fill(rgb.BLACK)
		self.fsm.screen.blit(self.background, (0, 0))
		self.action_manager.draw_buttons(self.fsm.screen)


class MainMenuState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.background = pygame.image.load(f"{self.fsm.ASSETS_DIR}menu_background.png").convert()
		self.action_manager.add_button("Campaign", (50, 50), (50, 30))
		self.action_manager.add_button("Chapter Select", (50, 100), (50, 30))
		self.action_manager.add_button("Arcade", (50, 150), (50, 30))
		self.action_manager.add_button("Sandbox", (50, 200), (50, 30))
		self.action_manager.add_button("Achievements", (50, 250), (50, 30))
		self.action_manager.add_button("Options", (50, 300), (50, 30))
		self.action_manager.add_button("About", (50, self.fsm.HEIGHT - 100), (50, 30))
		self.action_manager.add_button("Exit", (50, self.fsm.HEIGHT - 50), (50, 30), ret="Exit", key="escape")
		
		self.font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 22)
		self.user_text = TextLine(f"Welcome Back, {self.fsm.USER}!", self.font, (790, 10)).align_top_right()
		self.action_manager.add_button("Switch User", (670, 35), (20, 15), font=self.font, font_colour=rgb.WHITE)
		
		self.action_manager.add_keystroke('info', 'i')
		help_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 16)
		self.help_text = []
		self.help_text.append(
			TextLine("Press the 'I' key to toggle help messages!", help_font, (400, 10)).align_top_ctr())
		self.help_text.append(
			TextLine("Click on any button to navigate through the game!", help_font, (400, 30)).align_top_ctr())
		self.help_text.append(TextLine("Experience an exciting storyline!", help_font, (160, 83)).align_mid_left())
		self.help_text.append(
			TextLine("Quickly navigate between story chapters!", help_font, (235, 133)).align_mid_left())
		self.help_text.append(TextLine("Just play any song track!", help_font, (140, 183)).align_mid_left())
		self.help_text.append(TextLine("Modify any track to your liking!", help_font, (155, 233)).align_mid_left())
		self.help_text.append(TextLine("Check your achievements!", help_font, (215, 283)).align_mid_left())
		self.help_text.append(
			TextLine("Change default volume and keybindings, etc.", help_font, (145, 333)).align_mid_left())
		self.help_text.append(TextLine("View information about this game!", help_font, (125, 533)).align_mid_left())
		self.help_text.append(
			TextLine("(ESC) Quit this game... Why would you want to?", help_font, (165, 583)).align_mid_left())
	
	def enter(self, args):
		if not self.fsm.bg_music.is_playing():		
			self.fsm.bg_music.audio_set_volume(self.fsm.bg_vol)
			self.fsm.bg_music.play()
			
	def update(self, game_time, lag):
		events = pygame.event.get()
		actions = self.action_manager.chk_actions(events)
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			
			elif action == "Arcade":
				self.fsm.ch_state(SelectTrackState(self.fsm))
			
			elif action == "Options":
				self.fsm.ch_state(SettingsState(self.fsm))
			
			elif action == "Achievements":
				self.fsm.ch_state(AchievementsState(self.fsm))
			
			elif action == "About":
				self.fsm.ch_state(AboutState(self.fsm))
			
			elif action == "Campaign":
				from Storyline import StoryState
				self.fsm.ch_state(StoryState(self.fsm), {"file": "storyline1.json"})
			elif action == "Sandbox":
				self.fsm.ch_state(SandBoxState(self.fsm))
			elif action == "Chapter Select":
				self.fsm.ch_state(ChapterSelectState(self.fsm))
			
			elif action == "Switch User":
				self.fsm.ch_state(UsersState(self.fsm))
			
			elif action == 'info':
				self.fsm.showHelp = not self.fsm.showHelp
	
	def draw(self):
		super().draw()
		self.user_text.draw(self.fsm.screen)
		if self.fsm.showHelp:
			for i in self.help_text:
				i.draw(self.fsm.screen)


class UsersState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (50, 50), (20, 30))
		
		vert_offset = 0
		for i, user in enumerate(get_users()):
			self.action_manager.add_button(user, (350, 50 + i * 50), (100, 30), canScroll=True, ret=("Switch User", user))
			
			if i != 0:
				self.action_manager.add_button("Delete", (250, 50 + i * 50), (50, 30), canScroll=True, ret=("Delete User", user, 50 + i * 50))
				
			vert_offset += 50
		
		self.action_manager.add_button("New User", (400, 100 + vert_offset), (100, 30), canScroll=True, isCenter=True)
		
		self.action_manager.scroll_max = self.action_manager.scroll_buttons[-1].rect[1] - (self.fsm.HEIGHT // 4) * 3
		self.del_target= None
	
	def update(self, game_time, lag):
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "New User":
				self.fsm.ch_state(NewUserState(self.fsm))
			
			elif action == "Confirm delete":
				print(f"Deleting USER {action[1]}")
				
				if self.del_target == self.fsm.USER:
					print("Switching to Guest")
					ch_user("Guest")
					self.fsm.USER = "Guest"
				
				del_user(self.del_target)	
				self.fsm.ch_state(MainMenuState(self.fsm))		
	
			elif action[0] == "Switch User":
				ch_user(action[1])
				self.fsm.USER = action[1]
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action[0] == "Delete User":
				self.del_target= action[1]
				self.action_manager.add_button("Confirm", (140, action[2]-self.action_manager.scroll_pos), (20, 30), canScroll= True, ret= "Confirm delete")

	def draw(self):
		super().draw()


class NewUserState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (50, 50), (20, 30))
		
		self.action_manager.add_keystroke("backspace", "backspace")
		self.action_manager.add_keystroke("space", "space")
		self.action_manager.add_button("Confirm", (400, 350), (20, 30), key="return", isCenter=True)
		self.action_manager.add_keystroke("caps lock", "caps lock")
		
		self.valid_chars = ASCII_LOWERCASE + DIGITS
		
		for i in self.valid_chars:
			self.action_manager.add_keystroke(i, i)
		
		self.curr_str = ''
		self.input_font = self.font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 32)
		self.curr_input = TextLine(self.curr_str, self.input_font, (400, 300)).align_ctr()
		
		self.prompts = []
		self.prompts.append(TextLine("What is your name?", self.font, (400, 100)).align_ctr())
		
		self.isCaps = False
		
		self.error_text = None
	
	def update(self, game_time, lag):
		
		mod_mask = pygame.key.get_mods()
		self.isCaps = bool(mod_mask & pygame.KMOD_CAPS) ^ bool(mod_mask & pygame.KMOD_SHIFT)
		
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "backspace":
				self.error_text = None
				self.curr_str = self.curr_str[:-1]
				self.update_curr_str()
			
			elif action == "space":
				self.error_text = None
				self.curr_str += ' '
				self.update_curr_str()
			
			elif action == "Confirm":
				try:
					new_user(self.curr_str)
					ch_user(self.curr_str)
					self.fsm.USER = self.curr_str
					self.fsm.ch_state(MainMenuState(self.fsm))
				except:
					self.error_text = TextLine("Name already taken!", self.font, (400, 250),
					                           font_colour=rgb.RED).align_ctr()
			
			elif action in self.valid_chars:
				self.error_text = None
				self.curr_str += action.upper() if self.isCaps else action
				self.update_curr_str()
	
	def update_curr_str(self):
		self.curr_input = TextLine(self.curr_str, self.input_font, (400, 300)).align_ctr()
	
	def draw(self):
		super().draw()
		self.curr_input.draw(self.fsm.screen)
		for i in self.prompts:
			i.draw(self.fsm.screen)
		
		if self.error_text is not None:
			self.error_text.draw(self.fsm.screen)


class AboutState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		
		self.text_lines= []
		
		lines= [("Bach to the Future", 28), \
		  ("Orbital 2020", 28), \
		  ("Team Last Minute Wonders", 28), \
		  ("Members:", 28), \
		  ("Chen Mingyi", 18), \
		  ("Chen YiJia", 18), \
		  ("Advisor:", 28), \
		  ("Nicholas Lee", 18), \
		  ("Special Thanks to:", 28), \
		  ("Nicholas", 18), \
		  ("Lau Kuan Hoe", 18), \
		  ("Phua Kai Jie", 18), \
		  ("Hillson Hung", 18), \
		  ("For their patient testing and helpful feedback", 24), \
		  ("JoshuaPrzyborowski", 18), \
		  ("For providing the Windows FluidSynth build", 24), \
		  ("Icon made by Freepik from www.flaticon.com", 14)
			  ]
		
		y_pos= 50
		for str_val, size in lines:
			self.text_lines.append(TextLine(str_val, self.make_font(size), (400, y_pos)).align_ctr())
			y_pos += self.text_lines[-1].content.get_height() * 1 + 10


		self.action_manager.add_button("Back", (50, 50), (50, 30))
		
		self.action_manager.add_button("Exit", (50, self.fsm.HEIGHT - 100), (50, 30))
		
		self.action_manager.add_button("Website", (50, 100), (50, 30))
	
	def update(self, game_time, lag):
		
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "Website":
				wb.open_new_tab("https://github.com/Last-Minute-Wonders/Bach-to-the-Future")
	
	def draw(self):
		super().draw()
		for line in self.text_lines:
			line.draw(self.fsm.screen)

	def make_font(self, size):
		return pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", size)

class SelectTrackState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.tracks = listdir(self.fsm.TRACKS_DIR)
		des_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 14)
		self.des_lines = []
		self.highscores = get_user_data(self.fsm.USER)["Highscores"]
		self.best_grades = get_user_data(self.fsm.USER)["Max Grade"]
	
		for i, file in enumerate(sorted(self.tracks)):
			self.action_manager.add_button(file.rsplit('.', 1)[0], (325, i * 100 + 50), (50, 30), canScroll=True,
			                               ret=file)
			num_notes, song_dur, insts = self.songInfo(file.rsplit('.', 1)[0])
			self.des_lines.append(TextLine(f"Notes: {num_notes}, Duration: {song_dur}", des_font, (325, i * 100 + 83)))
			self.des_lines.append(TextLine(insts, des_font, (325, i * 100 + 98)))
			
			if file.rsplit('.', 1)[0] in self.highscores.keys():
				self.des_lines.append(
					TextLine(f"Highscore: {self.highscores[file.rsplit('.', 1)[0]]}", des_font, (325, i * 100 + 114)))
			if file.rsplit('.', 1)[0] in self.best_grades.keys():
				self.des_lines.append(
					TextLine(f"Best Grade: {self.best_grades[file.rsplit('.', 1)[0]]}", des_font, (325, i * 100 + 129)))
		
		for i in self.des_lines:
			self.action_manager.scroll_items.add(i)
		
		self.action_manager.scroll_max = self.action_manager.scroll_buttons[-1].rect[1] - (self.fsm.HEIGHT // 4) * 3
		
		self.action_manager.add_button("Back", (50, 50), (50, 30), ret="Back", key="backspace")
	
	def songInfo(self, csv_file):
		rel_path = path.join("beatmaps", csv_file) + ".csv"
		with open(rel_path, 'r') as file:
			reader = csv.reader(file)
			next(reader)
			info = next(reader)
		totalNotes = info[0]
		songLength = info[3]
		instrument = info[4]
		return (totalNotes, songLength, instrument)  # add spacing afterwards
	
	def update(self, game_time, lag):
		events = pygame.event.get()
		actions = self.action_manager.chk_actions(events)
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			elif action in self.tracks:
				print(f"Playing {action}")
				self.fsm.ch_state(PlayGameState(self.fsm), {"file_name": action})
	
	def draw(self):
		super().draw()
		for i in self.des_lines:
			i.draw(self.fsm.screen)


class SettingsState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (50, 50), (50, 30))
		self.action_manager.add_button("Exit (Esc)", (50, self.fsm.HEIGHT - 100), (50, 30), ret="Exit", key="escape")
		self.action_manager.add_button("Restore", (50, 150), (110, 30), ret="Restore defaults")
		self.action_manager.add_button("defaults", (50, 180), (110, 30), ret="Restore defaults")
		self.font = pygame.font.Font(self.fsm.SYSFONT, 15)
	
	def enter(self, args):
		self.settings = get_config()
		self.text = []
		self.text_lines = []
		
		for i, setting in enumerate(self.settings):
			val = self.settings[setting]["Value"]
			self.text_lines.append(TextLine(f"{setting} : {val}", self.font, (300, i * 45 + 30, 10, 10)))
			self.action_manager.add_button("Change", (200, i * 45 + 25), (30, 30), ret=setting)
	
	def update(self, game_time, lag):
		events = pygame.event.get()
		actions = self.action_manager.chk_actions(events)
		
		for action in actions:
			
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			elif action in self.settings:
				self.fsm.ch_state(ChSettingState(self.fsm), {"setting": action, "value": self.settings[action]})
			
			elif action == "Restore defaults":
				reset_config()
				self.fsm.bg_music.stop()
				self.fsm.__init__()
				self.fsm.curr_state = MainMenuState(self.fsm)
				self.fsm.ch_state(SettingsState(self.fsm))
	
	def draw(self):
		super().draw()
		
		for text_line in self.text_lines:
			text_line.draw(self.fsm.screen)


class ChSettingState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.font = pygame.font.Font(self.fsm.SYSFONT, 20)
		self.action_manager.add_button("Back", (50, 50), (50, 30))
	
	def enter(self, args):
		self.args = args
		self.setting = args["setting"]
		self.setting_text_line = TextLine(self.setting, self.font, (250, 50))
		self.val = args["value"]["Value"]
		self.val_text_line = TextLine(f"Current value : {self.val}", self.font, (250, 100))
		
		self.choices = args["value"]["Choices"]
		
		for e, i in enumerate(args["value"]["Choices"]):
			x_pos = 250
			y_pos = e * 50 + 150
			
			while y_pos >= 550:
				x_pos += 100
				y_pos -= 400
			self.action_manager.add_button(str(i), (x_pos, y_pos), (20, 30))
	
	def update(self, game_time, lag):
		events = pygame.event.get()
		
		actions = self.action_manager.chk_actions(events)
		
		for action in actions:
			if action == "Back":
				self.fsm.ch_state(SettingsState(self.fsm))
			elif action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			
			elif action in self.choices or eval(action) in self.choices:
				# print(f"Choice clicked : {eval(action)}")
				ch_config(self.setting, action)
				config2 = get_config()
				self.fsm.bg_music.stop()
				self.fsm.__init__(config2)
				self.fsm.curr_state = MainMenuState(self.fsm)
				self.fsm.ch_state(SettingsState(self.fsm))
	
	def draw(self):
		super().draw()
		self.setting_text_line.draw(self.fsm.screen)
		self.val_text_line.draw(self.fsm.screen)


class AchievementsState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (50, 50), (50, 30))
		self.name_font = pygame.font.Font(self.fsm.SYSFONT, 20)
		self.des_font = pygame.font.Font(self.fsm.SYSFONT, 14)
		
		self.text_lines = []
		hasAchieved = get_user_data(self.fsm.USER)["Achievements"]
		print(hasAchieved)
		achievements = get_achievements()
		for i, achievement in enumerate(achievements):
			font_col = rgb.GREEN if hasAchieved[achievement["name"]] else rgb.WHITE
			self.text_lines.append(
				TextLine(achievement["name"], self.name_font, (200, i * 80 + 50), font_colour=font_col))
			self.text_lines.append(
				TextLine(achievement["description"], self.des_font, (200, i * 80 + 85), font_colour=font_col))
	
	def update(self, game_time, lag):
		events = pygame.event.get()
		actions = self.action_manager.chk_actions(events)
		
		for action in actions:
			if action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			elif action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
	
	def draw(self):
		super().draw()
		
		for line in self.text_lines:
			line.draw(self.fsm.screen)


class ChapterSelectState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (50, 50), (20, 30))
		
		self.indexes = {1: 21, 2: 28, 3: 42, 4: 47, 5: 52, 6: 57, 7: 63, 8: 74, 9: 80, 10: 89, 11: 96, 12: 102, 13: 112,
		                14: 124}
		self.thumbnails = (
		(1, 1791, '1.png'), (2, 1800, '2.png'), (3, 1808, '3.png'), (4, 1828, '4.png'), (5, 1832, '5.png'), \
		(6, 1839, '6.png'), (7, 1858, '7.png'), (8, 1875, '8.png'), (9, 1876, '9.png'), (10, 1888, '10.png'), \
		(11, 1916, '11.png'), (12, 1957, '12.png'), (13, 1960, '13.png'), (14, 1713, '14.png'))
		
		self.sprites = []
		
		for i, year, pic in self.thumbnails:
			x_val = 300 if i % 2 > 0 else 600
			y_val = 250 + (i // 2 - 1) * 200 if i % 2 == 0 else 250 + (i // 2) * 200
			self.action_manager.add_button(f"Year {year}", (x_val, y_val), (20, 30), canScroll=True, isCenter=True,
			                               ret=i)
			self.sprites.append(Sprite(path.join("story_thumbnails", pic), (x_val, y_val - 155)).align_top_ctr())
		
		for i in self.sprites:
			self.action_manager.scroll_items.add(i)
		
		self.action_manager.scroll_max = self.action_manager.scroll_buttons[-1].rect[1] - (self.fsm.HEIGHT // 4) * 3
	
	def update(self, game_time, lag):
		actions = self.action_manager.chk_actions(pygame.event.get())
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action in self.indexes.keys():
				from Storyline import StoryState
				self.fsm.ch_state(StoryState(self.fsm), {"file": "storyline1.json", "curr_line": self.indexes[action]})
	
	def draw(self):
		super().draw()
		for i in self.sprites:
			i.draw_raw(self.fsm.screen)


class Orbs:
	def __init__(self, x, end_time, start_time, duration, lane, sustained, speed, offset, sustainTrim):
		self.x = x + 10
		self.tail_y = -end_time * speed + offset  # ensure sound always before visual, 0.1 reaction time
		self.head_y = -start_time * speed + offset
		self.length = duration * speed
		self.lane = lane
		self.sustained = sustained
		self.sustainTrim = sustainTrim
		
		# ASSETS
		raw_paths = get_sys_config()
		ASSETS_DIR = path.join(*raw_paths["Assets"])
		self.heads = [pygame.image.load(f"{ASSETS_DIR}lane1_orb.png").convert_alpha(), \
		              pygame.image.load(f"{ASSETS_DIR}lane2_orb.png").convert_alpha(), \
		              pygame.image.load(f"{ASSETS_DIR}lane3_orb.png").convert_alpha(), \
		              pygame.image.load(f"{ASSETS_DIR}lane4_orb.png").convert_alpha(), \
		              pygame.image.load(f"{ASSETS_DIR}lane5_orb.png").convert_alpha(), \
		              pygame.image.load(f"{ASSETS_DIR}lane6_orb.png").convert_alpha()]
		self.sustains = [pygame.image.load(f"{ASSETS_DIR}lane1_sustain.png").convert_alpha(), \
		                 pygame.image.load(f"{ASSETS_DIR}lane2_sustain.png").convert_alpha(), \
		                 pygame.image.load(f"{ASSETS_DIR}lane3_sustain.png").convert_alpha(), \
		                 pygame.image.load(f"{ASSETS_DIR}lane4_sustain.png").convert_alpha(), \
		                 pygame.image.load(f"{ASSETS_DIR}lane5_sustain.png").convert_alpha(), \
		                 pygame.image.load(f"{ASSETS_DIR}lane6_sustain.png").convert_alpha()]
	
	def blits(self):
		result = []
		if self.sustained:
			result.append([self.sustains[self.lane], \
			               [self.x + 12, self.tail_y + 30 + self.length * (1 - self.sustainTrim)], \
			               (0, 0, 36, self.length * self.sustainTrim)])
		result.append([self.heads[self.lane], [self.x, self.head_y]])
		return result


class PlayGameState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		config = get_config()
		self.backgrounds = (pygame.image.load(f"{self.fsm.ASSETS_DIR}play_background.png").convert(), \
		                    pygame.image.load(f"{self.fsm.ASSETS_DIR}play_background1.png").convert(), \
		                    pygame.image.load(f"{self.fsm.ASSETS_DIR}play_background2.png").convert(), \
		                    pygame.image.load(f"{self.fsm.ASSETS_DIR}play_background3.png").convert())
		self.background = self.backgrounds[0]
		self.curr_prog = 0
		self.fsm.screen.blit(self.background, (0, 0))
		self.load_font = pygame.font.Font(self.fsm.SYSFONT, 24)
		rand_msg_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 18)
		congrats_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}nighttraveler.otf", 42)
		TextBox(get_rand_msg(), rand_msg_font, (100, 230), (300, 10), rgb.BLACK).draw(self.fsm.screen)
		pygame.display.update()
		
		self.action_manager.add_keystroke("Back", "escape")
		self.action_manager.add_keystroke("Pause", "p")
		self.action_manager.add_keystroke("Vol+", "up")
		self.action_manager.add_keystroke("Vol-", "down")
		self.lineOfGoal = 500
		self.orb_spd = 450
		self.errorMargin = int(config["Accuracy Margin (Advanced)"]["Value"])
		self.rangeOfGoal = (self.lineOfGoal - self.orb_spd / self.fsm.FPS * self.errorMargin,
		                    self.lineOfGoal + self.orb_spd / self.fsm.FPS * self.errorMargin)
		self.sustainTrim = 0.8  # 1 for no Trim
		self.baseScore = 50
		self.meter_bar = pygame.image.load(f"{self.fsm.ASSETS_DIR}meter_bar.png").convert_alpha()
		
		self.orbs = []
		self.laneNo = int(config["Number of Lanes"]["Value"])
		pascal = [[280, 0, 0, 0, 0, 0], [240, 320, 0, 0, 0, 0], [200, 280, 360, 0, 0, 0], [160, 240, 320, 400, 0, 0],
		          [120, 200, 280, 360, 440, 0], [80, 160, 240, 320, 400, 480]]
		self.positions = pascal[self.laneNo - 1]
		self.grids = (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane_topblack.png").convert_alpha(), \
		              pygame.image.load(f"{self.fsm.ASSETS_DIR}lane_bottomblack.png").convert_alpha())
		self.gridBlits = [(pygame.image.load(f"{self.fsm.ASSETS_DIR}meter.png").convert_alpha(), (0, 0))]
		for i in range(self.laneNo):
			self.gridBlits.append((self.grids[i % 2], (self.positions[i], 0)))
		
		self.lanes = [(pygame.image.load(f"{self.fsm.ASSETS_DIR}lane1.png").convert_alpha(), (self.positions[0], 490)), \
		              (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane2.png").convert_alpha(), (self.positions[1], 490)), \
		              (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane3.png").convert_alpha(), (self.positions[2], 490)), \
		              (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane4.png").convert_alpha(), (self.positions[3], 490)), \
		              (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane5.png").convert_alpha(), (self.positions[4], 490)), \
		              (pygame.image.load(f"{self.fsm.ASSETS_DIR}lane6.png").convert_alpha(), (self.positions[5], 490))]
		self.laneBlits = self.lanes[:self.laneNo]
		
		
		key_list = [config[f"Lane {i + 1} key"]["Value"] for i in range(6)]
		
		self.key_bindings = key_list[:self.laneNo]
		self.key_binds = [eval(f"pygame.K_{x}") for x in self.key_bindings]
		for key in self.key_bindings:
			self.action_manager.add_sp_keystroke(key, key)
		
		self.score = 0
		self.streak = 0
		self.maxStreak = 0
		self.score_line = TextLine(str(int(self.score)), self.load_font, (680, 110)).align_ctr()
		self.streak_line = TextLine(str(self.streak), self.load_font, (680, 190)).align_ctr()
		self.congrats_msgs = (TextLine('Contrapuntal!', congrats_font, (320, 110), font_colour=rgb.YELLOW).align_ctr(), \
		                      TextLine('Polyphonic!', congrats_font, (320, 110), font_colour=rgb.YELLOW).align_ctr(), \
		                      TextLine('Fugue-tastic!', congrats_font, (320, 110), font_colour=rgb.YELLOW).align_ctr())
		self.congrats_sound = (vlc.MediaPlayer(f"{self.fsm.ASSETS_DIR}streak1.mp3"), \
		                       vlc.MediaPlayer(f"{self.fsm.ASSETS_DIR}streak2.mp3"), \
		                       vlc.MediaPlayer(f"{self.fsm.ASSETS_DIR}streak3.mp3"))
		self.congrats_timer = -1
		
		self.isPlaying = True
		self.countdown = self.fsm.FPS * 5
		self.start_timer = self.fsm.FPS * 3
		self.hasStarted = False
		self.start_timer_text = TextLine("", pygame.font.Font(self.fsm.SYSFONT, 48), (400, 300)).align_ctr()
	
	def enter(self, args):
		self.fsm.bg_music.stop()
		
		self.file = args["file_name"]
		print(f"File name = {self.file}")
		if "Story" in args.keys():
			self.story = True
			self.story_line = args["Story"]
		else:
			self.story = False
		file_path = f"{self.fsm.TRACKS_DIR}{self.file}"
		with open(file_path, 'r') as file:
			reader = csv.reader(file)
			next(reader)
			info = next(reader)
			next(reader)
			self.beatmap = [row for row in reader]
		
		self.sustainSnapshot = [False for _ in range(self.laneNo)]
		self.sustainValid = [False for _ in range(self.laneNo)]
		############################################################################
		# [[bool(input), source], [bool(correct), source], (x, y)]
		self.lane_responses = [[[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane1_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane1_correct.png").convert_alpha()], \
		                        (self.positions[0], 490)], \
		                       [[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane2_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane2_correct.png").convert_alpha()], \
		                        (self.positions[1], 490)], \
		                       [[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane3_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane3_correct.png").convert_alpha()], \
		                        (self.positions[2], 490)], \
		                       [[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane4_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane4_correct.png").convert_alpha()], \
		                        (self.positions[3], 490)], \
		                       [[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane5_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane5_correct.png").convert_alpha()], \
		                        (self.positions[4], 490)], \
		                       [[False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane6_press.png").convert_alpha()], \
		                        [False, pygame.image.load(f"{self.fsm.ASSETS_DIR}lane6_correct.png").convert_alpha()], \
		                        (self.positions[5], 490)]]
		self.lane_input = [False for _ in range(self.laneNo)]
		############################################################################
		
		reference_note = int(self.beatmap[0][3])
		initial_lane = 0
		first_note = True
		lane_history = {lane:0 for lane in range(self.laneNo)}
		
		self.max_prog = len(self.beatmap)
		
		for end_time, start_time, duration, pitch, sustained in self.beatmap:
			end_time = float(end_time)
			start_time = float(start_time)
			duration = float(duration)
			pitch = int(pitch)
			sustained = sustained == 'True'
			
			diff = pitch - reference_note
			lane = (initial_lane + diff) % self.laneNo
			check_overlap = diff and not first_note and sustained
			while check_overlap and not all(start_time < time for time in lane_history.values()):
				if diff > 0:
					lane = (lane + 1) % self.laneNo
				else:
					lane = (lane - 1) % self.laneNo
				if start_time > lane_history[lane]:
					break
			x = self.positions[lane]
			
			orb = Orbs(x, end_time, start_time, duration, lane, sustained, self.orb_spd, self.lineOfGoal,
			           self.sustainTrim)
			self.orbs.extend(orb.blits())
			reference_note = pitch
			initial_lane = lane
			lane_history[lane] = end_time
			if first_note:
				first_note = False
			self.load_update()
		
		# FULL SCORE CALCULATION
		totalNotes = int(info[0])
		sustainedNotes = int(info[1])
		totalSustainDuration = float(info[2]) * self.sustainTrim
		crotchet = float(info[8])
		self.fullScore = (totalNotes * self.baseScore) \
		                 + (totalSustainDuration / crotchet - sustainedNotes * crotchet) * self.baseScore / 2
		self.scorePercentage = 0
		
		wav_file = self.file.rsplit('.', 1)[0]
		self.player = self.fsm.wav_files[wav_file]
		self.volume = int(get_config()["Default Game Volume"]["Value"])
		self.player.audio_set_volume(self.volume)
	
	def update(self, game_time, lag):
		deltaTime = self.fsm.fps_clock.get_time() / 1000
		
		# TIMER EVENTS
		if self.start_timer < 0 and not self.hasStarted:
			self.player.play()
			self.hasStarted = True
			self.isPlaying = True
		elif self.start_timer >= 0:
			self.start_timer_text = TextLine(str(self.start_timer // self.fsm.FPS + 1),
			                                 pygame.font.Font(self.fsm.SYSFONT, 48), (400, 300)).align_ctr()
			self.start_timer -= 1
		if self.congrats_timer >= 0:
			self.congrats_timer -= 1
		
		# GAME BEGINS WHEN AUDIO BEGINS
		tapSnapshot = [False for _ in range(self.laneNo)]
		
		if self.player.is_playing() or self.player.get_position() > 0.95:
			# MOVEMENT
			increaseY = self.orb_spd * deltaTime
			for orb in self.orbs.copy():
				orb[1][1] += increaseY
				if orb[1][1] > self.fsm.HEIGHT:
					self.orbs.remove(orb)
		
		if self.player.is_playing():
			# COMPUTER VISION
			for orb in self.orbs:
				# orb = source, dest, area
				if len(orb) == 3 and (orb[1][1] - 30 + orb[2][3]) > self.lineOfGoal:
					# Check for the tail of a sustained note
					lane = self.positions.index(orb[1][0] - 22)
					self.sustainSnapshot[lane] = True
				if self.rangeOfGoal[0] < orb[1][1] < self.rangeOfGoal[1] and len(orb) == 2:
					# Check for a tap
					lane = self.positions.index(orb[1][0] - 10)
					tapSnapshot[lane] = True
				if len(orb) == 3 and (orb[1][1] - 30) > self.lineOfGoal:
					# Check for the head of a sustained note and terminate all boolean
					lane = self.positions.index(orb[1][0] - 22)
					self.sustainSnapshot[lane] = False
					self.sustainValid[lane] = False
			
			# SCORING
			for i in range(self.laneNo):
				if tapSnapshot[i] and self.lane_input[i]:
					# if there is AN ORB AT THE GOAL LINE and INPUT AT THAT LANE:
					self.lane_responses[i][1][0] = True  # fire animation
					self.sustainValid[i] = True  # VALID INPUT if it were a sustained note
					self.score += self.baseScore
					self.streak += 1
					if self.streak > self.maxStreak:
						self.maxStreak += 1
				elif self.lane_input[i] and not tapSnapshot[i]:
					# else if there is INPUT AT THAT LANE and NO ORBS AT THE GOAL LINE:
					self.streak = 0
				self.lane_input[i] = False  # invalidate input immediately
				if self.lane_responses[i][1][0]:
					# if there is a fire animation:
					self.lane_responses[i][1][0] = tapSnapshot[i] or self.sustainSnapshot[i]  # remove fire art once note has passed.
				if self.sustainSnapshot[i] and self.sustainValid[i] and self.lane_responses[i][0][0]:
					# if there is A SUSTAINED ORB AT THE GOAL LINE and a VALID INPUT and INPUT AT THAT LANE
					self.score += deltaTime * self.baseScore / 2
					self.lane_responses[i][1][0] = True  # fire animation
			
			# STREAK EFFECTS
			if self.streak == 30:
				self.congrats_sound[2].play()
				self.congrats_timer = self.fsm.FPS * 2
				self.background = self.backgrounds[3]
				self.congrats = self.congrats_msgs[2]
			elif self.streak == 20:
				self.congrats_sound[1].play()
				self.congrats_timer = self.fsm.FPS * 2
				self.background = self.backgrounds[2]
				self.congrats = self.congrats_msgs[1]
			elif self.streak == 10:
				self.congrats_sound[0].play()
				self.congrats_timer = self.fsm.FPS * 2
				self.background = self.backgrounds[1]
				self.congrats = self.congrats_msgs[0]
			elif self.streak == 0:
				self.background = self.backgrounds[0]
				for sound in self.congrats_sound:
					sound.stop()
		
		# INPUT CHECK
		actions = self.action_manager.chk_actions(pygame.event.get())
		for action in actions:
			for i in range(self.laneNo):
				if action == f"{self.key_bindings[i]} (down)":
					self.lane_responses[i][0][0] = True
					self.lane_input[i] = True
				elif action == f"{self.key_bindings[i]} (up)":
					self.lane_responses[i][0][0] = False
					self.lane_responses[i][1][0] = False
					self.lane_input[i] = False
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(SelectTrackState(self.fsm))
			elif self.hasStarted and action == "Pause" and self.isPlaying:
				self.player.pause()
				self.isPlaying = False
			elif self.hasStarted and action == "Pause" and not self.isPlaying:
				self.hasStarted = False
				self.start_timer = self.fsm.FPS * 3
			elif action == "Vol+":
				self.volume += 1
				self.player.audio_set_volume(self.volume)
				print(f"Volume : {self.player.audio_get_volume()}")
			elif action == "Vol-":
				self.volume = max(0, self.volume - 1)
				self.player.audio_set_volume(self.volume)
				print(f"Volume : {self.player.audio_get_volume()}")
		
		self.score_line = TextLine(str(int(self.score)), self.load_font, (680, 110)).align_ctr()
		self.streak_line = TextLine(str(self.streak), self.load_font, (680, 190)).align_ctr()
		self.scorePercentage = self.score / self.fullScore
		
		# SCORE REVIEW IN GAME OVER STATE
		if not self.orbs:
			self.countdown -= 1
			if self.countdown < 0:
				gradebook = {0: 'FAIL', 0.125: 'C', 0.375: 'B', 0.625: 'A', 0.875: 'S', 1: 'PERFECT'}
				percentages = list(gradebook.keys())
				for i in range(len(percentages) - 1):
					if percentages[i] <= self.scorePercentage < percentages[i+1]:
						grade = gradebook[percentages[i]]
						break
				if self.story:
					self.fsm.ch_state(GameOverState(self.fsm),
					                  {"file_name": self.file, \
					                   "score": int(self.score), \
					                   "accuracy_allowance": self.errorMargin, \
					                   "Story": self.story_line, \
					                   "Grade": grade, \
									   "max_streak": self.maxStreak})
				else:
					self.fsm.ch_state(GameOverState(self.fsm),
					                  {"file_name": self.file, \
					                   "score": int(self.score), \
					                   "accuracy_allowance": self.errorMargin, \
					                   "Grade": grade, \
					                   "max_streak": self.maxStreak})
	
	def exit(self):
		self.player.stop()
	
	def load_update(self):
		
		self.curr_prog += 1
		
		if self.curr_prog % 2 == 0:
			self.fsm.screen.blit(self.background, (0, 0))
			pygame.draw.rect(self.fsm.screen, rgb.GREEN, (0, 580, round(800 * self.curr_prog / self.max_prog), 20), 0)
			TextLine("Loading" + '.' * ((self.curr_prog % 40) // 10), self.load_font, (400, 550),
			         font_colour=rgb.GREEN).align_top_ctr().draw(self.fsm.screen)
			pygame.event.get()
			pygame.display.update([(0, 580, 800, 20), (160, 550, 450, 30)])
	
	def draw(self):
		super().draw()
		self.fsm.screen.blits(self.gridBlits)
		self.score_line.draw(self.fsm.screen)
		self.streak_line.draw(self.fsm.screen)
		self.fsm.screen.blits(self.orbs)
		self.fsm.screen.blits(self.laneBlits)
		
		for press, correct, position in self.lane_responses:
			if press[0]:
				self.fsm.screen.blit(press[1], position)
			if correct[0]:
				self.fsm.screen.blit(correct[1], position)
		self.fsm.screen.blit(self.meter_bar, (11, 499 - self.scorePercentage * 398),
		                     (0, 0, 28, self.scorePercentage * 398))
		pygame.draw.rect(self.fsm.screen, (248,146,17), (0, 590, round(800 * self.player.get_position()), 10), 0)
		
		if self.congrats_timer > 0:
			self.congrats.draw(self.fsm.screen)
		
		if not self.hasStarted:
			self.start_timer_text.draw(self.fsm.screen)


class GameOverState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		
		self.timer= 0
		self.timer1 = self.fsm.FPS * 2
		self.timer2 = self.fsm.FPS * 6
		self.timer3 = self.fsm.FPS * 8
		self.isDone= False
		self.action_manager.add_button("Retry", (200, 400), (50, 30), isCenter=True)
		self.action_manager.add_keystroke("Exit", "escape")
		self.high_scores = get_user_data(self.fsm.USER)["Highscores"]
		self.best_grades= get_user_data(self.fsm.USER)["Max Grade"]

		self.score_font = pygame.font.Font(self.fsm.SYSFONT, 24)
		self.grade_font = pygame.font.Font(self.fsm.SYSFONT, 64)
		self.high_score_text = TextLine("New Highscore!", self.score_font, (400, 350)).align_ctr()
		
		self.impact_sound = vlc.MediaPlayer(f"{self.fsm.ASSETS_DIR}impact.flac")
		self.grade_sound = vlc.MediaPlayer(f"{self.fsm.ASSETS_DIR}grade.flac")
	
	def enter(self, args):
		self.args = args
		
		self.score = args["score"]
		self.init_score= self.score
		self.max_streak= args["max_streak"]
		self.accuracy = args["accuracy_allowance"]
		self.streak_score = self.init_score * self.max_streak
		self.final_score= round(self.streak_score * (1 + (6-self.accuracy)/12))
		self.track = args["file_name"].rsplit('.', 1)[0]
		self.grade = args["Grade"]
		self.grade_text = TextLine(self.grade, self.grade_font, (600, 175)).align_ctr()
		
		if "Story" in args.keys():
			self.story = True
			self.story_line = args["Story"]
			self.action_manager.add_button("Continue", (550, 400), (50, 30), isCenter=True)
		
		else:
			self.action_manager.add_button("Back to Main Menu", (575, 400), (50, 30), ret="Main Menu", isCenter=True)
			self.action_manager.add_button("Back to Start", (350, 400), (50, 30), ret="Start", isCenter=True)
		
		
		
		self.score_line = TextLine(f"    Score : {self.score}", self.score_font, (25, 150))
		self.streak_line= TextLine(f"   Streak : {self.max_streak}", self.score_font, (25, 200))
		self.allowance_line = TextLine(f"Allowance : {self.accuracy}", self.score_font, (25, 250))
		
		self.track_line = TextLine(self.track, self.score_font, (400, 50)).align_ctr()
		
		if self.track in self.high_scores.keys():
			
			if self.high_scores[self.track] < self.score:
				print("High Score achieved!")
				self.isHighScore = True
				update_user_data(("Highscores", args["file_name"].rsplit('.', 1)[0]), args["score"], self.fsm.USER)
			else:
				print("High Score not achieved")
				self.isHighScore = False
		else:
			print("No previous high score found")
			self.isHighScore = True
			update_user_data(("Highscores", args["file_name"].rsplit('.', 1)[0]), args["score"], self.fsm.USER)	
		
		grade_map= {e:i for i, e in enumerate(["FAIL", 'C', 'B', 'A', 'S', "PERFECT"])}
		
		if self.track in self.best_grades.keys():
			if grade_map[self.best_grades[self.track]] < grade_map[self.grade]:
				print("High Grade achieved!")
				update_user_data(("Max Grade", args["file_name"].rsplit('.', 1)[0]), self.grade, self.fsm.USER)
		else:
			print("No previous grade found")
			update_user_data(("Max Grade", args["file_name"].rsplit('.', 1)[0]), self.grade, self.fsm.USER)
	
	def update(self, game_time, lag):
		events = pygame.event.get()
		
		actions = self.action_manager.chk_actions(events)
			
		for action in actions:
			if action == "Retry":
				self.fsm.ch_state(PlayGameState(self.fsm), self.args)
			
			elif action == "Main Menu":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "Start":
				self.fsm.ch_state(SelectTrackState(self.fsm))
			
			elif action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			
			elif action == "Continue":
				from Storyline import StoryState
				self.fsm.ch_state(StoryState(self.fsm), {"file": "storyline1.json", "curr_line": self.story_line})

		if self.timer <= self.timer3:
			self.timer += 1

		if self.timer2 > self.timer > self.timer1 and self.score < self.streak_score:
			self.score += max(round((self.streak_score - self.init_score)/ (self.fsm.FPS*3.5)), 1)
			self.score_line = TextLine(f"    Score : {self.score}", self.score_font, (25, 150))
		elif self.timer == self.timer2:
			self.impact_sound.stop()
			self.score_line = TextLine(f"    Score : {self.streak_score}", self.score_font, (25, 150))
		elif self.timer3 > self.timer > self.timer2 and self.streak_score != self.final_score:
			if self.streak_score < self.final_score:
				self.score += max(round((self.final_score - self.streak_score) / (self.fsm.FPS * 1.5)), 1)
			else:
				self.score += min(round((self.final_score - self.streak_score) / (self.fsm.FPS * 1.5)), -1)
			self.score_line = TextLine(f"    Score : {self.score}", self.score_font, (25, 150))
		elif self.timer > self.timer3:
			self.grade_sound.play()
			self.isDone = True
			self.score_line = TextLine(f"    Score : {self.final_score}", self.score_font, (25, 150))
	
	def draw(self):
		super().draw()
		self.score_line.draw(self.fsm.screen)
		if self.timer > self.timer1:
			self.impact_sound.play()
			self.streak_line.draw(self.fsm.screen)
		if self.timer > self.timer2:
			self.allowance_line.draw(self.fsm.screen)
		self.track_line.draw(self.fsm.screen)
		if self.isDone:
			self.grade_text.draw(self.fsm.screen)
			if self.isHighScore:
				self.high_score_text.draw(self.fsm.screen)


class SandBoxState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.platform = SYS_PLATFORM
		self.action_manager.add_button("Back", (50, 50), (50, 30))
		self.file_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Vera.ttf", 14)
		
		self.sprites = []
		self.error_text = None
		
		self.drive_font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Vera.ttf", 30)
		self.action_manager.add_button("Original Songs", (50, 100), (50, 30), font=self.drive_font)
		self.action_manager.add_button("Expansion Pack", (50, 150), (50, 30), font=self.drive_font)
		if self.platform == "win32":
			
			from psutil import disk_partitions
			
			self.drives = [disk.device for disk in disk_partitions(all=True)]
			
			for i, drive in enumerate(self.drives):
				self.action_manager.add_button(drive, (50, 200 + i * 50), (50, 30), font=self.drive_font)
		
		else:
			
			self.drives = [disk for disk in listdir("/Volumes")]
			
			for i, drive in enumerate(self.drives):
				self.action_manager.add_button(drive, (50, 200 + i * 50), (50, 30), font=self.drive_font)
	
	def enter(self, args):
		if "curr_dir" not in args.keys():
			self.curr_dir = sep
		else:
			self.curr_dir = args["curr_dir"]
		print(self.curr_dir)
		dir_entries = list(scandir(self.curr_dir))
		
		self.action_manager.add_button("..", (375, 50), (20, 14), canScroll=True, font=self.file_font)
		self.sprites.append(Sprite(f"{self.fsm.ASSETS_DIR}upfolder.png", (355, 50)))
		
		self.folders = sorted([i.name for i in dir_entries if i.is_dir()])
		curr_height = 0
		
		for i, folder in enumerate(self.folders):
			self.action_manager.add_button(folder, (375, i * 20 + 70), (20, 14), canScroll=True, font=self.file_font)
			self.sprites.append(Sprite(f"{self.fsm.ASSETS_DIR}folder.png", (355, i * 20 + 70)))
			curr_height += 20
		
		self.files = sorted([i.name for i in dir_entries if (
					i.is_file() and (i.name.rsplit('.', 1)[-1] == "mid" or i.name.rsplit('.', 1)[-1] == "midi"))])
		
		for i, file in enumerate(self.files):
			self.action_manager.add_button(file, (375, i * 20 + 70 + curr_height), (20, 14), canScroll=True,
			                               font=self.file_font)
			self.sprites.append(Sprite(f"{self.fsm.ASSETS_DIR}file.png", (355, i * 20 + 70 + curr_height)))
		
		for sprite in self.sprites:
			self.action_manager.scroll_items.add(sprite)
		
		self.action_manager.scroll_max = self.action_manager.scroll_buttons[-1].rect[1] - (self.fsm.HEIGHT // 4) * 3
	
	def update(self, game_time, lag):
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "..":
				file_path = path.join(self.curr_dir, action)
				self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": path.normpath(file_path)})
			
			elif action == "Original Songs":
				self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": path.join('.', 'master tracks')})
			
			elif action == "Expansion Pack":
				self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": path.join('.', "Expansion Pack")})
			
			elif action in self.drives:
				if self.platform == 'Windows':
					try:
						scandir(action)
						self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": action})
					except:
						self.error_text = TextLine("Access denied", self.drive_font, (120, 50), font_colour=rgb.RED)
				else:
					mac_action = path.join('/Volumes', action)
					try:
						scandir(mac_action)
						self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": mac_action})
					except:
						self.error_text = TextLine("Access denied", self.drive_font, (120, 50), font_colour=rgb.RED)
			
			elif action in self.folders:
				
				file_path = path.join(self.curr_dir, action)
				try:
					scandir(file_path)
					self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": path.normpath(file_path)})
				except:
					self.error_text = TextLine("Access denied", self.drive_font, (120, 50), font_colour=rgb.RED)
			
			elif action in self.files:
				file_path = path.join(self.curr_dir, action)
				self.fsm.ch_state(SandBoxOptionsState(self.fsm), {"file": path.normpath(file_path)})
	
	def draw(self):
		super().draw()
		for sprite in self.sprites:
			sprite.draw_raw(self.fsm.screen)
		if self.error_text is not None:
			self.error_text.draw(self.fsm.screen)


class SandBoxOptionsState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_button("Back", (700, 50), (50, 30))
		self.font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 30)
		self.font2= pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 24)
		self.vol_offset = 0
		self.quantize_val = 0
		self.tempo_val = 1
		self.simplify_val = False
		self.inst_val = set()
		self.instruments = []
		self.vol_thold = 0
	
	def enter(self, args):
		self.midi_file = args["file"]
		
		from mapGenerator1 import midiInfo
		self.instruments, self.vol_thold = midiInfo(self.midi_file)
		# =============================================================================
		# 		try:
		# 			from mapGenerator1 import midiInfo
		# 			print("midiInfo imported!")
		# 			self.instruments, self.vol_thold= midiInfo(self.midi_file)
		#
		# 		except:
		# 			print("FluidSynth not working!")
		# 			self.fsm.ch_state(ErrorState(self.fsm), {"err_msg" : "FluidSynth not working"})
		# =============================================================================
		
		self.txt_lines = []
		self.txt_lines.append(TextLine("Quantize", self.font, (50, 100)))
		self.txt_lines.append(TextLine("Tempo", self.font, (50, 200)))
		self.txt_lines.append(TextLine("Volume", self.font, (50, 300)))
		self.txt_lines.append(TextLine(f"Room to increase : {self.vol_thold}", self.font, (400, 300)).align_top_ctr())
		self.txt_lines.append(TextLine("Simplify", self.font, (50, 500), (20, 30)))
		self.txt_lines.append(TextLine("Instruments", self.font, (50, 600), (20, 30)))
		
		self.vol_text = TextLine(f"Current Volume offset : {self.vol_offset}", self.font, (400, 350)).align_top_ctr()
		
		self.insts_text = TextLine(f"Selected : {'All' if len(self.inst_val) == 0 else self.inst_val}", self.font,
		                           (400, 600)).align_top_ctr()
		
		for i, val in enumerate(["Off", '8', "16", "32", "12"]):
			self.action_manager.add_button(val, (i * 80 + 250, 100), (20, 30), canScroll=True, isCenter=True,
			                               ret=f"Quantize {val}", font=self.font)
		
		for i, val in enumerate([0.5, 0.75, 1, 1.5, 2]):
			self.action_manager.add_button(f"{val}x", (i * 80 + 250, 200), (20, 30), canScroll=True, isCenter=True,
			                               ret=f"Tempo {val}", font=self.font)
		
		for i, val in enumerate([1, 5, 10]):
			self.action_manager.add_button(f"+{val}", (i * 70 + 435, 400), (20, 30), canScroll=True, isCenter=True,
			                               ret=f"Vol + {val}", font=self.font)
			self.action_manager.add_button(f"-{val}", (-i * 70 + 365, 400), (20, 30), canScroll=True, isCenter=True,
			                               ret=f"Vol - {val}", font=self.font)
		
		self.action_manager.add_button("ON", (360, 500), (20, 30), canScroll=True, isCenter=True, ret="Simplify ON",
		                               font=self.font)
		
		self.action_manager.add_button("OFF", (440, 500), (20, 30), canScroll=True, isCenter=True, ret="Simplify OFF",
		                               font=self.font)
		
		self.action_manager.add_button("All", (220, 650), (20, 25), canScroll=True, ret="Instrument All",
		                               font=self.font2)
		
		for i, inst in enumerate(self.instruments):
			self.action_manager.add_button(inst, (220, i * 50 + 700), (20, 25), canScroll=True,
			                               ret=f"Instrument {i + 1}", font=self.font2)
		
		self.action_manager.add_button("Confirm", (300, self.action_manager.scroll_buttons[-1].rect[1] + 100), (20, 30),
		                               canScroll=True, isCenter=True, font=self.font)
		
		self.action_manager.scroll_max = self.action_manager.scroll_buttons[-1].rect[1] - (self.fsm.HEIGHT // 4) * 3
		
		self.action_manager.scroll_items.add(self.vol_text)
		self.action_manager.scroll_items.add(self.insts_text)
		for line in self.txt_lines:
			self.action_manager.scroll_items.add(line)
	
	def update(self, game_time, lag):
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(SandBoxState(self.fsm), {"curr_dir": path.split(self.midi_file)[0]})
				
			
			elif action.rsplit(' ', 1)[0] == "Vol +":
				self.vol_offset += int(action.rsplit(' ', 1)[1])
				v_pos = self.vol_text.rect[1]
				self.vol_text = TextLine(f"Current Volume offset : {self.vol_offset}", self.font,
				                         (400, v_pos)).align_top_ctr()
				self.action_manager.scroll_items.add(self.vol_text)
			
			elif action.rsplit(' ', 1)[0] == "Vol -":
				self.vol_offset -= int(action.rsplit(' ', 1)[1])
				v_pos = self.vol_text.rect[1]
				self.vol_text = TextLine(f"Current Volume offset : {self.vol_offset}", self.font,
				                         (400, v_pos)).align_top_ctr()
				self.action_manager.scroll_items.add(self.vol_text)
			
			elif action.rsplit(' ', 1)[0] == "Quantize":
				if action.rsplit(' ', 1)[1] == 'Off':
					self.quantize_val = 0
				else:
					self.quantize_val = int(action.rsplit(' ', 1)[1])
			
			elif action.rsplit(' ', 1)[0] == "Tempo":
				tempo_map= {0.5: 2, 0.75: 1.5, 1: 1, 1.5: 0.75, 2: 0.5}
				self.tempo_val = tempo_map[float(action.rsplit(' ', 1)[1])]
			
			elif action.rsplit(' ', 1)[0] == "Simplify":
				self.simplify_val = True if action.rsplit(' ', 1)[1] == "ON" else False
			
			elif action.rsplit(' ', 1)[0] == "Instrument":
				if action.rsplit(' ', 1)[1] == 'All':
					self.inst_val.clear()
				else:
					self.inst_val.add(int(action.rsplit(' ', 1)[1]))
				v_pos = self.insts_text.rect[1]
				self.insts_text = TextLine(f"Selected : {'All' if len(self.inst_val) == 0 else self.inst_val}",
				                           self.font, (400, v_pos)).align_top_ctr()
				self.action_manager.scroll_items.add(self.insts_text)
			
			elif action == "Confirm":
				self.fsm.screen.blit(self.background, (0, 0))
				TextLine("WORKING MAGIC FOR YOU, PLEASE WAIT!", self.font, (50, 250)).draw(self.fsm.screen)
				pygame.display.update()
				
				from mapGenerator1 import midiFunnel
				self.inst_val = [x - 1 for x in self.inst_val]
				midiFunnel(self.midi_file, self.quantize_val, self.simplify_val, self.tempo_val, self.vol_offset,
				           self.inst_val)
				self.fsm.bg_music.stop()
				self.fsm.__init__(get_config())
				self.fsm.curr_state = MainMenuState(self.fsm)
				self.fsm.ch_state(SelectTrackState(self.fsm))
	
	def draw(self):
		super().draw()
		self.vol_text.draw(self.fsm.screen)
		self.insts_text.draw(self.fsm.screen)
		for i in self.txt_lines:
			i.draw(self.fsm.screen)


class ExitState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
	
	def enter(self, args):
		print("Exiting program")
		pygame.quit()
		exit()


class ErrorState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.font = pygame.font.Font(f"{self.fsm.ASSETS_DIR}Helvetica.ttf", 48)
		
		self.action_manager.add_button("Back to Main Menu", (400, 400), (20, 30), isCenter=True)
	
	def enter(self, args):
		if "err_msg" in args.keys():
			self.err_msg = TextLine(args["err_msg"], self.font, (400, 200), font_colour=rgb.RED).align_ctr()
		
		else:
			self.err_msg = TextLine("An unexpected error occured.", self.font, (400, 200),
			                        font_colour=rgb.RED).align_ctr()
	
	def update(self, game_time, lag):
		actions = self.action_manager.chk_actions(pygame.event.get())
		
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back to Main Menu":
				self.fsm.ch_state(MainMenuState(self.fsm))
	
	def draw(self):
		super().draw()
		self.err_msg.draw(self.fsm.screen)


def get_rand_msg(msg_file="rand_msgs.txt"):
	with open(msg_file, 'r') as file:
		lines = file.read().splitlines()
	
	max_line = len(lines) - 1
	return lines[randint(0, max_line)]


if __name__ == "__main__":
	
	fsm = State_Manager()
	fsm.curr_state = MainMenuState(fsm)
	while True:
		fsm.update()
