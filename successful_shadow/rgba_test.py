from manimlib import *

class test(Scene):
	def construct(self): 
		plane = NumberPlane()
		self.add(plane)
		line = Line([-3,-3,0], [3,3,0])
		rgbas = [[0.95882272, 0.0277352,  0.061623,   1.        ]]	
		rgbas = [[0.95882272, 0.0277352,  0.061623,   1.        ],
                 [0.03781613, 0.96890806, 0.05165273, 1.        ],
                 [0.0795209,  0.03976045, 0.90007538, 1.        ]]
		line.set_rgba_array(rgbas, "stroke_rgba")
		line.set_stroke(width=[60,30,1.5])
		self.add(line)
	    
    