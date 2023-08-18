from manimlib import *
import numpy as np

class cam(ThreeDScene):
	def construct(self): 
		#Scene Material
		axes = ThreeDAxes()
		self.add(axes)
		title = Text("Camera").shift(UP*3.5)
		self.play(FadeIn(title))
		self.play(FadeIn(Square(fill_opacity=1).set_color(TEAL)))

		#Camera
		frame = self.camera.frame
		
		frame2 = frame.copy()
		frame2.set_width(15)
		frame2.set_euler_angles(theta=-30*DEGREES, phi=70*DEGREES)
		self.play(Transform(frame, frame2))
		#Rotating Camera (without updaters)
		for i in range(200):
			frame.increment_theta(0.01)
			self.wait(0.001)






