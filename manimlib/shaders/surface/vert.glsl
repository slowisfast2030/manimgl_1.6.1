#version 330

#INSERT camera_uniform_declarations.glsl

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 color;

out vec3 xyz_coords;
out vec3 v_normal;
out vec4 v_color;

#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl
#INSERT get_rotated_surface_unit_normal_vector.glsl

void main(){
    // 将点从世界坐标系转换到相机坐标系
    xyz_coords = position_point_into_frame(point);
    // 计算(point, du_point, dv_point)面在point处的法向量, 并将其转换到相机坐标系
    v_normal = get_rotated_surface_unit_normal_vector(point, du_point, dv_point);
    v_color = color;
    // 将点从相机坐标系转换到裁剪坐标系
    gl_Position = get_gl_Position(xyz_coords);
}