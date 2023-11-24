import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

# 输入图片的路径，小正方形在长宽上的个数，返回这一系列小正方的集合
def image_divide(image_path, num_rows, num_cols):

    full_image = ImageMobject(image_path).scale(2)
    segments = []

    # Calculate the size of each segment
    img_height, img_width = full_image.get_height(), full_image.get_width()
    segment_height, segment_width = img_height / num_rows, img_width / num_cols

    for i in range(num_rows):
        for j in range(num_cols):
            # Calculate the position for each segment
            x = segment_width * (j - num_cols / 2 + 0.5)
            y = segment_height * (num_rows / 2 - i - 0.5)

            # Create a new ImageMobject for the segment
            segment = ImageMobject(image_path)
            segment.set_width(segment_width)
            segment.set_height(segment_height)
            segment.move_to(np.array([x, y, 0]))

            # Calculate and set im_coords
            left, right = j / num_cols, (j + 1) / num_cols
            top, bottom = i / num_rows, (i + 1) / num_rows
            segment.data["im_coords"] = np.array([(left, top), (left, bottom), (right, top), (right, bottom)])

            segments.append(segment)

    segments = random.sample(list(segments), num_rows*num_cols)
    # Display all the segments
    segments = Group(*segments).space_out_submobjects(1.02)
    return segments

class test(Scene):
    # CONFIG = {
    #     "camera_class": ThreeDCamera,
    # }

    def construct(self):

        sphere1 = Sphere(radius=3)
        sphere2 = Sphere(radius=3)
        sphere3 = Sphere(radius=3)

        def update_sphere_right(sphere, dt):
            sphere.rotate(0.3 * dt, axis=RIGHT)
        
        def update_sphere_up(sphere, dt):
            sphere.rotate(0.3 * dt, axis=UP)

        def update_sphere(sphere, dt):
            sphere.rotate(0.3 * dt)
    
        texture1 = "dall-boy.png"
        mob1 = TexturedSurface(sphere1, texture1).scale(0.3).rotate(PI/2, axis=RIGHT)
        mob1.add_updater(update_sphere_right)

        texture2 = "dall-house.png"
        mob2 = TexturedSurface(sphere2, texture2).scale(0.3).rotate(PI/2, axis=RIGHT)
        mob2.add_updater(update_sphere_up)

        texture3 = "dall-path.png"
        mob3 = TexturedSurface(sphere3, texture3).scale(0.3).rotate(PI/2, axis=RIGHT)
        mob3.add_updater(update_sphere)

        # 这3个小球在右上角的位置应该固定
        # gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=0.5).scale(0.4).move_to([2.7,6.7,0])
        # for mob in gr:
        #     print(mob.get_center())
        """
        [1.78 6.7  0.  ]
        [2.7 6.7 0. ]
        [3.62 6.7  0.  ]
        """
        gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=1).shift(UP*2)
        self.add(gr)

        colors = color_gradient([BLUE, GREEN], 2)
        pis = [PiCreature(color=color) for color in colors]
        pis[1].set_color(RED).scale(1.3).shift(UP*1.2)
        #pis[1].look_at(UL)
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT, buff=0.9).shift(DOWN*5.5).scale(0.8)
        self.play(FadeIn(pi_group))
        self.add(pi_group)
        self.play(pis[1].says("today, we will \nlearn abandon!"))
        self.wait(1)
        #pis[1].look_at(UP)

        # 单词出现
        word = Text("Abandon").scale(2).move_to([-2.3, 6.8,0]).set_color_by_gradient(RED, BLUE)

        self.play(
            pis[1].debubble(),
            mob1.animate.scale(0.4).move_to([1.78, 6.7,  0.  ]),
            mob2.animate.scale(0.4).move_to([2.7, 6.7, 0. ]),
            mob3.animate.scale(0.4).move_to([3.62, 6.7,  0.  ]),
            Write(word),
            run_time=2
        )
        self.wait(1)

        # 单词的第一个释义出现

        meaning_1 = Text("V-T If you abandon a place, thing, or person, you\n        leave the place, thing, or person permanently or for a long time, \n        especially when you should not do so.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_1.next_to(word, DOWN*2).shift(RIGHT*2.2)
        self.play(
            FadeIn(meaning_1),
            mob2.animate.set_opacity(0.2),
            mob3.animate.set_opacity(0.2),
            )
        sentence_1 = Text("\n•  He claimed that his parents had abandoned him.", font_size=40, t2c={'abandoned': BLUE})
        sentence_1.next_to(meaning_1, DOWN*2)
        self.play(Write(sentence_1))

        self.play(pis[0].thinks("what a lonely boy!"),
                  run_time=2,
                  )
        self.wait(1)


        # 导入第一个单词对应的图片
        self.play(pis[0].debubble())
        self.remove(pi_group)
        image_boy = image_divide("dall-boy.png", 10, 10).shift(DOWN*3).space_out_submobjects(1.03)
        self.add(*image_boy)
        image_boy = random.sample(list(image_boy), 10*10)
        # 在翻转之前，先执行一次翻转
        for i in range(len(image_boy)):
            if i % 4 == 0:
                image_boy[i]= image_boy[i].rotate(TAU/2, UP).copy()
            elif i % 4 == 1:
                image_boy[i].rotate(TAU/4, OUT)
            elif i % 4 == 2:
                image_boy[i].rotate(TAU/4, IN)
            else:
                image_boy[i].rotate(TAU/2, OUT)

        anims = []
        for i in range(len(image_boy)):
            if i % 4 == 0:
                anims.append(ApplyMethod(image_boy[i].rotate, TAU/2, UP))
            elif i % 4 == 1:
                anims.append(ApplyMethod(image_boy[i].rotate, TAU/4, -OUT))
            elif i % 4 == 2:
                anims.append(ApplyMethod(image_boy[i].rotate, TAU/4, -IN))
            else:
                anims.append(ApplyMethod(image_boy[i].rotate, TAU/2, -OUT))
        
        self.play(*anims, run_time=3)
        self.wait(1)
        

        
        




            