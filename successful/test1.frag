uniform vec2 iResolution;
uniform float iTime;

void main()
{    
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    
    vec3 col = 0.5 + 0.5 * cos(iTime + vec3(uv.xyx) + vec3(0, 2, 4));

    gl_FragColor = vec4(col, 1.0);
}
