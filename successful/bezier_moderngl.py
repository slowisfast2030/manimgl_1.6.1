import moderngl
import numpy as np
from PIL import Image

# Create a context
ctx = moderngl.create_standalone_context()

# Define the vertex shader code
vertex_shader = """
#version 330
in vec2 in_vert;
out vec4 v_color;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_color = vec4(0.5, 0.0, 0.0, 1);
}
"""

# Define the fragment shader code
fragment_shader = """
#version 330
in vec4 v_color;
out vec4 fragColor;
void main() {
    fragColor = v_color;
}
"""

# Create a shader program
prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

# 计算贝塞尔曲线上的点
def bezier_curve(points, num_segments):
    t = np.linspace(0, 1, num=num_segments)
    curve = np.zeros((num_segments, 2))
    for i in range(num_segments):
        curve[i] = (1 - t[i]) ** 3 * points[0] + 3 * (1 - t[i]) ** 2 * t[i] * points[1] + 3 * (1 - t[i]) * t[i] ** 2 * points[2] + t[i] ** 3 * points[3]
    return curve

# 定义控制点
points = np.array([[-0.8, -0.8], [-0.4, 0.4], [0.4, -0.4], [0.8, 0.8]])

# 计算曲线上的100个点
curve = bezier_curve(points, 100)

vertices = np.array(curve, dtype=np.float32)

# Create a vertex buffer object (VBO)
vbo = ctx.buffer(vertices)

# Create a vertex array object (VAO)
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

# Create a framebuffer object (FBO)
fbo = ctx.framebuffer(color_attachments=[ctx.texture((400, 500), 4)])

# Bind the FBO and clear the color buffer
fbo.use()
ctx.clear()

# Render the triangle
render_modes = [moderngl.POINTS, moderngl.LINES, moderngl.LINE_STRIP, moderngl.LINE_LOOP]
image_names = ["points.png", "lines.png", "line_strip.png", "line_loop.png"]

for mode, name in zip(render_modes, image_names):
    """
    vao和fbo之间的关系:
    vao --> vertex shader --> fragment shader --> fbo
    vao中有render所需要的所有资源
    render的结果会写入fbo

    A VAO is used to specify the input data for the vertex shader, while a FBO is 
    used to specify the output target for the fragment shader.
    """
    vao.render(mode)

    # Read the rendered image from the FBO
    image = fbo.read(components=3)

    # Save the image to a file
    Image.frombytes('RGB', fbo.size, image).save(name)

print("all is well")
print(fbo.size)
print(fbo.viewport)