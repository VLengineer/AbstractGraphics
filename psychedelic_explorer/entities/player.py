"""Player/Camera entity for the game."""
import numpy as np
from dataclasses import dataclass


@dataclass
class Player:
    """Player camera with position, velocity, and game stats."""
    position: np.ndarray  # xyz position
    velocity: np.ndarray  # xyz velocity
    yaw: float = 0.0      # horizontal rotation (radians)
    pitch: float = 0.0    # vertical rotation (radians)
    energy: float = 100.0  # 0..100, for dash/flash ability
    score: int = 0
    health: float = 100.0
    is_alive: bool = True
    
    # Movement parameters
    move_speed: float = 5.0
    look_sensitivity: float = 0.002
    max_energy: float = 100.0
    energy_regen: float = 10.0  # per second
    dash_cost: float = 30.0
    
    def __post_init__(self):
        if self.position is None:
            self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        if self.velocity is None:
            self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    
    @classmethod
    def create(cls) -> 'Player':
        """Create a new player with default values."""
        return cls(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            velocity=np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )
    
    def update(self, dt: float, input_state: dict, gravity_flipped: bool = False) -> None:
        """Update player based on input and time delta.
        
        Args:
            dt: Delta time in seconds
            input_state: Dict with keys: move, look, action, boost
            gravity_flipped: If True, invert vertical movement
        """
        if not self.is_alive:
            return
            
        # Mouse look from 'look' vector
        look = input_state.get('look', np.array([0.0, 0.0], dtype=np.float32))
        self.yaw += look[0]
        self.pitch += look[1]
        self.pitch = np.clip(self.pitch, -np.pi/2 + 0.1, np.pi/2 - 0.1)
        
        # Keyboard movement from 'move' vector
        move = input_state.get('move', np.array([0.0, 0.0, 0.0], dtype=np.float32))
        move_dir = move.copy()
        
        # Always moving forward automatically
        move_dir[2] -= 1.0
        
        # Apply gravity flip if active
        if gravity_flipped:
            move_dir[1] *= -1
        
        # Boost speed
        speed_multiplier = 2.0 if input_state.get('boost', False) else 1.0
        speed = self.move_speed * speed_multiplier
        
        # Update position
        self.position += move_dir * speed * dt
        
        # Energy regeneration
        self.energy = min(self.max_energy, self.energy + self.energy_regen * dt)
        
        # Handle dash/action
        if input_state.get('action', False):
            self.dash()
    
    def dash(self) -> bool:
        """Perform a dash/flash action. Returns True if successful."""
        if self.energy >= self.dash_cost and self.is_alive:
            self.energy -= self.dash_cost
            return True
        return False
    
    def take_damage(self, amount: float) -> None:
        """Take damage."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
    
    def add_score(self, points: int) -> None:
        """Add to score."""
        self.score += points
    
    def reset(self) -> None:
        """Reset player state."""
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.yaw = 0.0
        self.pitch = 0.0
        self.energy = self.max_energy
        self.score = 0
        self.health = 100.0
        self.is_alive = True
    
    def get_forward_vector(self) -> np.ndarray:
        """Calculate the forward direction vector based on yaw and pitch.
        
        Returns:
            3D unit vector pointing in the direction the player is looking
        """
        x = np.cos(self.pitch) * np.sin(self.yaw)
        y = np.sin(self.pitch)
        z = np.cos(self.pitch) * np.cos(self.yaw)
        return np.array([x, y, z], dtype=np.float32)
