from manimlib import *

def compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray:
    angle = TAU / n
    return np.array([
        rotate_vector(start_vect, k * angle)
        for k in range(n)
    ])

print(compass_directions(4))
"""
RIGHT本身是[1,0,0], 经过4次旋转后得到: 
[1,0,0]
[0,1,0]
[-1,0,0]
[0,-1,0]
"""

class test(Scene):
    def construct(self):
        image_path = ImageMobject("dall-path.png").scale(1.5)
        image_house = ImageMobject("dall-house.png").scale(1.5)
        image_boy = ImageMobject("dall-boy.png").rotate(PI/2).scale(1.5)

        radius = image_path.get_height()/2
        image_path.move_to(radius * OUT)
        image_house.move_to(radius * OUT)
        image_boy.move_to(radius * OUT)

        result = [image_path]
        # result.extend([
        #     image_path.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
        #     for vect in compass_directions(4)
        # ])
        result.append(image_house.copy().rotate(PI/2, RIGHT, about_point=ORIGIN))
        result.append(image_boy.copy().rotate(PI/2, UP, about_point=ORIGIN))

        self.add(*result)   

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(60, 70), run_time=2)
        frame.add_updater(update_frame)

        self.wait(5)

