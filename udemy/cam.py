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

		

		frame4 = frame.copy()
		frame4.set_width(15)
		frame4.set_euler_angles(theta=-10*DEGREES, phi=70*DEGREES)
		self.play(Transform(frame, frame4))
		#Rotating Camera (without updaters)
		for i in range(100):
			frame.increment_theta(0.01)
			self.wait(0.001)






