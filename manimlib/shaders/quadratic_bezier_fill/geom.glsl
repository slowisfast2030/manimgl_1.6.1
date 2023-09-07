#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float anti_alias_width; // 抗锯齿宽度

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;
// Needed for finalize_color
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

// 因为几何着色器处理的是整个图元
// 所以这里的每一个输入变量都是3份
in vec3 bp[3];
in vec3 v_global_unit_normal[3];
in vec4 v_color[3];
in float v_vert_index[3];

// 特别注意: 下面的输出变量对于图元中的每个顶点都会输出一次
out vec4 color;
out float fill_all;
out float uv_anti_alias_width;

out vec3 xyz_coords; // 这个变量没有用，应该是3b1b没有删除
out float orientation;
// uv space is where b0 = (0, 0), b1 = (1, 0), and transform is orthogonal
/*
从xyz空间映射到uv空间
bp[0] --> b0
bp[1] --> b1
存在一个变换矩阵(通过get_xyz_to_uv函数计算)
这个矩阵近似正交阵
存在模长缩放: 缩放比例length(bp[0] - bp[1]) / length((1,0) - (0,0)) = length(bp[0] - bp[1])
*/
out vec2 uv_coords;
out vec2 uv_b2;
out float bezier_degree;
/*
这里可以进一步分析下uv_coords和uv_b2
暂时忽略修改基元得到的5个顶点，仍然按照3个顶点分析
in(xyz space) -->         out(uv space) 
bz[0]         -->         uv_coords_0, uv_b2
bz[1]         -->         uv_coords_1, uv_b2
bz[2]         -->         uv_coords_2, uv_b2

小细节：在3个顶点的情况下
uv_coords_0就是uv_b0，既(0,0)
uv_coords_1就是uv_b1，即(0,1)

因为贝塞尔曲线的前两个控制点已经映射到了uv_b0(0,0)和uv_b1(0,1)
所以整个贝塞尔曲线完全由uv_b2决定
其实完全可以不做从xyz到uv空间的映射
通过我们锐利的观察: 这份代码中存在一个没有使用的变量: xyz_coords
我们完全可以猜测: 3b1b忘记删了
那么他为什么引入这个变量呢？因为完全可以替代uv空间
不过需要再添加一个变量xyz_coords[3]
示例如下:
in(xyz space) -->         out(xyz space) 
bz[0]         -->         [xyz_coords_0, xyz_coords_1, xyz_coords_2], xyz_coords_0 
bz[1]         -->         [xyz_coords_0, xyz_coords_1, xyz_coords_2], xyz_coords_1
bz[2]         -->         [xyz_coords_0, xyz_coords_1, xyz_coords_2], xyz_coords_2
经过光栅化器的插值，每个pixel
xyz_coords有两个属性
1. [xyz_coords_0, xyz_coords_1, xyz_coords_2]
2. interpolate([(xyz_coords_0, xyz_coords_1, xyz_coords_2)) 
和引入uv空间效果一样

经过光栅化器的插值，每个pixel
uv_coords: interpolate(uv_coords_0, uv_coords_1, uv_coords_2)
uv_b2: interpolate(uv_b2, uv_b2, uv_b2) = uv_b2
这样，每个pixel是可以知道在uv空间中的贝塞尔曲线((0,0), (1,0), uv_b2)和自己的坐标(uv_b2)
这样每个pixel就可以计算自己是否在贝塞尔曲线的内部
*/


// Analog of import for manim only
#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl


void emit_vertex_wrapper(vec3 point, int index){
    // 这里在几何着色器中计算光照，本质上是计算顶点的颜色
    // 而surface是在片段着色器计算光照，本质上是计算像素的颜色
    color = finalize_color(
        v_color[index],
        point,
        v_global_unit_normal[index],
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
    xyz_coords = point;
    gl_Position = get_gl_Position(xyz_coords);
    EmitVertex();
}


void emit_simple_triangle(){
    for(int i = 0; i < 3; i++){
        emit_vertex_wrapper(bp[i], i);
    }
    EndPrimitive();
}


void emit_pentagon(vec3[3] points, vec3 normal){
    vec3 p0 = points[0];
    vec3 p1 = points[1];
    vec3 p2 = points[2];
    // Tangent vectors
    vec3 t01 = normalize(p1 - p0);
    vec3 t12 = normalize(p2 - p1);
    // Vectors perpendicular to the curve in the plane of the curve pointing outside the curve
    vec3 p0_perp = cross(t01, normal);
    vec3 p2_perp = cross(t12, normal);

    bool fill_inside = orientation > 0;
    float aaw = anti_alias_width;
    vec3 corners[5];
    if(fill_inside){
        // Note, straight lines will also fall into this case, and since p0_perp and p2_perp
        // will point to the right of the curve, it's just what we want
        corners = vec3[5](
            p0 + aaw * p0_perp,
            p0,
            p1 + 0.5 * aaw * (p0_perp + p2_perp),
            p2,
            p2 + aaw * p2_perp
        );
    }else{
        corners = vec3[5](
            p0,
            p0 - aaw * p0_perp,
            p1,
            p2 - aaw * p2_perp,
            p2
        );
    }

    mat4 xyz_to_uv = get_xyz_to_uv(p0, p1, normal);
    uv_b2 = (xyz_to_uv * vec4(p2, 1)).xy;
    uv_anti_alias_width = anti_alias_width / length(p1 - p0);

    for(int i = 0; i < 5; i++){
        vec3 corner = corners[i];
        uv_coords = (xyz_to_uv * vec4(corner, 1)).xy;
        int j = int(sign(i - 1) + 1);  // Maps i = [0, 1, 2, 3, 4] onto j = [0, 0, 1, 2, 2]
        emit_vertex_wrapper(corner, j);
    }
    EndPrimitive();
}


void main(){
    // If vert indices are sequential, don't fill all
    fill_all = float(
        (v_vert_index[1] - v_vert_index[0]) != 1.0 ||
        (v_vert_index[2] - v_vert_index[1]) != 1.0
    );

    if(fill_all == 1.0){
        emit_simple_triangle();
        return;
    }

    vec3 new_bp[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), new_bp);
    vec3 local_unit_normal = get_unit_normal(new_bp);
    orientation = sign(dot(v_global_unit_normal[0], local_unit_normal));

    if(bezier_degree >= 1){
        emit_pentagon(new_bp, local_unit_normal);
    }
    // Don't emit any vertices for bezier_degree 0
}

