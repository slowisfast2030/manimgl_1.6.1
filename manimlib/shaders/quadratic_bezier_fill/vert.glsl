#version 330

#INSERT camera_uniform_declarations.glsl

/*
这里可以假设我们要绘制的是circle
在manim中，circle是由8段贝塞尔曲线组成的
每段贝塞尔曲线由3个控制点组成
因此，我们有24个控制点

这里我们需要假设:
我们不仅传入了每个点的坐标，还传入了每个点的法向量(可以提前计算出来)、颜色、索引

在surface的着色器代码中，每个点的法向量是在顶点着色器中计算出来的
*/
in vec3 point;
in vec3 unit_normal;
in vec4 color;
in float vert_index;

out vec3 bp;  // Bezier control point
out vec3 v_global_unit_normal;
out vec4 v_color;
out float v_vert_index;

// Analog of import for manim only
#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    v_global_unit_normal = rotate_point_into_frame(unit_normal);
    v_color = color;
    v_vert_index = vert_index;
}