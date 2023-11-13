from manimlib import *

class test(Scene):
    def construct(self):
        x1_tex = "\\vec{\\textbf{x}}_1"
        x2_tex = "\\vec{\\textbf{x}}_2"
        a1_tex = "\\vec{\\textbf{a}}_1"
        new_brown = interpolate_color(GREY_B, LIGHT_BROWN, 0.5)
        law = Tex(
            "F_1", "=", "m_1", a1_tex, "=",
            "G", "m_1", "m_2",
            "\\left({", x2_tex, "-", x1_tex, "\\over",
            "||", x2_tex, "-", x1_tex, "||", "}\\right)",
            "\\left({", "1", "\\over",
            "||", x2_tex, "-", x1_tex, "||^2", "}\\right)",
            tex_to_color_map={
                x1_tex: BLUE_C,
                "m_1": BLUE_C,
                x2_tex: new_brown,
                "m_2": new_brown,
                a1_tex: YELLOW,
            }
        )
        law.to_edge(UP)

        force = law[:4]
        constants = law[4:8]
        unit_vect = law[8:19]
        inverse_square = law[19:]
        parts = VGroup(
            force, unit_vect, inverse_square
        )

        words = VGroup(
            TexText("Force on\\\\mass 1"),
            TexText("Unit vector\\\\towards mass 2"),
            TexText("Inverse square\\\\law"),
        )

        self.add(law)

        # braces = VGroup()
        # rects = VGroup()
        # for part, word in zip(parts, words):
        #     brace = Brace(part, DOWN)
        #     word.scale(0.8)
        #     word.next_to(brace, DOWN)
        #     rect = SurroundingRectangle(part)
        #     rect.set_stroke(YELLOW, 1)
        #     braces.add(brace)
        #     rects.add(rect)

        # self.play(
        #     ShowCreationThenFadeOut(rects[0]),
        #     GrowFromCenter(braces[0]),
        #     FadeIn(words[0], UP)
        # )
        # self.wait()
        # self.play(
        #     ShowCreationThenFadeOut(rects[1]),
        #     GrowFromCenter(braces[1]),
        #     FadeIn(words[1], UP)
        # )
        # self.wait()
        # self.play(
        #     ShowCreationThenFadeOut(rects[2]),
        #     TransformFromCopy(*braces[1:3]),
        #     FadeIn(words[2], UP),
        # )
        # self.wait()