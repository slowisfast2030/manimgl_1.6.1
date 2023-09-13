from manimlib import *


class test(Scene):
	def construct(self): 
		plane = NumberPlane()
		self.add(plane)

		points = [[-2, -3, 0],
			      [0, 0, 0],
				  [2, 1, 0],
				  [3, 3, 0]]
		line = VMobject().set_points_smoothly(points, True).set_stroke(YELLOW, 5)	
		
		self.add(line)
		for point in points:
			dot = Dot(point)
			self.add(dot)

		rgbas = [
				 [0.95882272, 0.0277352,  0.061623,   1.        ],
                 [0.03781613, 0.96890806, 0.05165273, 1.        ],
                 [0.0795209,  0.03976045, 0.90007538, 1.        ],
				 ]
		line.set_rgba_array(rgbas, "stroke_rgba")
		line.set_stroke(width=[20,10.5,1, 
						       1,9.5,18,
							   18,9.5,1,
							   1,10.5,20, 
						       20,11,2,
							   2,9.5,17])	
		
		"""
		一个猜想:
		整个曲线分为6段, 每一段的stroke渲染的时候都会从rgbas和width数组拿到属于自己的颜色和线宽
		每一段的首尾像素都会得到自己的颜色和线宽, 中间部分会插值
		
		困惑:每一段衔接处有些不自然, 需要进一步研究stroke部分的着色器代码
		解答:需要为每一段曲线需要3个width值, 且上一段width的末尾和后一段width的开始要相等
		"""
		self.play(ShowCreation(line, run_time=3))
		#self.play(Write(line, run_time=3)) # 报错
		#print(len(line.get_points())//3) #6


class test_ani(Scene):
	def construct(self): 

		plane = NumberPlane()
		self.add(plane)

		points = [[-1, -1, 0],
					[0, 1, 0],
					[2, 1, 0],
					[3, 4, 0]]
		curve = VMobject().set_points_smoothly(points, True).set_stroke(YELLOW, 5)
		self.add(curve)
		# print(curve.get_points())
		# print(len(curve.get_points()))

		#self.play(VShowPassingFlash(Circle().scale(2), time_width=1, run_time=2))
		self.play(VShowPassingFlash(curve, time_width=1, run_time=2))
			
		