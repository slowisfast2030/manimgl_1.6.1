// Assumes the following uniforms exist in the surrounding context:
// uniform float is_fixed_in_frame;
// uniform vec3 camera_offset;
// uniform mat3 camera_rotation;

vec3 rotate_point_into_frame(vec3 point){
    if(bool(is_fixed_in_frame)){
        return point;
    }
    return camera_rotation * point;
}

// 世界坐标系 --> 相机坐标系
// camera_offset: 相机在世界空间中的位置
vec3 position_point_into_frame(vec3 point){
    if(bool(is_fixed_in_frame)){
        return point;
    }
    return rotate_point_into_frame(point - camera_offset);
}
