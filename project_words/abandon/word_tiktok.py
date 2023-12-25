import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/project_words/abandon')
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-linus-creatures")

from manimlib import *

from manim_imports_ext import *
from abandon_text import image_paths, student_words, meaning_sentence_dict
from alphabet_creature_upgrade import AlphabetCreature

# 整体下移的距离
down_shift = 0.5 * UP

# 三个小球在右上角的坐标
Mob1_coord = np.array([1.78, 6.7, 0.]) - down_shift
Mob2_coord = np.array([2.7, 6.7, 0.]) - down_shift
Mob3_coord = np.array([3.62, 6.7, 0.]) - down_shift

# 单词在左上角的坐标
Word_coord = np.array([-2.3, 6.8, 0]) - down_shift

# VT的坐标
VT_coord = np.array([-3.72, 5.81836484, 0.]) - down_shift

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

    # 这里打乱了顺序，是因为要给每个小正方形加上动画
    segments = random.sample(list(segments), num_rows*num_cols)
    segments = Group(*segments).space_out_submobjects(1.02)

    return segments

def get_image_anims(image_segments):

    # group对象不支持索引，所以要转换成list
    image_segments = list(image_segments)

    # 在翻转之前，先执行一次翻转
    for i in range(len(image_segments)):
        if i % 4 == 0:
            image_segments[i]= image_segments[i].rotate(TAU/2, UP).copy()
        elif i % 4 == 1:
            image_segments[i].rotate(TAU/4, OUT)
        elif i % 4 == 2:
            image_segments[i].rotate(TAU/4, IN)
        else:
            image_segments[i].rotate(TAU/2, OUT)

    anims = []
    for i in range(len(image_segments)):
        if i % 4 == 0:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/2, UP))
        elif i % 4 == 1:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/4, -OUT))
        elif i % 4 == 2:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/4, -IN))
        else:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/2, -OUT))

    return anims

# 传入三张图片的地址，返回3个小球
def three_sphere_with_texture(texture1, texture2, texture3):
    sphere1 = Sphere(radius=3)
    sphere2 = Sphere(radius=3)
    sphere3 = Sphere(radius=3)

    speed = 0.7

    def update_sphere_right(sphere, dt):
        sphere.rotate(speed * dt, axis=RIGHT)
    
    def update_sphere_up(sphere, dt):
        sphere.rotate(speed * dt, axis=UP)

    def update_sphere(sphere, dt):
        sphere.rotate(speed * dt)

    mob1 = TexturedSurface(sphere1, texture1).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob1.add_updater(update_sphere_right)

    mob2 = TexturedSurface(sphere2, texture2).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob2.add_updater(update_sphere_up)

    mob3 = TexturedSurface(sphere3, texture3).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob3.add_updater(update_sphere)

    mob_gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=1).shift(UP*2)

    return mob_gr

def student_with_teacher():
    colors = [BLUE, RED]
    student_teacher = [AlphabetCreature(r"$\Omega$", 
                             flip_at_start=False, 
                             start_corner=ORIGIN,
                             color=color,
                             eye_scale=0.3,
                             eye_buffer=0.12,
                             eye_prop=[0.5, 0.05]) for color in colors]
    student_teacher = VGroup(*student_teacher)
    student_teacher.arrange(RIGHT, buff=1.5).shift(DOWN*4.5).scale(0.8)
    student_teacher[0].shift(DOWN*0.3)

    _, teacher = student_teacher
    teacher.scale(1.3)

    return student_teacher

def meaning(parts, parts_ch, sents, sents_ch):
    # parts是单词含义的各个部分，每个部分都是一个str
    VT = Text("V-T", font_size=40, t2c={'V-T': RED})
    #VT = SVGMobject("svg-teapot.svg").scale(0.25)
    VT.move_to(VT_coord) 

    meaning_gr = [VT]

    # 英文释义
    for index, part in enumerate(parts):
        if index == 0:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={meaning_sentence_dict["word"]: BLUE}).set_width(7)
            meaning_en.next_to(VT, RIGHT)
            meaning_gr.append(meaning_en)

        elif index == len(parts)-1:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={meaning_sentence_dict["word"]: BLUE})
            meaning_en.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_en)

        else:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={meaning_sentence_dict["word"]: BLUE}).set_width(7)
            meaning_en.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_en)
    
    # 中文释义
    for index, part in enumerate(parts_ch):

        if index == len(parts_ch)-1:
            index = index + len(parts)

            meaning_ch = Text(part, 
                             font_size=36,
                             t2c={'放弃': BLUE})
            meaning_ch.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_ch)

        else:
            index = index + len(parts)

            meaning_ch = Text(part, 
                             font_size=36,
                             t2c={'放弃': BLUE}).set_width(7)
            meaning_ch.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_ch)

    
    # VT是释义的定位点，例句也需要一个定位点
    eg = Text("E.G.", font_size=40, t2c={'E.G.': BLUE})
    #eg = SVGMobject("svg-water-cup.svg").scale(0.3)
    eg_coord = VT_coord + (len(parts)+len(parts_ch))*DOWN*0.5 + DOWN * 0.2 # 0.2是调整的参数
    eg.move_to(eg_coord)
    sentence_gr = [eg]

    # 英文例句
    for index, sent in enumerate(sents):
        if index == 0:
            sentence = Text(sent, font_size=40, t2c={meaning_sentence_dict["word"]: BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT)
            sentence_gr.append(sentence)
        
        elif index == len(sents)-1:
            sentence = Text(sent, font_size=40, t2c={meaning_sentence_dict["word"]: BLUE})
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

        else:
            sentence = Text(sent, font_size=40, t2c={meaning_sentence_dict["word"]: BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)
    
    # 中文例句
    for index, sent in enumerate(sents_ch):
        if index == len(sents_ch)-1:
            index = index + len(sents)

            sentence = Text(sent, font_size=36, t2c={'抛弃': BLUE, "放弃": BLUE})
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

        else:
            index = index + len(sents)

            sentence = Text(sent, font_size=36, t2c={'抛弃': BLUE, "放弃": BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

    meaning_gr = Group(*meaning_gr)
    sentence_gr = Group(*sentence_gr)

    return Group(meaning_gr, sentence_gr)

    


class test(Scene):
    def construct(self):
        # 画出3个小球
        textures = image_paths
        mob_gr = three_sphere_with_texture(*textures)

        # 先把3个球放中间
        mob_gr = mob_gr.arrange(RIGHT, buff=1).shift(UP*2)
        self.add(mob_gr)

        # 画出学生和老师
        student_teacher = student_with_teacher()
        self.play(FadeIn(student_teacher))
        self.play(student_teacher[1].says("Today we will \nlearn " + meaning_sentence_dict["word"] + "!"))
        self.wait(1) 

        # 画出单词
        word = Text(meaning_sentence_dict["word"]).scale(2).move_to(Word_coord).set_color_by_gradient(RED, BLUE)
        mob1, mob2, mob3 = mob_gr  
        self.play(
            student_teacher[1].debubble(),
            mob1.animate.scale(0.4).move_to(Mob1_coord),
            mob2.animate.scale(0.4).move_to(Mob2_coord),
            mob3.animate.scale(0.4).move_to(Mob3_coord),
            Write(word),
            run_time=2
        )

        self.wait(0.5)

        # 清场，为第一个单词释义做准备
        self.clear()
        self.add(mob_gr, word, student_teacher)
        self.wait()

        # 单词的第一个释义出现
        # 给出中英文释义
        parts = meaning_sentence_dict["first_meaning"][0]
        parts_ch = meaning_sentence_dict["first_meaning"][1]
        sents = meaning_sentence_dict["first_sentence"][0]
        sents_ch = meaning_sentence_dict["first_sentence"][1]

        meaning_sentence = meaning(parts, parts_ch, sents, sents_ch)
        meaning_gr = meaning_sentence[0]
        sentence_gr = meaning_sentence[1]

        self.play(FadeIn(meaning_gr),
                  mob1.animate.set_opacity(1),
                  mob2.animate.set_opacity(0.2),
                  mob3.animate.set_opacity(0.2))
        
        self.play(
            *[Write(sent) for sent in sentence_gr])

        # 写完句子后，需要给出对话
        self.play(student_teacher[0].thinks(student_words[0]),
                  run_time=2,
                  )
        self.wait(1)
        # 删除对话 
        self.play(
            student_teacher[0].debubble(),
            FadeOut(student_teacher),
            )

        # 第一张图片
        image_boy = image_divide(image_paths[0], 10, 10).next_to(meaning_sentence, DOWN*2).space_out_submobjects(1.01).scale(1)
        self.add(*image_boy)

        image_anims = get_image_anims(image_boy)
        self.play(*image_anims, run_time=1.5)
        self.wait(1)

        # 清场，为第二个单词释义做准备
        #student_teacher[0].change_mode("plain")
        self.clear()
        self.add(mob_gr, word, student_teacher)
        self.wait()

        # 单词的第二个释义
        parts = meaning_sentence_dict["second_meaning"][0]   
        parts_ch = meaning_sentence_dict["second_meaning"][1]
        sents = meaning_sentence_dict["second_sentence"][0]
        sents_ch = meaning_sentence_dict["second_sentence"][1]

        meaning_sentence = meaning(parts, parts_ch, sents, sents_ch)
        meaning_gr = meaning_sentence[0]
        sentence_gr = meaning_sentence[1]

        self.play(FadeIn(meaning_gr),
                  mob1.animate.set_opacity(0.2),
                  mob2.animate.set_opacity(1),
                  mob3.animate.set_opacity(0.2))
        self.play(
            *[Write(sent) for sent in sentence_gr])

        # 写完句子后，需要给出对话
        self.play(student_teacher[0].thinks(student_words[1]),
                  run_time=2,
                  )
        # 删除对话 
        self.play(
            student_teacher[0].debubble(),
            FadeOut(student_teacher),
            )
        self.wait(1)

        # 第二张图片
        image_boy = image_divide(image_paths[1], 10, 10).shift(DOWN*3.5).space_out_submobjects(1.01).scale(1)
        #image_boy = image_divide("dall-house.png", 10, 10).next_to(meaning_sentence, DOWN*2).space_out_submobjects(1.01).scale(1)
        self.add(*image_boy)

        image_anims = get_image_anims(image_boy)
        self.play(*image_anims, run_time=1.5)
        self.wait(1)

        # 清场，为第三个单词释义做准备
        #student_teacher[0].change_mode("plain")
        self.clear()
        self.add(mob_gr, word, student_teacher)
        self.wait()

        # 单词的第三个释义
        parts = meaning_sentence_dict["third_meaning"][0]
        parts_ch = meaning_sentence_dict["third_meaning"][1]
        sents = meaning_sentence_dict["third_sentence"][0]   
        sents_ch = meaning_sentence_dict["third_sentence"][1]

        meaning_sentence = meaning(parts, parts_ch, sents, sents_ch)
        meaning_gr = meaning_sentence[0]
        sentence_gr = meaning_sentence[1]

        self.play(FadeIn(meaning_gr),
                  mob1.animate.set_opacity(0.2),
                  mob2.animate.set_opacity(0.2),
                  mob3.animate.set_opacity(1))
        self.play(
            *[Write(sent) for sent in sentence_gr])
        
        # 写完句子后，需要给出对话
        self.play(student_teacher[0].thinks(student_words[2]),
                  run_time=2,
                  )
        # 删除对话 
        self.play(
            student_teacher[0].debubble(),
            FadeOut(student_teacher),
            )
        self.wait(1)

        # 第三张图片
        image_boy = image_divide(image_paths[2], 10, 10).shift(DOWN*3.5).space_out_submobjects(1.01).scale(1)
        #image_boy = image_divide("dall-house.png", 10, 10).next_to(meaning_sentence, DOWN*2).space_out_submobjects(1.01).scale(1)
        self.add(*image_boy)

        image_anims = get_image_anims(image_boy)
        self.play(*image_anims, run_time=1.5)
        self.wait(1) 

        # 清场，为首尾准备
        self.clear()
        self.add(mob_gr, word)
        self.wait()

        # 收尾
        #self.play(word.animate.move_to(ORIGIN+UP*4))
        mob1.set_opacity(1)
        mob2.set_opacity(1)
        mob3.set_opacity(1)
        student_teacher.fix_in_frame()

        # 把所有单词的释义放在一起
        self.add(meaning_sentence.shift(DOWN))
        self.add(meaning_sentence.copy().shift(DOWN*4)) 
        self.add(meaning_sentence.copy().shift(DOWN*8))  

        self.play(
            mob_gr[0].animate.scale(2.5).move_to(-2*LEFT+DOWN*1+OUT*3),
            mob_gr[1].animate.scale(2.5).move_to(2*LEFT+DOWN*1+OUT*3),
            mob_gr[2].animate.scale(2.5).move_to(UP*2+OUT*3),
            run_time=2
        )

        word.fix_in_frame()

        frame = self.camera.frame
        
        def update_frame(frame, dt):
            frame.increment_theta(-0.3 * dt)
        frame.add_updater(update_frame)

        self.play(frame.animate.reorient(20, 70),
                  #word.animate.shift(DOWN*2), 
                  run_time=2)
        self.wait(7)
