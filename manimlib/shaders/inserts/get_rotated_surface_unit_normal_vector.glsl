// Assumes the following uniforms exist in the surrounding context:
// uniform vec3 camera_offset;
// uniform mat3 camera_rotation;

// 计算point, du_point和dv_point三个点所构成平面的法向量
// 并将法向量从世界坐标系变换到相机坐标系
vec3 get_rotated_surface_unit_normal_vector(vec3 point, vec3 du_point, vec3 dv_point){
    vec3 cp = cross(
        (du_point - point),
        (dv_point - point)
    );
    if(length(cp) == 0){
        // Instead choose a normal to just dv_point - point in the direction of point
        vec3 v2 = dv_point - point;
        cp = cross(cross(v2, point), v2);
    }
    return normalize(rotate_point_into_frame(cp));
}