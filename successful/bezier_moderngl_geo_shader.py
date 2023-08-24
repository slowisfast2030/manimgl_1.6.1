import moderngl
import numpy as np
from PIL import Image

# Initialize ModernGL context
ctx = moderngl.create_standalone_context()

# Vertex shader code
vertex_shader = """
#version 330
in vec2 in_position;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

# Geometry shader code
geometry_shader = """
#version 330
layout(points) in;
layout(line_strip, max_vertices = 100) out;

uniform int num_segments;

void main() {
    for (int i = 0; i <= num_segments; ++i) {
        float t = float(i) / float(num_segments);
        
        vec2 p0 = gl_in[0].gl_Position.xy;
        vec2 p1 = vec2(-0.6, 0.6);
        vec2 p2 = vec2(0.6, -0.6);
        vec2 p3 = gl_in[0].gl_Position.xy;
        
        vec2 position = p0 * pow(1.0 - t, 3.0)
                      + p1 * 3.0 * t * pow(1.0 - t, 2.0)
                      + p2 * 3.0 * t * t * (1.0 - t)
                      + p3 * pow(t, 3.0);
        
        gl_Position = vec4(position, 0.0, 1.0);
        EmitVertex();
    }
    
    EndPrimitive();
}
"""

# Fragment shader code
fragment_shader = """
#version 330
out vec4 out_color;

void main() {
    out_color = vec4(1.0, 0.0, 0.0, 1.0); // Red color
}
"""

# Compile shaders
program = ctx.program(vertex_shader=vertex_shader, geometry_shader=geometry_shader, fragment_shader=fragment_shader)

# Set up vertex buffer object
ctrl_points = np.array([[-0.8, -0.8], [-0.4, 0.4], [0.4, -0.4], [0.8, 0.8]], dtype=np.float32)
vbo = ctx.buffer(ctrl_points)
vao = ctx.simple_vertex_array(program, vbo, 'in_position')

# Set uniform values
program['num_segments'].value = 100

# Create framebuffer
fbo = ctx.framebuffer(color_attachments=[ctx.texture((800, 600), 4)])

# Bind the FBO and clear the color buffer
fbo.use()
ctx.clear()

vao.render(moderngl.LINE_STRIP)

# Read the framebuffer contents
image = fbo.read(components=3)
image = Image.frombytes('RGB', fbo.size, image).save("hello.png")

print("这个例子有问题，我不知道怎么解决")
