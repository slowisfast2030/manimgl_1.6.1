#version 330

uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;
uniform float focal_distance;

// 这里是每一个像素的输入变量
// pixel的值是由vertex处的值插值得到的
in vec3 xyz_coords;
in vec3 v_normal;
in vec4 v_color;

out vec4 frag_color;

#INSERT finalize_color.glsl

void main() {
    frag_color = finalize_color(
        v_color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
}