from manimlib import *

class test(Scene):
    def construct(self):
        self.add(self.matrix_multiplication())

    def matrix_multiplication(self):
        return Tex("""
            \\left[
                \\begin{array}{cc}
                    a & b \\\\
                    c & d
                \\end{array}
            \\right]
            \\left[
                \\begin{array}{cc}
                    e & f \\\\
                    g & h
                \\end{array}
            \\right]
            = 
            \\left[
                \\begin{array}{cc}
                    ae + bg & af + bh \\\\
                    ce + dg & cf + dh
                \\end{array}
            \\right]
        """)