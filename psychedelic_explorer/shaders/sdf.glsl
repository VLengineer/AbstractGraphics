#version 330 core
// Phonk / Neon SDF World
// Стиль: Synthwave, Darkwave, Neon Grid, Glowing Objects

uniform vec2 u_resolution;
uniform float u_time;
uniform vec4 u_palette_a;
uniform vec4 u_palette_b;
uniform float u_fade;
uniform float u_seed;
uniform vec2 u_mouse;
uniform vec3 u_camera_pos;
uniform vec3 u_camera_dir;
uniform float u_event_intensity;

in vec2 v_uv;
out vec4 fragColor;

vec3 palette(float t, vec4 p) {
    return p.xyz + p.w * cos(6.28318 * (p.x * t + p.yzw));
}

// --- SDF Primitives ---
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

// Бесконечная неоновая сетка (пол)
float sdGrid(vec3 p, float size) {
    vec3 q = abs(fract(p / size) - 0.5) * size;
    // Расстояние до линий сетки
    float d = min(min(q.x, q.y), q.z);
    return d - 0.03; // Толщина линий
}

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

// --- Scene Map ---
vec2 map(vec3 p) {
    // Искажение пространства
    vec3 pd = p;
    pd.y += sin(pd.x * 0.5 + u_time * 1.5) * 0.3;
    pd.x += cos(pd.z * 0.3 + u_time) * 0.2;
    
    // Пол - неоновая сетка
    float grid = sdGrid(pd + vec3(0.0, -1.0, 0.0), 2.0);
    
    // Движущиеся светящиеся сферы
    float s1 = sdSphere(pd - vec3(sin(u_time * 0.8) * 5.0, 1.5, cos(u_time * 0.6) * 5.0 - 8.0), 0.6);
    float s2 = sdSphere(pd - vec3(cos(u_time * 0.5) * 4.0, 3.0, sin(u_time * 0.7) * 4.0 - 8.0), 0.4);
    
    // Вращающийся тор
    vec3 pt = pd;
    float angle = u_time * 0.4;
    float c = cos(angle), s = sin(angle);
    pt.xz = mat2(c, -s, s, c) * pt.xz;
    float torus = sdTorus(pt - vec3(0.0, 0.5, -8.0), vec2(1.8, 0.25));
    
    // Плавающие кубы
    float cube1 = sdBox(pd - vec3(2.0, 2.0 + sin(u_time) * 0.5, -6.0), vec3(0.4));
    float cube2 = sdBox(pd - vec3(-2.5, 1.5 + cos(u_time * 1.2) * 0.3, -7.0), vec3(0.3));
    
    // Комбинация через smooth min
    float d = grid;
    d = smin(d, s1, 0.5);
    d = smin(d, s2, 0.4);
    d = smin(d, torus, 0.6);
    d = smin(d, cube1, 0.3);
    d = smin(d, cube2, 0.3);
    
    return vec2(d, 0.0);
}

vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy).x - map(p - e.xyy).x,
        map(p + e.yxy).x - map(p - e.yxy).x,
        map(p + e.yyx).x - map(p - e.yyx).x
    ));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    // Камера
    vec3 ro = u_camera_pos;
    vec3 target = ro + u_camera_dir;
    vec3 forward = normalize(target - ro);
    vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), forward));
    vec3 up = cross(forward, right);
    vec3 rd = normalize(forward + uv.x * right + uv.y * up);
    
    // Raymarching
    float t = 0.0;
    float glow = 0.0;
    vec3 col = vec3(0.0);
    bool hit = false;
    
    for (int i = 0; i < 120; i++) {
        vec3 p = ro + rd * t;
        vec2 res = map(p);
        float d = res.x;
        
        // Накопление свечения (neon glow)
        glow += exp(-d * 8.0) * 0.04;
        
        if (d < 0.001) {
            hit = true;
            vec3 n = calcNormal(p);
            vec3 lightDir = normalize(vec3(0.5, 1.0, -0.5));
            
            // Diffuse + Fresnel для неонового эффекта
            float diff = max(dot(n, lightDir), 0.0);
            float fresnel = pow(1.0 - abs(dot(rd, n)), 3.0);
            
            // Цвет объекта
            float colorT = length(p) * 0.15 + u_time * 0.15;
            vec3 baseCol = palette(colorT, u_palette_a);
            
            // Усиление краев (fresnel glow)
            col = baseCol * (0.3 + diff * 0.7 + fresnel * 2.5);
            break;
        }
        
        t += d;
        if (t > 60.0) break;
    }
    
    // Неоновый туман (purple/cyan fog)
    vec3 fogCol = mix(vec3(0.1, 0.0, 0.15), vec3(0.0, 0.3, 0.3), glow * 2.0);
    col += fogCol * glow * 4.0;
    
    // Подсветка сетки
    if (glow > 0.15) {
        col = mix(col, vec3(0.0, 1.0, 0.9), 0.4); // Cyan highlights
    }
    
    // Виньетка
    float vig = 1.0 - length(uv) * 0.7;
    col *= vig;
    
    // Хроматическая аберрация при событиях
    if (u_event_intensity > 0.5) {
        float aberr = (u_event_intensity - 0.5) * 0.02;
        col.r += aberr;
        col.b -= aberr;
    }
    
    // Fade transition
    col *= u_fade;
    
    // Tone mapping
    col = col / (col + vec3(1.0));
    
    fragColor = vec4(col, 1.0);
}
