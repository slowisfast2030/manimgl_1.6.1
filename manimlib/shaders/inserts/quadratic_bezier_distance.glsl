// Must be inserted in a context with a definition for modify_distance_for_endpoints

// All of this is with respect to a curve that's been rotated/scaled
// so that b0 = (0, 0) and b1 = (1, 0).  That is, b2 entirely
// determines the shape of the curve

/*
假设 b0 = (0, 0) , b1 = (1, 0) , b2 = (x, y) ，
返回 b0, b1, b2 之间的二阶贝塞尔插值
*/
vec2 bezier(float t, vec2 b2){
    // Quick returns for the 0 and 1 cases
    if (t == 0) return vec2(0, 0);
    else if (t == 1) return b2;
    // Everything else
    return vec2(
        2 * t * (1 - t) + b2.x * t*t,
        b2.y * t * t
    );
}

// 计算立方根
float cube_root(float x){
    return sign(x) * pow(abs(x), 1.0 / 3.0);
}

// 解出一元三次方程的实根，返回值为实根个数
int cubic_solve(float a, float b, float c, float d, out float roots[3]){
    // Normalize so a = 1
    b = b / a;
    c = c / a;
    d = d / a;

    float  p = c - b*b / 3.0;
    float  q = b * (2.0*b*b - 9.0*c) / 27.0 + d;
    float p3 = p*p*p;
    float  disc = q*q + 4.0*p3 / 27.0;
    float offset = -b / 3.0;
    if(disc >= 0.0){
        float z = sqrt(disc);
        float u = (-q + z) / 2.0;
        float v = (-q - z) / 2.0;
        u = cube_root(u);
        v = cube_root(v);
        roots[0] = offset + u + v;
        return 1;
    }
    float u = sqrt(-p / 3.0);
    float v = acos(-sqrt( -27.0 / p3) * q / 2.0) / 3.0;
    float m = cos(v);
    float n = sin(v) * 1.732050808;

    float all_roots[3] = float[3](
        offset + u * (n - m),
        offset - u * (n + m),
        offset + u * (m + m)
    );

    // Only accept roots with a positive derivative
    int n_valid_roots = 0;
    for(int i = 0; i < 3; i++){
        float r = all_roots[i];
        if(3*r*r + 2*b*r + c > 0){ 
            roots[n_valid_roots] = r;
            n_valid_roots++;
        }
    }
    return n_valid_roots;
}

// 点到线段的距离
float dist_to_line(vec2 p, vec2 b2){
    float t = clamp(p.x / b2.x, 0, 1);
    float dist;
    if(t == 0)      dist = length(p);
    else if(t == 1) dist = distance(p, b2);
    else            dist = abs(p.y);

    return modify_distance_for_endpoints(p, dist, t);
}

// 点到贝塞尔曲线上某一点的距离
float dist_to_point_on_curve(vec2 p, float t, vec2 b2){
    t = clamp(t, 0, 1);
    return modify_distance_for_endpoints(
        p, length(p - bezier(t, b2)), t
    );
}

// 点到贝塞尔曲线上的最小距离
/*
这里需要把问题更加准确的定义一下：
点: p
贝塞尔曲线: b0(0,0), b1(1,0), b2
b0, b1, b2三个点会确定一个三角形，且点p在三角形内
*/
float min_dist_to_curve(vec2 p, vec2 b2, float degree){
    // 这个函数的返回值是不是永远为正？
    // Check if curve is really a a line
    if(degree == 1) return dist_to_line(p, b2);

    // Try finding the exact sdf by solving the equation
    // (d/dt) dist^2(t) = 0, which amount to the following
    // cubic.
    // 这里的uv_b2哪里来的? 应该是写错了
    float xm2 = uv_b2.x - 2.0;
    float y = uv_b2.y;
    // 修改后
    // float xm2 = b2.x - 2.0;
    // float y = b2.y;
    /*
    修改前和修改后都能正确的执行。原因：
    因为这段代码是插入quadratic_bezier_fill/frag.glsl文件中
    这份文件一开始就定义了in vec2 uv_b2;
    所以可以正确执行，算是歪打正着
    */

    float a = xm2*xm2 + y*y;
    float b = 3 * xm2;
    float c = -(p.x*xm2 + p.y*y) + 2;
    float d = -p.x;

    float roots[3];
    int n = cubic_solve(a, b, c, d, roots);  
    // At most 2 roots will have been populated.
    float d0 = dist_to_point_on_curve(p, roots[0], b2);
    if(n == 1) return d0;
    float d1 = dist_to_point_on_curve(p, roots[1], b2);
    return min(d0, d1);
}