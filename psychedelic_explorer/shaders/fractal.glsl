#version 330 core
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;
uniform vec2 u_camera;
uniform float u_zoom;
uniform vec4 u_palette_a;
uniform vec4 u_palette_b;
uniform vec2 u_julia_c;
uniform float u_morph;
uniform float u_fade;

in vec2 v_uv;
out vec4 fragColor;

vec3 palette(float t, vec4 p) {
    return 0.5 + 0.5 * cos(6.28318 * (p.x * t + p.yzw));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    uv = uv / u_zoom + u_camera;
    
    vec2 c1 = u_julia_c;
    vec2 c2 = vec2(
        0.7885 * cos(u_time * 0.3),
        0.7885 * sin(u_time * 0.3)
    );
    vec2 c = mix(c1, c2, u_morph);
    c += u_mouse * 0.2;
    
    vec2 z = uv;
    float iter = 0.0;
    const float MAX_ITER = 150.0;
    
    for (float i = 0.0; i < MAX_ITER; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if (dot(z, z) > 4.0) break;
        iter++;
    }
    
    float smooth_iter = iter - log2(log2(dot(z, z))) + 4.0;
    float t = smooth_iter / 40.0 + u_time * 0.05;
    
    vec3 col1 = palette(t, u_palette_a);
    vec3 col2 = palette(t + 0.5, u_palette_b);
    vec3 col = mix(col1, col2, u_morph);
    
    float vig = 1.0 - 0.4 * length(uv);
    col *= vig;
    col *= u_fade;
    
    fragColor = vec4(col, 1.0);
}
