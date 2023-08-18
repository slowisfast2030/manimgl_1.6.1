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
		"""
		从实际效果来看
		theta是绕z轴旋转
		phi是绕y轴旋转

		假设camera距离世界坐标系的原点的距离是r
		那么camera运动的轨迹是一个以世界坐标系原点为圆心, 半径为r的圆
		"""
		frame2.set_euler_angles(theta=-30*DEGREES, phi=70*DEGREES)
		self.play(Transform(frame, frame2))
		#Rotating Camera (without updaters)
		for i in range(200):
			frame.increment_theta(0.01)
			self.wait(0.001)






