"""World system - base class and implementations."""
from abc import ABC, abstractmethod
import numpy as np
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..renderer.renderer import Renderer


class World(ABC):
    """Base interface for all world types."""
    
    name: str = "base"
    
    @abstractmethod
    def update(self, dt: float, player_pos: np.ndarray, time: float) -> None:
        """Update world state."""
        pass
    
    @abstractmethod
    def render(self, renderer: 'Renderer', time: float, resolution: tuple,
               mouse: tuple, palette_a: np.ndarray, palette_b: np.ndarray) -> None:
        """Render the world."""
        pass
    
    @abstractmethod
    def randomize(self, seed: float = None) -> None:
        """Randomize world parameters."""
        pass
    
    def transition_in(self) -> None:
        """Called when transitioning into this world."""
        pass
    
    def transition_out(self) -> None:
        """Called when transitioning out of this world."""
        pass


class FractalWorld(World):
    """Julia set fractal world with morphing."""
    
    name = "fractal"
    
    def __init__(self):
        self.camera = np.array([0.0, 0.0], dtype=np.float32)
        self.zoom = 1.0
        self.julia_c = np.array([-0.7, 0.27015], dtype=np.float32)
        self.morph = 0.0
        self.target_julia_c = self.julia_c.copy()
        
    def update(self, dt: float, player_pos: np.ndarray, time: float) -> None:
        # Animate julia parameter
        self.julia_c += (self.target_julia_c - self.julia_c) * dt * 0.5
        
        # Camera follows player loosely
        target_cam = player_pos[:2] * 0.1
        self.camera += (target_cam - self.camera) * dt * 2.0
        
        # Zoom pulse
        self.zoom = 1.0 + 0.2 * np.sin(time * 0.5)
        
        # Morph animation
        self.morph = 0.5 + 0.5 * np.sin(time * 0.3)
    
    def render(self, renderer: 'Renderer', time: float, resolution: tuple,
               mouse: tuple, palette_a: np.ndarray, palette_b: np.ndarray) -> None:
        renderer.render_fractal(
            time=time,
            resolution=resolution,
            mouse=mouse,
            camera=self.camera,
            zoom=self.zoom,
            palette_a=palette_a,
            palette_b=palette_b,
            julia_c=self.julia_c,
            morph=self.morph
        )
    
    def randomize(self, seed: float = None) -> None:
        if seed is not None:
            rng = np.random.default_rng(int(seed * 1000))
        else:
            rng = np.random.default_rng()
        
        self.target_julia_c = np.array([
            rng.uniform(-1.0, 1.0),
            rng.uniform(-1.0, 1.0)
        ], dtype=np.float32)
        self.zoom = rng.uniform(0.8, 1.5)


class TunnelWorld(World):
    """Infinite fractal tunnel world."""
    
    name = "tunnel"
    
    def __init__(self):
        self.speed = 0.2
        self.twist = 0.1
        
    def update(self, dt: float, player_pos: np.ndarray, time: float) -> None:
        # Speed varies with time
        self.speed = 0.2 + 0.1 * np.sin(time * 0.3)
    
    def render(self, renderer: 'Renderer', time: float, resolution: tuple,
               mouse: tuple, palette_a: np.ndarray, palette_b: np.ndarray) -> None:
        renderer.render_tunnel(
            time=time,
            resolution=resolution,
            palette_a=palette_a,
            palette_b=palette_b
        )
    
    def randomize(self, seed: float = None) -> None:
        if seed is not None:
            rng = np.random.default_rng(int(seed * 1000))
        else:
            rng = np.random.default_rng()
        self.speed = rng.uniform(0.1, 0.4)
        self.twist = rng.uniform(-0.2, 0.2)


class SDFWorld(World):
    """Signed distance field world with strange forms."""
    
    name = "sdf"
    
    def __init__(self):
        self.seed = 0.0
        self.rotation_speed = 0.1
        
    def update(self, dt: float, player_pos: np.ndarray, time: float) -> None:
        self.rotation_speed = 0.1 + 0.05 * np.sin(time * 0.2)
    
    def render(self, renderer: 'Renderer', time: float, resolution: tuple,
               mouse: tuple, palette_a: np.ndarray, palette_b: np.ndarray) -> None:
        renderer.render_sdf(
            time=time,
            resolution=resolution,
            palette_a=palette_a,
            palette_b=palette_b,
            seed=self.seed
        )
    
    def randomize(self, seed: float = None) -> None:
        if seed is not None:
            self.seed = seed
        else:
            self.seed = np.random.random()


class WorldFactory:
    """Factory for creating world instances."""
    
    _worlds = {
        'fractal': FractalWorld,
        'tunnel': TunnelWorld,
        'sdf': SDFWorld,
    }
    
    @classmethod
    def create(cls, name: str) -> World:
        """Create a world by name."""
        world_class = cls._worlds.get(name.lower())
        if world_class is None:
            raise ValueError(f"Unknown world type: {name}")
        return world_class()
    
    @classmethod
    def get_names(cls) -> list:
        """Get list of available world names."""
        return list(cls._worlds.keys())
