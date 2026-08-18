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
            input_state: Dict with keys: mouse_delta, keys_pressed
            gravity_flipped: If True, invert vertical movement
        """
        if not self.is_alive:
            return
            
        # Mouse look
        mouse_delta = input_state.get('mouse_delta', (0, 0))
        self.yaw -= mouse_delta[0] * self.look_sensitivity
        self.pitch -= mouse_delta[1] * self.look_sensitivity
        self.pitch = np.clip(self.pitch, -np.pi/2 + 0.1, np.pi/2 - 0.1)
        
        # Keyboard movement
        keys = input_state.get('keys_pressed', set())
        move_dir = np.zeros(3, dtype=np.float32)
        
        # Forward/back (auto-forward always active)
        move_dir[2] = -1.0  # Always moving forward
        
        if 'W' in keys:
            move_dir[2] -= 1.0
        if 'S' in keys:
            move_dir[2] += 1.0
        if 'A' in keys:
            move_dir[0] -= 1.0
        if 'D' in keys:
            move_dir[1] += 1.0
            
        # Normalize horizontal movement
        if move_dir[0] != 0 or move_dir[1] != 0:
            length = np.sqrt(move_dir[0]**2 + move_dir[1]**2)
            move_dir[0] /= length
            move_dir[1] /= length
        
        # Apply gravity flip if active
        if gravity_flipped:
            move_dir[1] *= -1
        
        speed = self.move_speed * (2.0 if 'SHIFT' in keys else 1.0)
        self.velocity = move_dir * speed
        
        # Update position
        self.position += self.velocity * dt
        
        # Energy regeneration
        self.energy = min(self.max_energy, self.energy + self.energy_regen * dt)
    
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
