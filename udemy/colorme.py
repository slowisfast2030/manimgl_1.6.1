from manimlib import *
import numpy as np
import random

class colorme(Scene):
	def construct(self): 
		text = Text("Color Functions I: set_color, set_opacity, set_gloss, set_shadow").scale(0.6)
		self.play(FadeIn(text))
		#self.wait(3)
		self.play(FadeOut(text))

		title = Text("Color Functions I: set_color, set_opacity, set_gloss, set_shadow").shift(UP*3.5).scale(0.6)
		self.play(FadeIn(title))

		stuff = []
		stuff.append( Text("This is text").shift(LEFT*4) )
		stuff.append(  Square(fill_opacity=1).set_color(YELLOW).shift(RIGHT*4) )
		stuff.append(  Rectangle(fill_opacity=1).set_color(GREEN).shift(DOWN*2) )
		stuff.append(  Sphere(fill_opacity=1).set_color(RED).shift(UP*2) )
		
		for i in stuff:
			i.generate_target()
		self.add(*stuff)
		self.wait(1)

		stuff[0].target.set_color(BLUE)
		stuff[1].target.set_opacity(0.5)
		stuff[2].target.set_gloss(1)
		stuff[3].target.set_shadow(10)
		

		for i in stuff:
			self.play(MoveToTarget(i))









