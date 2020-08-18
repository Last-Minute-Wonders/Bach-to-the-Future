self.curr_alpha += self.fade_spd
if self.forceDone:
	self.curr_alpha= 255
self.mask.set_alpha(self.curr_alpha)
# self.background= self.bg_copy.copy()
# self.background.blit(self.mask, (0, 0))
self.curr_alpha = min(self.curr_alpha, 255)
self.background.fill((0,0,0, self.curr_alpha))
if self.curr_alpha < 255:
	self.scriptsDone.append(False)