#version 330 core
uniform vec2 u_resolution;
uniform float u_time;
uniform vec4 u_palette_a;
uniform vec4 u_palette_b;
uniform float u_fade;

in vec2 v_uv;
out vec4 fragColor;

vec3 palette(float t, vec4 p) {
    return 0.5 + 0.5 * cos(6.28318 * (p.x * t + p.yzw));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    float r = length(uv);
    float a = atan(uv.y, uv.x);
    
    vec2 tuv = vec2(1.0 / r, a / 3.14159);
    tuv.y += u_time * 0.2;
    tuv.x += u_time * 0.1;
    
    vec2 z = tuv * 2.0;
    vec2 c = vec2(
        0.5 * sin(u_time * 0.1),
        0.5 * cos(u_time * 0.1)
    );
    
    float iter = 0.0;
    for (float i = 0.0; i < 100.0; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if (dot(z, z) > 4.0) break;
        iter++;
    }
    
    float t = iter / 30.0 + u_time * 0.05;
    vec3 col1 = palette(t, u_palette_a);
    vec3 col2 = palette(t + 0.3, u_palette_b);
    vec3 col = mix(col1, col2, 0.5);
    
    col *= exp(-r * 2.0);
    col *= u_fade;
    
    fragColor = vec4(col, 1.0);
}
