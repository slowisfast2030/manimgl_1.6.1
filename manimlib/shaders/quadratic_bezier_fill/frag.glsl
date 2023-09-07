#version 330

#INSERT camera_uniform_declarations.glsl

/*
vertex shader --> geometry shader --> rasterizer --> fragment shader
顶点着色器只能看到每个点, 片段着色器只能看到每个像素
几何着色器和光栅化器都能看到整个图元

引入几何着色器有两个目的：
目的一(次要): 将部分图元顶点数由3个变成5个
目的二(主要): 因为几何着色器可以看见整个图元，我们需要针对每个图元做些计算并将计算结果传给光栅化器和片段着色器
有些变量在图元范围内应该保持不变，比如uv_b2，不同的图元之间可以变化
这种功能只能由几何着色器实现(顶点着色器看不见整个图元)
*/

in vec4 color;
in float fill_all;  // Either 0 or 1
in float uv_anti_alias_width; // uv空间下的抗锯齿宽度

in vec3 xyz_coords;
in float orientation;
in vec2 uv_coords;
in vec2 uv_b2;
in float bezier_degree;

out vec4 frag_color;

// Needed for quadratic_bezier_distance insertion below
float modify_distance_for_endpoints(vec2 p, float dist, float t){
    return dist;
}

#INSERT quadratic_bezier_distance.glsl


float sdf(){
    /*
    在uv空间下，计算当前像素点uv_coords到贝塞尔曲线的最小距离

    Sdf stands for signed distance function, which is a mathematical construct that 
    computes the distance from a point to a surface, with the sign indicating whether 
    the point is inside or outside the surface.

    The term "signed" in Signed Distance Function refers to the fact that the function 
    can return both positive and negative values. It indicates not only the distance to
    the object but also whether the point is inside or outside the object.

    If the function returns a positive value, it means the point is outside the object.
    If it returns zero, the point is on the object's surface.
    If it returns a negative value, the point is inside the object.
    */

    if(bezier_degree < 2){
        return abs(uv_coords[1]);
    }
    float u2 = uv_b2.x;
    float v2 = uv_b2.y;
    // For really flat curves, just take the distance to x-axis
    if(abs(v2 / u2) < 0.1 * uv_anti_alias_width){
        return abs(uv_coords[1]);
    }
    // For flat-ish curves, take the curve
    else if(abs(v2 / u2) < 0.5 * uv_anti_alias_width){
        /*
        uv_coords: 当前像素点的uv坐标
        uv_b2: 贝塞尔曲线的第三个控制点（前两个固定在(0,0)和(0,1)，所以曲线的形状完全由uv_b2决定）
        */
        return min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    }
    // I know, I don't love this amount of arbitrary-seeming branching either,
    // but a number of strange dimples and bugs pop up otherwise.

    // This converts uv_coords to yet another space where the bezier points sit on
    // (0, 0), (1/2, 0) and (1, 1), so that the curve can be expressed implicityly
    // as y = x^2.
    mat2 to_simple_space = mat2(
        v2, 0,
        2 - u2, 4 * v2
    );
    vec2 p = to_simple_space * uv_coords;
    // Sign takes care of whether we should be filling the inside or outside of curve.
    float sgn = orientation * sign(v2);
    float Fp = (p.x * p.x - p.y);
    if(sgn * Fp < 0){
        return 0.0;
    }else{
        return min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    }
}


void main() {
    if (color.a == 0) discard;
    frag_color = color;
    if (fill_all == 1.0) return;
    /*
    当sdf() / uv_anti_alias_width < 0，返回1
    当sdf() / uv_anti_alias_width > 1，返回0
    当0 < sdf() / uv_anti_alias_width < 1，返回从0到1的平滑插值
    */
    frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);
}
