self.sp.rect[0]= min(800, self.sp.rect[0] + 10)
if self.forceDone:
	self.sp.rect[0]= 800
if self.sp.rect[0] < 800:
	self.scriptsDone.append(False)