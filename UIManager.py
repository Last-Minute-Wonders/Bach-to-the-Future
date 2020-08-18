import rgb
import pygame
from data_parser import get_sys_config
from os import path
from vlc import MediaPlayer

pygame.font.init()

ASSETS_DIR= path.join(*(get_sys_config()["Assets"]))

def isWithin(point, rect):
	if point[0] > rect[0] and point[0] < (rect[0] + rect[2]):
		if point[1] > rect[1] and point[1] < (rect[1] + rect[3]):
			return True
	return False

class Button:
	def __init__(self, name, ret, pos, size, key, colour, font, font_colour, hl_colour, sel_colour):
		self.name= name
		self.coords= list(pos)
		self.size= list(size)
		self.rect= pygame.Rect(self.coords+self.size)
		self.key= key
		if ret is None:
			self.ret= name
		else:
			self.ret= ret
		self.def_colour= self.colour= colour
		self.font_colour= font_colour
		self.hl_colour= hl_colour
		self.sel_colour= sel_colour
		self.font= font
		self.text= font.render(self.name, True, self.font_colour)
		self.rect[2]= self.width= max(size[0], self.text.get_width())
		self.rect[3]= self.height= max(size[1], self.text.get_height())
	
	def align_ctr(self, pos= None):
		if pos is None:
			self.rect.centerx= self.rect.left
		else:
			self.rect.midtop= pos
		return self


class KeyStroke:
	def __init__(self, name, key, ret):
		self.name= name
		self.key= key
		if ret is None:
			self.ret= name
		else:
			self.ret= ret	

class SpKeyStroke(KeyStroke):
	def __init__(self, name, key, ret):
		super().__init__(name, key, ret)

class ActionManager:
	def __init__(self):
		ASSETS_DIR = path.join(*get_sys_config()['Assets'])
		self.press_sound = MediaPlayer(f"{ASSETS_DIR}BUTTONPRESS.mp3")
		self.buttons= []
		self.scroll_buttons= []
		self.keystrokes= []
		self.sp_keystrokes= []
		self.scroll_items= set()
		self.scroll_pos= 0
		self.scroll_min= 0
		self.scroll_max= 600
	
	def add_button(self, name, pos, size, ret=None, key= None, colour= rgb.BLACK, \
				font= pygame.font.Font(f"{ASSETS_DIR}Barcade-R4LM.otf", 22), \
					font_colour= rgb.YELLOW, hl_colour= rgb.GREY, sel_colour= rgb.GREEN, \
						canScroll= False, isCenter= False):
		if canScroll:
			
			if isCenter:
				self.scroll_buttons.append(Button(name, ret, pos, size, key, colour, font, font_colour, hl_colour, sel_colour).align_ctr())
			else:
				self.scroll_buttons.append(Button(name, ret, pos, size, key, colour, font, font_colour, hl_colour, sel_colour))
				
		else:
			
			if isCenter:
				
				self.buttons.append(Button(name, ret, pos, size, key, colour, font, font_colour, hl_colour, sel_colour).align_ctr())
			else:
				self.buttons.append(Button(name, ret, pos, size, key, colour, font, font_colour, hl_colour, sel_colour))
		
		if key != None:
			self.keystrokes.append(KeyStroke(name, key, ret))
	
	def add_keystroke(self, name, key, ret= None):
		self.keystrokes.append(KeyStroke(name, key, ret))
	
	def add_sp_keystroke(self, name, key, ret= None):
		self.sp_keystrokes.append(SpKeyStroke(name, key, ret))
	
	def chk_actions(self, events):
		curr_pos= pygame.mouse.get_pos()
		actions= []
		
		for event in events:
			
			if event.type== pygame.QUIT:
				actions.append("Exit")
	
			if event.type == pygame.MOUSEBUTTONDOWN:
	
				if event.button == 1:
	
					for button in self.buttons + self.scroll_buttons:
	
						if isWithin(curr_pos, button.rect):
							self.press_sound.play()
							button.colour= button.sel_colour
	
							print(f"Button \"{button.name}\" clicked, return value : \"{button.ret}\"")
							actions.append(button.ret)
	
					print(f"No buttons clicked! Cursor position : {curr_pos}")
				
				elif event.button == 4:
					print(f"Mouse Button 4 : Scroll up, scroll_pos : {self.scroll_pos}")

					if self.scroll_pos > self.scroll_min:
						self.scroll_pos -= 30
					
						for button in self.scroll_buttons:
							button.rect[1] += 30
						
						for item in self.scroll_items:
							item.rect[1] += 30
				
				elif event.button == 5:
					print(f"Mouse Button 5 : Scroll down, scroll_pos : {self.scroll_pos}")
					
					if self.scroll_pos < self.scroll_max:
						self.scroll_pos += 30
	
						for button in self.scroll_buttons:
							button.rect[1] -= 30
							
						for item in self.scroll_items:
							item.rect[1] -= 30

			# elif event.type == pygame.MOUSEBUTTONUP:
				# for button in self.buttons:
					# button.colour= button.def_colour

			elif event.type == pygame.KEYDOWN:
						
				for keystroke in self.keystrokes:
					if pygame.key.name(event.key) == keystroke.key:
						# print(f"Keystroke \"{keystroke.name}\" key \"{keystroke.key}\" pressed, return value : \"{keystroke.ret}\"")
						actions.append(keystroke.ret)

				for keystroke in self.sp_keystrokes:
					if pygame.key.name(event.key) == keystroke.key:
						pass
						# print(f"Special Keystroke \"{keystroke.name}\" key \"{keystroke.key}\" pressed, return value : \"{keystroke.ret}\" (down)")
						actions.append(f"{keystroke.ret} (down)")
				
			
			elif event.type == pygame.KEYUP:
				
				for keystroke in self.sp_keystrokes:
					if pygame.key.name(event.key) == keystroke.key:
						pass
						# print(f"Special Keystroke \"{keystroke.name}\" key \"{keystroke.key}\" depressed, return value : \"{keystroke.ret}\" (up)")
						actions.append(f"{keystroke.ret} (up)")
				
		
		for button in self.buttons + self.scroll_buttons:
			if isWithin(curr_pos, button.rect):
				button.colour= rgb.GREY
			else:
				button.colour= button.def_colour
		
		return actions
		
	def draw_buttons(self, screen):
		for button in self.buttons:
# 			text= button.font.render(button.name, 1, button.font_colour)
# 			text_len= text.get_width()
# 			button.rect[2]= max( ( text_len, button.rect[2]))
	
			pygame.draw.rect(screen, button.colour, button.rect)
			screen.blit(button.text, button.rect)
			
		for button in self.scroll_buttons:

			pygame.draw.rect(screen, button.colour, button.rect)
			screen.blit(button.text, button.rect)


class TextLine:
	def __init__(self, text, font, pos, size= (50, 50), font_colour= rgb.WHITE):
		self.content= font.render(text, True, font_colour)
		width= max(size[0], self.content.get_width())
		height= max(size[1], self.content.get_height())
		self.rect= pygame.Rect(pos[0], pos[1], width, height)
		
	def align_ctr(self, pos= None):
		if pos is None:
			self.rect.center= self.rect.topleft
		else:
			self.rect.center= pos
		
		return self
	
	def align_top_ctr(self, pos= None):
		if pos is None:
			self.rect.centerx= self.rect.left
		else:
			self.rect.midtop= pos
		
		return self

	def align_top_right(self, pos= None):
		if pos is None:
			self.rect.topright= self.rect.topleft
		else:
			self.rect.topright= pos
		
		return self
	
	def align_mid_left(self, pos= None):
		if pos is None:
			self.rect.midleft= self.rect.topleft
		else:
			self.rect.midleft= pos
		return self
	
	def draw(self, screen):
		screen.blit(self.content, self.rect)

		
class TextBox:
	def __init__(self, text, font, pos, size= (400, 50), font_colour= rgb.WHITE):
		words= text.split(' ')
		contents= []
		for word in words:
			word_img= font.render(''.join([word, ' ']), True, font_colour)
			contents.append(word_img)
			
		self.lines= []
		vert_offset= 0
		
		
		while len(contents) > 0:

			line_width= contents[0].get_width()
	
			max_height= contents[0].get_height()		
			
			line= [(contents[0], [pos[0], pos[1] + vert_offset, line_width, max_height])]
	
			contents.remove(contents[0])
			
			while line_width <= size[0] and len(contents) > 0:
				
				curr_width= contents[0].get_width()
				
				curr_height= contents[0].get_height()
				
				line.append( (contents[0], [pos[0] + line_width, pos[1] + vert_offset, curr_width, curr_height] ))
				
				line_width += curr_width
				
				max_height= max(max_height, curr_height)
				
				contents.remove(contents[0])
	
			self.lines.append(line)
			vert_offset += max_height
		self.rect= pygame.Rect((pos), (size[0], vert_offset))

	def align_ctr(self, pos= None):
		if pos is None:
			self.rect.center= self.rect.topleft
		else:
			self.rect.center= pos
		
		return self
	
	def draw(self, screen):
		
		for line in self.lines:
			for word in line:
				screen.blit(word[0], word[1])
		
class Sprite:
	def __init__(self, img, pos):
		self.img= pygame.image.load(img).convert_alpha()
		self.rect= pygame.Rect(pos, self.img.get_size())
	
	def draw(self, screen):
		screen.blit(self.img, (self.rect[0]-self.img.get_width() / 2, self.rect[1]-self.img.get_height() / 2))
		#screen.blit(self.img, self.img.get_rect().topleft)
	
	def draw_raw(self, screen):
		screen.blit(self.img, self.rect)
	
	def align_ctr(self, pos= None):
		if pos is None:
			self.rect.center= self.rect.topleft
		else:
			self.rect.center= pos
		
		return self
	
	def align_top_ctr(self, pos= None):
		if pos is None:
			self.rect.centerx= self.rect.left
		else:
			self.rect.midtop= pos
		
		return self		