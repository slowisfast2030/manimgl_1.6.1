// Assumes the following uniforms exist in the surrounding context:
// uniform vec2 frame_shape;
// uniform float focal_distance;
// uniform float is_fixed_in_frame;

// 这里有隐患。如果想把屏幕的输出比例改为16: 9
// 如果不是固定的obj，没有影响
// 如果是固定的obj, 缩放比例有误
const vec2 DEFAULT_FRAME_SHAPE = vec2(8.0 * 16.0 / 9.0, 8.0);

// 定义了视锥, 当 -inf < z < focal_distance可见
// 假设focal_distance = 16
// 如果z = -16, focal_distance / (focal_distance - z) = 1/2 缩小2倍
// 如果z = 0,   focal_distance / (focal_distance - z) = 1   保持不变
// 如果z = 8,   focal_distance / (focal_distance - z) = 2   放大2倍
// 意味着, 在xoy平面的物体保持大小不变, xoy平面之下的缩小, xoy平面之上(小于焦距)的物体放大
float perspective_scale_factor(float z, float focal_distance){
    return max(0.0, focal_distance / (focal_distance - z));
}

// 相机空间 --> 裁剪空间 
vec4 get_gl_Position(vec3 point){
    vec4 result = vec4(point, 1.0);
    if(!bool(is_fixed_in_frame)){
        // 缩放到[-1, 1]的范围
        result.x *= 2.0 / frame_shape.x;
        result.y *= 2.0 / frame_shape.y;
        float psf = perspective_scale_factor(result.z, focal_distance);
        if (psf > 0){
            result.xy *= psf;
            // TODO, what's the better way to do this?
            // This is to keep vertices too far out of frame from getting cut.
            result.z *= 0.01;
        }
    } else{
        result.x *= 2.0 / DEFAULT_FRAME_SHAPE.x;
        result.y *= 2.0 / DEFAULT_FRAME_SHAPE.y;
    }
    result.z *= -1;
    return result;
}