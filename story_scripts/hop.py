self.sp.rect[1]= min(round(self.sp.rect[1]+self.vel), 300)
self.vel += 4
if self.forceDone:
	self.sp.rect[1]= 300
if self.sp.rect[1] < 300:
	self.scriptsDone.append(False)