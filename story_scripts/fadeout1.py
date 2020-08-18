self.curr_alpha += self.fade_spd
if self.forceDone:
	self.curr_alpha= 255
self.mask.set_alpha(self.curr_alpha)
self.background= self.bg_copy.copy()
self.background.blit(self.mask, (0, 0))
if self.curr_alpha < 255:
	self.scriptsDone.append(False)