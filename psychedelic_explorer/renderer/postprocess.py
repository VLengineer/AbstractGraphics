"""Post-processing effects (bloom, trails, etc.)."""
import moderngl
import numpy as np


class PostProcessor:
    """Handles post-processing effects with framebuffers."""
    
    def __init__(self, ctx: moderngl.Context, shader_manager, 
                 width: int, height: int):
        self.ctx = ctx
        self.width = width
        self.height = height
        self.shader_manager = shader_manager
        
        # Get postprocess program
        self.program = shader_manager.create_program('postprocess')
        
        # Create framebuffers for double buffering
        self.fb1 = self._create_framebuffer(width, height)
        self.fb2 = self._create_framebuffer(width, height)
        self.current_fb = 0
        
        # Fullscreen quad VAO
        self.quad_vao = self._create_quad()
        
        # Post-process parameters
        self.trail_strength = 0.7
        self.bloom_threshold = 0.8
        self.aberration = 0.0
        
    def _create_framebuffer(self, w: int, h: int) -> moderngl.Framebuffer:
        """Create a framebuffer with color texture."""
        texture = self.ctx.texture((w, h), 4, dtype='f4')
        return self.ctx.framebuffer(color_attachments=[texture])
    
    def _create_quad(self) -> moderngl.VertexArray:
        """Create fullscreen quad VAO."""
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        vbo = self.ctx.buffer(vertices.tobytes())
        return self.ctx.vertex_array(
            self.program,
            [(vbo, '2f', 'in_vert')]
        )
    
    @property
    def current_texture(self) -> moderngl.Texture:
        """Get current framebuffer's color texture."""
        return self.fb1.color_attachments[0] if self.current_fb == 0 else self.fb2.color_attachments[0]
    
    @property
    def previous_texture(self) -> moderngl.Texture:
        """Get previous framebuffer's color texture."""
        return self.fb2.color_attachments[0] if self.current_fb == 0 else self.fb1.color_attachments[0]
    
    def render(self, source_texture: moderngl.Texture) -> None:
        """Apply post-processing to source texture."""
        # Bind destination framebuffer
        dest_fb = self.fb2 if self.current_fb == 0 else self.fb1
        dest_fb.use()
        
        # Set uniforms
        self.program['u_current'].value = 0
        self.program['u_previous'].value = 1
        self.program['u_trail_strength'].value = self.trail_strength
        self.program['u_bloom_threshold'].value = self.bloom_threshold
        self.program['u_aberration'].value = self.aberration
        
        # Bind textures
        source_texture.use(0)
        self.previous_texture.use(1)
        
        # Render
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
        
        # Swap buffers
        self.current_fb = 1 - self.current_fb
    
    def update_params(self, trail: float = None, bloom: float = None,
                      aberration: float = None) -> None:
        """Update post-processing parameters."""
        if trail is not None:
            self.trail_strength = np.clip(trail, 0.0, 0.95)
        if bloom is not None:
            self.bloom_threshold = np.clip(bloom, 0.0, 1.0)
        if aberration is not None:
            self.aberration = np.clip(aberration, 0.0, 0.05)
    
    def set_event_intensity(self, intensity: float) -> None:
        """Adjust parameters based on event intensity."""
        # More intense events = more trails and aberration
        self.trail_strength = 0.5 + intensity * 0.3
        self.aberration = intensity * 0.02
    
    def clear(self, color: tuple = (0.0, 0.0, 0.0, 1.0)) -> None:
        """Clear both framebuffers."""
        for fb in [self.fb1, self.fb2]:
            fb.clear(*color)
    
    def resize(self, width: int, height: int) -> None:
        """Resize framebuffers."""
        self.width = width
        self.height = height
        self.fb1 = self._create_framebuffer(width, height)
        self.fb2 = self._create_framebuffer(width, height)
