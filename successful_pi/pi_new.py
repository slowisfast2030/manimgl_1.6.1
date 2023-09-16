import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext_new import *

LEFT_EYE_INDEX: int = 0
RIGHT_EYE_INDEX: int = 1
LEFT_PUPIL_INDEX: int = 2
RIGHT_PUPIL_INDEX: int = 3
BODY_INDEX: int = 4
MOUTH_INDEX: int = 5

class NowWeHaveEmotions(TeacherStudentsScene):
    def construct(self):
        self.play(self.change_students('happy', 'hooray', 'well'))
        self.play(self.teacher.change_mode, 'happy')
        self.teacher_says('Now we have emotions!')
        
        self.wait()
        self.student_says('Hooray!', student_index=1, target_mode='hooray',
                         added_anims=[self.teacher.change, "hooray"])
        self.play(self.teacher.change_mode, 'hooray')
        self.wait(2)
        self.play(RemovePiCreatureBubble(self.students[2]), target_mode='hooray')
        self.wait(3)

class test(Scene):
    def construct(self):
        # p = NumberPlane()
        # self.add(p)

        modes = ('plain', 'sassy', 'happy', 'hooray', 'sad', 'thinking', 'confused',
                 'angry', 'speaking', 'pleading', 'shruggie', 'maybe', 'surprised',
                 'well', 'pondering', 'erm', 'raise_right_hand', 'raise_left_hand',
                 'guilty', 'hesitant', 'dance_kick', 'horrified', 'dance_1',
                 'dance_2', 'dance_3', 'gracious', 'tired')
        pi = PiCreature(mode='plain').scale(1)
        self.add(pi)
        for mode in modes:
            t = Text(mode).move_to(UP*2).scale(1)
            self.add(t)
            pi.change_mode(mode)
            self.wait(0.3)
            self.remove(t)


class test1(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       #pi.look_at(UP+LEFT)
       #pi.blink()
       #bubble = pi.get_bubble(content="hello")
       #self.add(bubble)
       #pi.shrug()
       self.play(pi.thinks("hello world"))
       #self.play(pi.replace_bubble("hi"))
       self.wait()
       #self.play(pi.change("happy"))
       self.wait()
