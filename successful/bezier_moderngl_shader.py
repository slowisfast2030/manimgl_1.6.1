import moderngl
import numpy as np
import imageio # You can also use Pillow or other libraries

# Create a context
ctx = moderngl.create_standalone_context()

# Create a shader program
prog = ctx.program(
    vertex_shader='''
        #version 330

        in vec2 in_ctrl_point;
        out vec2 ctrl_point;

        void main() {
            ctrl_point = in_ctrl_point;
        }
    ''',
    geometry_shader='''
        #version 330

        layout (points) in;
        layout (line_strip, max_vertices = 100) out;

        in vec2 ctrl_point[];
        out vec2 pos;

        uniform float t;

        void main() {
            // Calculate the position of the curve point using Bernstein polynomials
            pos = pow(1 - t, 3) * ctrl_point[0] +
                  3 * pow(1 - t, 2) * t * ctrl_point[1] +
                  3 * (1 - t) * pow(t, 2) * ctrl_point[2] +
                  pow(t, 3) * ctrl_point[3];
            gl_Position = vec4(pos, 0.0, 1.0);
            EmitVertex();
            EndPrimitive();
        }
    ''',
)

# Create a vertex array with the control points
ctrl_points = np.array([
    [-0.8, -0.8],
    [-0.4, 0.8],
    [0.4, -0.8],
    [0.8, 0.8],
], dtype='f4')
vbo = ctx.buffer(ctrl_points)
vao = ctx.simple_vertex_array(prog, vbo, 'in_ctrl_point')

# Create a texture object to render to
tex = ctx.texture((512, 512), 4)
fbo = ctx.framebuffer(color_attachments=[tex])

# Render the curve by varying t from 0 to 1
fbo.use()
ctx.clear(1.0, 1.0, 1.0)
for i in range(100):
    t = i / 99
    prog['t'].value = t
    vao.render(moderngl.POINTS)

# Read the texture data and save it as an image file
data = tex.read()
imageio.imwrite('bezier_curve_shader.png', np.flipud(np.frombuffer(data, dtype=np.uint8).reshape(512, 512, 4)))
