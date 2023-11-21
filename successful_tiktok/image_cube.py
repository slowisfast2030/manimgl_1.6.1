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
        image_path = ImageMobject("dall-house.png")
        print(image_path.get_height())
        print(image_path.get_width())
        #image_house = ImageMobject("dall-house.png").scale(2)
        #image_boy = ImageMobject("dall-boy.png").scale(2)

        radius = image_path.get_height()/2
        image_path.move_to(radius * OUT)
        result = [image_path]
        result.extend([
            image_path.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
            for vect in compass_directions(4)
        ])
        result.append(image_path.copy().rotate(PI, RIGHT, about_point=ORIGIN))

        self.add(*result)   

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(30, 70), run_time=2)
        frame.add_updater(update_frame)

