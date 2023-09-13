from manimlib import *

class test(Scene):
	def construct(self): 
		plane = NumberPlane()
		self.add(plane)
		points = [[-2, -3, 0],
			      [0, 0, 0],
				  [2, 1, 0],
				  [3, 3, 0]]
		for point in points:
			dot = Dot(point)
			self.add(dot)

		line = VMobject().set_points_smoothly(points, True).set_stroke(YELLOW, 5)	
		rgbas = [
				 [0.95882272, 0.0277352,  0.061623,   1.        ],
                 [0.03781613, 0.96890806, 0.05165273, 1.        ],
                 [0.0795209,  0.03976045, 0.90007538, 1.        ],
				 ]
		line.set_rgba_array(rgbas, "stroke_rgba")
		line.set_stroke(width=[20,1,18,1])
		self.add(line)
		print(len(line.get_points())//3) #6
	    
    