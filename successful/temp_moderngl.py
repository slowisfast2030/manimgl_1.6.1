import moderngl
import numpy as np
from PIL import Image

# Create a context
ctx = moderngl.create_standalone_context()

# Define the vertex shader code
vertex_shader = """
#version 330
in vec2 in_vert;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# Define the fragment shader code
fragment_shader = """
#version 330
out vec4 fragColor;
void main() {
    fragColor = vec4(0.0, 0.5, 0.0, 1.0);
}
"""

# Create a shader program
prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

# Define the vertices of a triangle
# 一个三角形
# vertices = np.array([
#     -0.6, -0.6,
#     0.6, -0.6,
#     0.0, 0.6,
# ], dtype=np.float32)

# 两个三角形
# vertices = np.array([
#     -0.6, -0.6,
#     0.6, -0.6,
#     0.0, 0.6,
#     -0.6, 0.6,
#     0.6, -0.6,
#     0.6, 0.6,
# ], dtype=np.float32)

# 正方形
# vertices = np.array([
#     -0.5, -0.5,
#     0.5, -0.5,
#     0.5, 0.5,
#     -0.5, 0.5,
# ], dtype=np.float32)

# 圆
import math

num_segments = 12
radius = 0.5

vertices = [0.0, 0.0]
for i in range(num_segments + 1):
    angle = 2.0 * math.pi * i / num_segments
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    vertices.extend([x, y])

vertices = np.array(vertices, dtype=np.float32)

# Create a vertex buffer object (VBO)
vbo = ctx.buffer(vertices)

# Create a vertex array object (VAO)
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

# Create a framebuffer object (FBO)
fbo = ctx.framebuffer(color_attachments=[ctx.texture((512, 512), 4)])

# Bind the FBO and clear the color buffer
fbo.use()
ctx.clear()

# Render the triangle
render_modes = [moderngl.TRIANGLES, moderngl.TRIANGLE_STRIP, moderngl.TRIANGLE_FAN]
image_names = ["triangles.png", "triangle_strip.png", "triangle_fan.png"]
for mode, name in zip(render_modes, image_names):
    vao.render(mode)

    # Read the rendered image from the FBO
    image = fbo.read(components=3)

    # Save the image to a file
    Image.frombytes('RGB', (512, 512), image).save(name)

print("all is well")