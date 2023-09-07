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
    在uv空间下，计算当前像素点uv_coords到贝塞尔曲线((0,0), (1,0), uv_b2)的最小距离

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
    // 贝塞尔曲线会经过uv_b2
    // 当满足abs(v2 / u2) < 0.1 * uv_anti_alias_width，说明uv_b2离x轴很近
    // 又因为贝塞尔曲线经过(0,0), 所以这条曲线近似于x轴 
    if(abs(v2 / u2) < 0.1 * uv_anti_alias_width){
        return abs(uv_coords[1]);
    }
    // For flat-ish curves, take the curve
    // 当有一些弯曲的时候
    else if(abs(v2 / u2) < 0.5 * uv_anti_alias_width){
        /*
        uv_coords: 当前像素点的uv坐标
        uv_b2: 贝塞尔曲线的第三个控制点（前两个固定在(0,0)和(1,0)，所以曲线的形状完全由uv_b2决定）
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
    当sdf() / uv_anti_alias_width < 0，返回1（曲线内部）
    当sdf() / uv_anti_alias_width > 1，返回0（曲线外部，且比较远）
    当0 < sdf() / uv_anti_alias_width < 1，返回从0到1的平滑插值（曲线外部，不太远）
    */
    frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);
}

/*
class glsl(Scene):
    def construct(self):
        frame = self.camera.frame
        frame.scale(0.5)
        plane = NumberPlane(x_range=(-2,2), y_range=(-2,2), width=8, height=8)
        self.add(plane)
        
        vm = VMobject()
        points = [[0,0,0], [1,0,0], [2.0,1.5,0]] 
        vm.set_points(np.array(points))
        vm.set_fill(GREEN, 1).set_stroke(WHITE, 0)
        self.add(vm)

        b0 = Dot(points[0]).set_color(RED).scale(0.5)
        b1 = Dot(points[1]).set_color(RED).scale(0.5)
        b2 = Dot(points[2]).set_color(RED).scale(0.5) 
        self.add(b0, b1, b2)

        vm.needs_new_triangulation = True
        print(vm.get_triangulation())
        self.wait()

通过不断调整points[3]的位置，可以模拟这里sdf函数的效果
通过在Camera类中修改anti_alias_width的大小，可以看出抗锯齿的效果

From chatgpt:
Anti-Aliasing Width: The "width" in anti-aliasing width refers to the extent of the blending or smoothing effect applied to the edges of objects. A wider anti-aliasing width results in a more significant reduction of jaggedness but can also introduce a slight blur to the image. The choice of anti-aliasing width depends on the specific rendering requirements and the desired trade-off between sharpness and smoothness.

阴差阳错地解决了另一个在心中停留很久的问题:
当对贝塞尔曲线进行填充的时候，究竟填充的是哪些区域？
*/