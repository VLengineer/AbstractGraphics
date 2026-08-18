#version 330 core

uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;
uniform vec3 u_camera_pos;
uniform vec3 u_camera_dir;
uniform float u_zoom;
uniform vec4 u_palette_a;
uniform vec4 u_palette_b;
uniform float u_event_intensity;

in vec2 v_uv;
out vec4 fragColor;

// --- Helper Functions ---

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

vec3 palette(float t, vec4 a, vec4 b) {
    return a.xyz + b.xyz * cos(6.28318 * (t * b.w + b.yzw));
}

// --- Scene Mapping ---

float map(vec3 p) {
    // Space distortion based on time
    vec3 p_orig = p;
    p += 0.2 * vec3(
        sin(p.y * 2.0 + u_time * 0.5),
        cos(p.z * 2.0 + u_time * 0.3),
        sin(p.x * 2.0 + u_time * 0.7)
    );

    // Moving spheres
    float d1 = sdSphere(p - vec3(sin(u_time * 0.4) * 3.0, 0.0, cos(u_time * 0.4) * 3.0), 0.8);
    float d2 = sdSphere(p - vec3(cos(u_time * 0.3) * 2.0, 1.5, sin(u_time * 0.3) * 2.0), 0.5);

    // Rotating torus
    vec3 pt = p;
    float angle = u_time * 0.2;
    mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
    pt.xz *= rot;
    pt.yz *= rot;
    float d3 = sdTorus(pt, vec2(1.5, 0.2));

    // Floating cubes
    float d4 = sdBox(p - vec3(0.0, 2.0 + sin(u_time) * 1.0, 0.0), vec3(0.6));
    float d5 = sdBox(p - vec3(-2.5, 1.0, 0.0), vec3(0.4));
    float d6 = sdBox(p - vec3(2.5, 1.0, 0.0), vec3(0.4));

    // Infinite neon grid (floor)
    float grid_height = -1.5;
    float d_grid = abs(p.y - grid_height) - 0.05;
    
    // Combine shapes
    float d_objects = smin(smin(d1, d2, 0.3), d3, 0.5);
    d_objects = smin(d_objects, smin(d4, d5, 0.2), 0.3);
    d_objects = smin(d_objects, d6, 0.3);

    // Combine with grid
    return min(d_objects, d_grid);
}

// --- Raymarching ---

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;

    // Camera setup
    vec3 ro = u_camera_pos;
    vec3 target = ro + u_camera_dir;
    
    vec3 cw = normalize(target - ro);
    vec3 cp = vec3(0.0, 1.0, 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = normalize(cross(cu, cw));
    vec3 rd = normalize(uv.x * cu + uv.y * cv + 1.5 * cw);

    float t = 0.0;
    float d = 0.0;
    float glow = 0.0;
    int steps = 0;
    
    // Marching loop
    for (int i = 0; i < 100; i++) {
        vec3 p = ro + rd * t;
        d = map(p);
        
        // Glow accumulation near surfaces
        if (d < 0.1) {
            glow += 0.02 / (d + 0.01);
        }
        
        t += d;
        steps = i;
        if (d < 0.001 || t > 20.0) break;
    }

    // Coloring
    vec3 col = vec3(0.0);
    
    if (t < 20.0) {
        vec3 p = ro + rd * t;
        
        // Normal calculation
        vec2 e = vec2(0.001, 0.0);
        vec3 n = normalize(vec3(
            map(p + e.xyy) - map(p - e.xyy),
            map(p + e.yxy) - map(p - e.yxy),
            map(p + e.yyx) - map(p - e.yyx)
        ));

        // Base material color based on normal and palette
        float diff = dot(n, normalize(vec3(1.0, 1.0, 1.0)));
        vec3 base_col = palette(diff * 0.5 + 0.5, u_palette_a, u_palette_b);
        
        // Grid check (if y is near -1.5)
        if (abs(p.y + 1.5) < 0.06) {
            // Neon grid lines
            float grid_line = step(0.9, fract(p.x * 0.5)) + step(0.9, fract(p.z * 0.5));
            vec3 grid_col = vec3(1.0, 0.0, 1.0) * grid_line;
            base_col = mix(base_col, grid_col, 0.8);
            
            // Add extra glow to grid
            glow += grid_line * 0.5;
        }

        // Fresnel effect for neon look
        float fresnel = pow(1.0 + dot(rd, n), 4.0);
        col = base_col * (diff * 0.5 + 0.5) + vec3(0.2, 0.8, 1.0) * fresnel;
    }

    // Add accumulated glow
    col += vec3(0.1, 0.4, 0.8) * glow * 0.3;

    // Fog
    float fog = 1.0 - exp(-0.1 * t);
    vec3 fog_col = vec3(0.05, 0.0, 0.1);
    col = mix(col, fog_col, fog);

    // Chromatic aberration based on event intensity
    if (u_event_intensity > 0.1) {
        col.r += u_event_intensity * 0.2 * abs(uv.x);
        col.b += u_event_intensity * 0.2 * abs(uv.y);
    }

    // Tone mapping
    col = col / (col + vec3(1.0));
    
    // Gamma correction
    col = pow(col, vec3(0.4545));

    fragColor = vec4(col, 1.0);
}
