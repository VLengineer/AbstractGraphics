#version 330 core
uniform vec2 u_resolution;
uniform float u_time;
uniform vec4 u_palette_a;
uniform vec4 u_palette_b;
uniform float u_fade;
uniform float u_seed;

in vec2 v_uv;
out vec4 fragColor;

vec3 palette(float t, vec4 p) {
    return 0.5 + 0.5 * cos(6.28318 * (p.x * t + p.yzw));
}

float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float map(vec3 p) {
    p += 0.3 * vec3(
        sin(p.y * 3.0 + u_time),
        cos(p.z * 3.0 + u_time * 0.7),
        sin(p.x * 3.0 + u_time * 1.3)
    );
    
    float d1 = sdTorus(p, vec2(1.2, 0.3));
    float d2 = sdSphere(p - vec3(sin(u_time) * 2.0, 0.0, 0.0), 0.8);
    float d3 = sdBox(p, vec3(0.6));
    
    return smin(smin(d1, d2, 0.5), d3, 0.3);
}

vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    vec3 ro = vec3(0.0, 0.0, -5.0 + u_time * 2.0);
    vec3 rd = normalize(vec3(uv, 1.0));
    
    float t = 0.0;
    float totalDist = 0.0;
    vec3 col = vec3(0.0);
    
    for (int i = 0; i < 100; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < 0.001) {
            vec3 n = calcNormal(p);
            vec3 light = normalize(vec3(1.0, 1.0, -1.0));
            float diff = max(dot(n, light), 0.0);
            
            float shade = 0.5 + 0.5 * diff;
            float ft = t * 0.1 + u_time * 0.05;
            vec3 pcol1 = palette(ft, u_palette_a);
            vec3 pcol2 = palette(ft + 0.5, u_palette_b);
            col = mix(pcol1, pcol2, 0.5) * shade;
            break;
        }
        t += d;
        totalDist += d;
        if (t > 50.0) break;
    }
    
    col *= exp(-totalDist * 0.05);
    col *= u_fade;
    
    fragColor = vec4(col, 1.0);
}
