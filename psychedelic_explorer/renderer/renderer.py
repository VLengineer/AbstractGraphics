"""Main renderer using ModernGL."""
import moderngl
import numpy as np
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.worlds import World
    from .shaders import ShaderManager
    from .postprocess import PostProcessor


class Renderer:
    """Main renderer wrapper for ModernGL."""
    
    def __init__(self, ctx: moderngl.Context, shader_manager: 'ShaderManager',
                 width: int, height: int):
        self.ctx = ctx
        self.width = width
        self.height = height
        self.shader_manager = shader_manager
        
        # Create programs for each world type
        self.fractal_program = shader_manager.create_program('fractal')
        self.tunnel_program = shader_manager.create_program('tunnel')
        self.sdf_program = shader_manager.create_program('sdf')
        
        # Fullscreen quad VAO (shared)
        self.quad_vao = self._create_quad(self.fractal_program)
        
        # Current world render texture
        self.render_texture = self._create_texture()
        self.render_fb = self.ctx.framebuffer(color_attachments=[self.render_texture])
        
        # Fade parameter for transitions
        self.fade = 1.0
        
    def _create_texture(self) -> moderngl.Texture:
        """Create render target texture."""
        return self.ctx.texture((self.width, self.height), 4, dtype='f4')
    
    def _create_quad(self, program: moderngl.Program) -> moderngl.VertexArray:
        """Create fullscreen quad VAO."""
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        vbo = self.ctx.buffer(vertices.tobytes())
        return self.ctx.vertex_array(program, [(vbo, '2f', 'in_vert')])
    
    def set_uniforms(self, program: moderngl.Program, **kwargs) -> None:
        """Set uniforms on a program safely."""
        for name, value in kwargs.items():
            uniform_name = f'u_{name}'
            if uniform_name in program:
                if isinstance(value, np.ndarray):
                    if value.ndim == 1:
                        if len(value) == 2:
                            program[uniform_name].value = tuple(value.astype('f4'))
                        elif len(value) == 3:
                            program[uniform_name].value = tuple(value.astype('f4'))
                        elif len(value) == 4:
                            program[uniform_name].value = tuple(value.astype('f4'))
                    else:
                        program[uniform_name].value = value.tolist()
                else:
                    program[uniform_name].value = float(value)
    
    def render_fractal(self, time: float, resolution: tuple, mouse: tuple,
                       camera: np.ndarray, zoom: float, 
                       palette_a: np.ndarray, palette_b: np.ndarray,
                       julia_c: np.ndarray, morph: float) -> None:
        """Render fractal world."""
        self.render_fb.use()
        self.render_fb.clear(0.0, 0.0, 0.0, 1.0)
        
        prog = self.fractal_program
        self.set_uniforms(prog,
            resolution=resolution,
            time=time,
            mouse=mouse,
            camera=camera,
            zoom=zoom,
            palette_a=palette_a,
            palette_b=palette_b,
            julia_c=julia_c,
            morph=morph,
            fade=self.fade
        )
        
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
    
    def render_tunnel(self, time: float, resolution: tuple,
                      palette_a: np.ndarray, palette_b: np.ndarray) -> None:
        """Render tunnel world."""
        self.render_fb.use()
        self.render_fb.clear(0.0, 0.0, 0.0, 1.0)
        
        prog = self.tunnel_program
        self.set_uniforms(prog,
            resolution=resolution,
            time=time,
            palette_a=palette_a,
            palette_b=palette_b,
            fade=self.fade
        )
        
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
    
    def render_sdf(self, time: float, resolution: tuple,
                   palette_a: np.ndarray, palette_b: np.ndarray,
                   seed: float = 0.0) -> None:
        """Render SDF world."""
        self.render_fb.use()
        self.render_fb.clear(0.0, 0.0, 0.0, 1.0)
        
        prog = self.sdf_program
        self.set_uniforms(prog,
            resolution=resolution,
            time=time,
            palette_a=palette_a,
            palette_b=palette_b,
            fade=self.fade,
            seed=seed
        )
        
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
    
    def get_render_texture(self) -> moderngl.Texture:
        """Get the current render texture for post-processing."""
        return self.render_texture
    
    def blit_to_screen(self, screen_texture: moderngl.Texture = None) -> None:
        """Blit final result to screen."""
        self.ctx.screen.use()
        self.ctx.screen.clear(0.0, 0.0, 0.0, 1.0)
        
        # Use the provided texture or render texture
        tex = screen_texture if screen_texture else self.render_texture
        tex.use(0)
        
        # Simple blit shader would go here, but we'll use a trick
        # For now, just clear - proper implementation needs a blit program
        pass
    
    def set_fade(self, value: float) -> None:
        """Set fade opacity for transitions."""
        self.fade = np.clip(value, 0.0, 1.0)
    
    def resize(self, width: int, height: int) -> None:
        """Resize renderer."""
        self.width = width
        self.height = height
        self.render_texture = self._create_texture()
        self.render_fb = self.ctx.framebuffer(color_attachments=[self.render_texture])
        self.quad_vao = self._create_quad(self.fractal_program)
