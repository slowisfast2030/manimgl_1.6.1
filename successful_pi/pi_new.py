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
        #self.change_student_modes('happy', 'hooray', 'well')
        self.play(self.teacher.change_mode, 'happy')
        #self.teacher_says('Now we have emotions!')
        self.wait()
        #self.student_says('Hooray!', student_index=1, target_mode='hooray',
        #                  added_anims=[self.teacher.change, "hooray"])
        #self.play(self.teacher.change_mode, 'hooray')
        #self.wait(2)
        #self.play(RemovePiCreatureBubble(self.students[1]), self.students[1].change_mode, 'hooray')
        #self.wait(3)