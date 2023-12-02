from manimlib import *

EQUATOR_STYLE = dict(stroke_color=TEAL, stroke_width=2)


def get_sphere_slices(radius=1.0, n_slices=20):
    delta_theta = TAU / n_slices
    north_slices = Group(*(
        ParametricSurface(
            uv_func=lambda u, v: [
                radius * math.sin(v) * math.cos(u),
                radius * math.sin(v) * math.sin(u),
                radius * math.cos(v),
            ],
            u_range=[theta, theta + delta_theta],
            v_range=[0, PI / 2],
            #resolution=(4, 25),
            resolution=(100, 100),
        )
        for theta in np.arange(0, TAU, delta_theta)
    ))
    north_slices.set_x(0)
    color_slices(north_slices)

    equator = Circle(**EQUATOR_STYLE)
    equator.insert_n_curves(100)
    equator.match_width(north_slices)
    equator.move_to(ORIGIN)
    equator.apply_depth_test()

    return Group(north_slices, get_south_slices(north_slices, dim=2), equator)

def get_flattened_slices(radius=1.0, n_slices=20, straightened=True):
    slc = ParametricSurface(
        # lambda u, v: [u * v, 1 - v, 0],
        lambda u, v: [u * math.sin(v * PI / 2), 1 - v, 0],
        u_range=[-1, 1],
        v_range=[0, 1],
        #resolution=(4, 25),
        resolution=(101, 101),
    )
    slc.set_width(TAU / n_slices, stretch=True)
    slc.set_height(radius * PI / 2)
    north_slices = slc.get_grid(1, n_slices, buff=0)
    north_slices.move_to(ORIGIN, DOWN)
    color_slices(north_slices)
    equator = Line(
        north_slices.get_corner(DL), north_slices.get_corner(DR),
        **EQUATOR_STYLE,
    )

    return Group(north_slices, get_south_slices(north_slices, dim=1), equator)

def color_slices(slices, colors=(BLUE_D, BLUE_E)):
    for slc, color in zip(slices, it.cycle([BLUE_D, BLUE_E])):
        slc.set_color(color)
    return slices

def get_south_slices(north_slices, dim):
    ss = north_slices.copy().stretch(-1, dim, about_point=ORIGIN)
    for slc in ss:
        slc.reverse_points()
    return ss

class test(Scene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)

        #slices = get_flattened_slices()
        slices = get_sphere_slices()
        self.add(slices)
        self.wait()
