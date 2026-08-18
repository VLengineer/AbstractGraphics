"""Shader management and compilation."""
import os
from typing import Dict, Optional
import moderngl


class ShaderManager:
    """Manages shader compilation and program creation."""
    
    def __init__(self, ctx: moderngl.Context, shader_dir: str):
        self.ctx = ctx
        self.shader_dir = shader_dir
        self._programs: Dict[str, moderngl.Program] = {}
        self._vertex_source: Optional[str] = None
        
    def _load_source(self, filename: str) -> str:
        """Load shader source from file."""
        path = os.path.join(self.shader_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @property
    def vertex_source(self) -> str:
        """Get cached vertex shader source."""
        if self._vertex_source is None:
            self._vertex_source = self._load_source('vertex.glsl')
        return self._vertex_source
    
    def create_program(self, fragment_shader: str) -> moderngl.Program:
        """Create a shader program from vertex and fragment shaders.
        
        Args:
            fragment_shader: Name of fragment shader file (without .glsl)
            
        Returns:
            Compiled ModernGL program
        """
        if fragment_shader in self._programs:
            return self._programs[fragment_shader]
        
        fragment_source = self._load_source(f'{fragment_shader}.glsl')
        
        program = self.ctx.program(
            vertex_shader=self.vertex_source,
            fragment_shader=fragment_source
        )
        
        self._programs[fragment_shader] = program
        return program
    
    def get_program(self, fragment_shader: str) -> Optional[moderngl.Program]:
        """Get existing program or None."""
        return self._programs.get(fragment_shader)
    
    def clear_cache(self) -> None:
        """Clear all cached programs."""
        self._programs.clear()
