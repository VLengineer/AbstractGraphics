#version 330 core
uniform sampler2D u_current;
uniform sampler2D u_previous;
uniform float u_trail_strength;
uniform float u_bloom_threshold;
uniform float u_aberration;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec3 curr = texture(u_current, v_uv).rgb;
    vec3 prev = texture(u_previous, v_uv).rgb;
    
    vec3 col = mix(curr, prev, u_trail_strength);
    
    float brightness = dot(col, vec3(0.2126, 0.7152, 0.0722));
    if (brightness > u_bloom_threshold) {
        col += (col - u_bloom_threshold) * 0.3;
    }
    
    if (u_aberration > 0.0) {
        col.r = texture(u_current, v_uv + vec2(u_aberration, 0.0)).r;
        col.b = texture(u_current, v_uv - vec2(u_aberration, 0.0)).b;
    }
    
    col = clamp(col, 0.0, 1.0);
    
    fragColor = vec4(col, 1.0);
}
