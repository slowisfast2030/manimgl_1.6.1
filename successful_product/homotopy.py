import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        mob = Square().set_fill(RED, 1)
        pi_1 = PiCreature(color=RED).shift(UP*2)
        pi_2 = PiCreature(color=BLUE).shift(DOWN*2)

        plane = NumberPlane(height=16, width=20)
        plane.prepare_for_nonlinear_transform()
        plane.add(pi_1, pi_2)
        
        test_homotopy1 = lambda x, y, z, t: (
			x + interpolate(-3, 3, 2*t if t<=0.5 else 1),     # First 5 Seconds
			y + interpolate(0, 3, 2*(t-0.5) if t>0.5 else 0), # Next 5 Seconds
			z)

        test_homotopy2 = lambda x, y, z, t: (
            x + interpolate(-3, 3, 4*t if t<=0.25 else 1) 
                + interpolate(3, -3, 4*(t-0.5) if (t>=0.5 and t<=0.75) else (0 if t<=0.5 else 1)), 
            y + interpolate(-3, 3, 4*(t-0.25) if (t>0.25 and t<0.5) else (0 if t<=0.25 else 1)) 
                + interpolate(3, -3, 4*(t-0.75) if (t>0.75) else (0 if t<=0.75 else 1)), 
            z)
        
        def plane_wave_homotopy(x, y, z, t):
            norm = get_norm([x, y])
            tau = interpolate(5, -5, t) + norm/FRAME_X_RADIUS
            alpha = sigmoid(tau)
            #return [x, y + 0.5*np.sin(2*np.pi*alpha)-t*SMALL_BUFF/2, z]
            return [x, y + 0.5*np.sin(2*np.pi*alpha), z]
        

        self.play(Homotopy(plane_wave_homotopy, plane, run_time=3, rate_func=linear))
        #self.play(Homotopy(test_homotopy1, mob, run_time=10, rate_func=linear))

# 从coordinate_systems.py文件中借鉴
def prepare_for_nonlinear_transform_local(obj, num_inserted_curves: int = 100):
        for mob in obj.family_members_with_points():
            num_curves = mob.get_num_curves()
            if num_inserted_curves > num_curves:
                mob.insert_n_curves(num_inserted_curves - num_curves)
            mob.make_smooth_after_applying_functions = True
        return obj

class SquareToCircleHomotopy(Scene):
    def construct(self):
        # Create a square
        square = Square()
        # 非线性变换需要增加点集的数量
        square = prepare_for_nonlinear_transform_local(square)

        # Define the homotopy transformation function
        def square_to_circle_homotopy(x, y, z, t):
            # Calculate the distance from the origin
            distance = np.sqrt(x**2 + y**2)

            # Interpolate between the square and circle's points
            new_x = interpolate(x, x / distance, t)
            new_y = interpolate(y, y / distance, t)

            # Return the new coordinates
            return [new_x, new_y, z]

        # Apply the homotopy to transform the square into the circle
        self.play(Homotopy(square_to_circle_homotopy, square))

        # Keep the final state displayed
        self.wait(2)

