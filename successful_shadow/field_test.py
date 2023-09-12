from manimlib import *

def pendulum_vector_field_func(theta, omega, mu=0.3, g=9.8, L=3):
    return [omega, -np.sqrt(g / L) * np.sin(theta) - mu * omega]

#func = lambda pos: ((pos[0] * UR + pos[1] * LEFT) - pos) / 3

def field_func(x, y):
	return ((x * np.array((0, 1)) + y * np.array((-1, 0))) - np.array((x,y))) / 3	

#func = lambda pos: np.sin(pos[1]) * RIGHT + np.cos(pos[0]) * UP

def field_func2(x, y):
	return np.sin(y) * np.array([1,0]) + np.cos(x) * np.array([0,1])

class test(Scene):
	
	def construct(self): 
		
		plane = NumberPlane()
		self.add(plane)

		vector_field = VectorField(
			#pendulum_vector_field_func,
			field_func,
			plane,
			step_multiple=0.5,
            magnitude_range=(0, 3),
            length_func=lambda norm: 0.35 * sigmoid(norm)
		)
		vector_field.scale(0.8)
		self.add(vector_field)
		self.play(Write(vector_field, run_time=3))
		
		stream_lines = StreamLines(
			#pendulum_vector_field_func,
			field_func,
			plane
		)
		self.add(stream_lines)
		stream_lines.scale(0.9)
		
		asl = AnimatedStreamLines(stream_lines)
		self.add(asl)
		self.wait(6)