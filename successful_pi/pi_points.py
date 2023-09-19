import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext_new import *
import json


class write(Scene):
    def construct(self):
        # p = NumberPlane()
        # self.add(p)

        modes = ('plain', 'happy', 'sad')
        pi = PiCreature(mode='speaking')
        mob = pi
        
        eyes = mob.eyes
        left_iris = eyes[0][0]
        left_pupil = eyes[0][1]
        right_iris = eyes[1][0]
        right_pupil = eyes[1][1]
        mouth = mob.mouth

        self.add(mob, )
        data_to_write = {
            "happy": {
                "iris_left": left_iris.get_points().tolist(),
                "pupil_left": left_pupil.get_all_points().tolist(),
                "iris_right": right_iris.get_points().tolist(),
                "pupil_right": right_pupil.get_all_points().tolist(),
                "mouth": mouth.get_points().tolist()
                }
        }

        #print(data_to_write)
        file_path = "/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters/alphabet_points.json"
        with open(file_path, "w") as json_file:
            json.dump(data_to_write, json_file)
        
class read(Scene):
    def construct(self):
        file_path = "/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters/alphabet_points.json"
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        
        pi = PiCreature(mode='speaking')
        

        vm = VMobject()
        mouth_points = data['happy']['mouth']
        vm.set_points(mouth_points)
        vm.match_style(pi.mouth)


        self.add(vm)