from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''
import pygame
import rgb
from UIManager import TextLine, TextBox, Sprite
from state_manager import State_Manager, BaseState, ExitState, MainMenuState, PlayGameState
import json
import vlc
from data_parser import get_config

class StoryState(BaseState):
	def __init__(self, fsm):
		super().__init__(fsm)
		self.action_manager.add_keystroke("space", "space", ret= "Advance")
		self.action_manager.add_keystroke("enter", "return", ret= "Advance")
		self.action_manager.add_keystroke("Vol+", "up")
		self.action_manager.add_keystroke("Vol-", "down")
		self.font1= pygame.font.Font(self.fsm.SYSFONT, 22)
		self.font2= pygame.font.Font(self.fsm.SYSFONT, 14)
		self.title= TextLine("StoryState", self.font1, (400, 50)).align_ctr()
		self.curr_text= ""
		self.text_len= 0
		self.curr_text_box= TextBox(self.curr_text , self.font2, (50, 450), (700, 250))
		self.speaker_box= None
		self.speaker_text_line= None
		self.curr_frame= 0
		self.scripts= []
		self.isDone= True
		self.forceDone= False
	
	def enter(self, args):
		self.background.fill(rgb.BLACK)
		with open(args["file"]) as file:
			self.json_script= json.load(file)
		if "curr_line" in args.keys():
			self.curr_line= args["curr_line"]
		else:
			self.curr_line= 0
		self.max_line= len(self.json_script)
		self.volume= int(get_config()["Default Volume"]["Value"])

		self.players= {}
		self.sprites= {}
		if self.curr_line < self.max_line:
			self.advance(self.json_script[self.curr_line])

	def update(self, game_time, lag):
		actions= self.action_manager.chk_actions(pygame.event.get())
		for action in actions:
			if action == "Exit":
				self.fsm.ch_state(ExitState(self.fsm))
			elif action == "Back":
				self.fsm.ch_state(MainMenuState(self.fsm))
			
			elif action == "Vol+":
				self.volume += 1

				print(f"Volume : {self.volume}")
				for player in self.players.values():
					player.audio_set_volume(self.volume)
			
			elif action == "Vol-":
				self.volume= max(0, self.volume-1)

				print(f"Volume : {self.volume}")
				for player in self.players.values():
					player.audio_set_volume(self.volume)

			elif action == "Advance":
				if self.isDone:
					print("Advancing...")
					if self.curr_line >= self.max_line:
						print("Scene completed!")
						self.fsm.ch_state(MainMenuState(self.fsm))
					else:
						self.advance(self.json_script[self.curr_line])
				else:
					print("Fast forwarding...")
					self.forceDone= True
					self.curr_frame= self.text_len
		
		curr_text_pos= min(self.curr_frame, self.text_len)
		self.curr_text_box= TextBox(self.curr_text[:curr_text_pos] , self.font2, (50, 450), (700, 250))
		self.curr_frame += 1
		self.scriptsDone= []
		for script_code in self.scripts:
			exec(script_code)
		if self.curr_frame >= self.text_len and self.scriptsDone == []:
			self.isDone= True

	def advance(self, commands):
		self.curr_line += 1
		self.curr_frame= 0
		self.isDone= False
		self.forceDone= False
		self.scripts= []
		self.scriptsDone= []
		self.curr_text= ""
		self.speaker_text_line= None
		self.speaker_box= None
		for command in commands:
			print(command)
			if command["Type"] == "Title":
				self.title= TextLine(command["Text"], self.font1, (400, 50)).align_ctr()
			
			elif command["Type"] == "Speech":
				self.curr_text= command["Text"]
				
				if "Speaker" in command.keys():
					if "Right" in command.keys() and command["Right"]:
						speaker_text_pos= (self.fsm.WIDTH - 95, 420)
					else:
						speaker_text_pos= (95, 420)
					self.speaker_text_line= TextLine(command["Speaker"], self.font2, speaker_text_pos).align_top_ctr()
					
				else:
					self.speaker_text_line= None
					self.speaker_box= None
				
			elif command["Type"] == "Audio Start":

				self.players[command["File"]]= vlc.MediaPlayer("Sheep may safely graze.mp3")
				self.players[command["File"]].play()
			
			elif command["Type"] == "Audio Stop":
				if "File" in command.keys():
					self.players[command["File"]].stop()
					del self.players[command["File"]]
				else:
					for player in self.players.values():
						player.stop()	
					self.players= {}
			
			elif command["Type"] == "Script":
				
				with open(command["File"]) as script_file:
					script_code= script_file.read()
				self.scripts.append(script_code)
				exec(command["Init"])
				
			elif command["Type"] == "Background":
				with open("fadein.py") as script_file:
					script_code= script_file.read()
				self.scripts.append(script_code)
				self.curr_alpha= 0
				self.bg_copy= self.background.copy()
				self.fade_spd= 2
				self.mask= pygame.image.load(command["File"]).convert()
			
			elif command["Type"] == "Sprite":
				self.sprites[command["File"]]= Sprite(command["File"], eval(command["Pos"]))
			
			elif command["Type"] == "Enter Game":
				self.fsm.ch_state(PlayGameState(self.fsm), {"file_name" : f"{command['File']}.csv", "Story" : self.curr_line + 1})
			
		self.text_len= len(self.curr_text)
	
	def draw(self):
		self.fsm.screen.blit(self.background, (0,0))
		self.action_manager.draw_buttons(self.fsm.screen)
		self.title.draw(self.fsm.screen)
		self.curr_text_box.draw(self.fsm.screen)
		for sprite in self.sprites.values():
			sprite.draw(self.fsm.screen)
		if self.speaker_text_line is not None:
			self.speaker_text_line.draw(self.fsm.screen)
		if self.speaker_box is not None:
			self.speaker_box.draw(self.fsm.screen)
	
	def exit(self):
		for player in self.players.values():
			player.stop()
		self.players= {}


if __name__ == "__main__":
	
	fsm = State_Manager()
	fsm.curr_state = MainMenuState(fsm)
	fsm.ch_state(StoryState(fsm), {"file" : "storyline.json"})
	while True:
		fsm.update()