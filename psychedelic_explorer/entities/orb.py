"""Entity classes for game objects."""
import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class EnergyOrb:
    """Collectible energy orb that gives points."""
    position: np.ndarray
    radius: float = 0.3
    collected: bool = False
    points: int = 100
    
    @classmethod
    def create_random(cls, bounds: tuple = (-10, 10)) -> 'EnergyOrb':
        """Create orb at random position within bounds."""
        pos = np.random.uniform(bounds[0], bounds[1], size=3).astype(np.float32)
        return cls(position=pos)


@dataclass
class HostileForm:
    """Hostile form that damages player on contact."""
    position: np.ndarray
    velocity: np.ndarray
    radius: float = 0.5
    damage: float = 20.0
    active: bool = True
    
    @classmethod
    def create_towards_player(cls, spawn_pos: np.ndarray, 
                               player_pos: np.ndarray,
                               speed: float = 2.0) -> 'HostileForm':
        """Create hostile form moving towards player."""
        direction = player_pos - spawn_pos
        dist = np.linalg.norm(direction)
        if dist > 0:
            velocity = (direction / dist) * speed
        else:
            velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        return cls(position=spawn_pos.copy(), velocity=velocity)
    
    def update(self, dt: float, player_pos: np.ndarray) -> None:
        """Update position and move towards player."""
        if not self.active:
            return
            
        self.position += self.velocity * dt
        
        # Slowly adjust velocity towards player
        direction = player_pos - self.position
        dist = np.linalg.norm(direction)
        if dist > 0:
            self.velocity = (direction / dist) * 2.0
    
    def check_collision(self, player_pos: np.ndarray, player_radius: float = 0.5) -> bool:
        """Check if colliding with player."""
        dist = np.linalg.norm(self.position - player_pos)
        return dist < (self.radius + player_radius)


@dataclass
class Portal:
    """Portal that teleports player to different world."""
    position: np.ndarray
    radius: float = 1.0
    active: bool = True
    target_world: str = "fractal"  # fractal, tunnel, or sdf
    
    @classmethod
    def create_random(cls, bounds: tuple = (-10, 10), 
                      worlds: List[str] = None) -> 'Portal':
        """Create portal at random position."""
        if worlds is None:
            worlds = ["fractal", "tunnel", "sdf"]
        pos = np.random.uniform(bounds[0], bounds[1], size=3).astype(np.float32)
        target = np.random.choice(worlds)
        return cls(position=pos, target_world=target)
    
    def check_activation(self, player_pos: np.ndarray, 
                         player_radius: float = 0.5) -> bool:
        """Check if player entered portal."""
        dist = np.linalg.norm(self.position - player_pos)
        return dist < (self.radius + player_radius)


@dataclass
class GlitchZone:
    """Zone that causes visual glitches/distortions."""
    position: np.ndarray
    radius: float = 2.0
    intensity: float = 0.5
    active: bool = True
    
    @classmethod
    def create_random(cls, bounds: tuple = (-10, 10)) -> 'GlitchZone':
        """Create glitch zone at random position."""
        pos = np.random.uniform(bounds[0], bounds[1], size=3).astype(np.float32)
        intensity = np.random.uniform(0.3, 1.0)
        return cls(position=pos, intensity=intensity)
    
    def contains(self, player_pos: np.ndarray) -> bool:
        """Check if player is inside the zone."""
        dist = np.linalg.norm(self.position - player_pos)
        return dist < self.radius


@dataclass
class EntityManager:
    """Manages all entities in the current world."""
    orbs: List[EnergyOrb] = field(default_factory=list)
    hostiles: List[HostileForm] = field(default_factory=list)
    portals: List[Portal] = field(default_factory=list)
    glitch_zones: List[GlitchZone] = field(default_factory=list)
    
    def spawn_orb(self, bounds: tuple = (-10, 10)) -> None:
        """Spawn a new energy orb."""
        self.orbs.append(EnergyOrb.create_random(bounds))
    
    def spawn_hostile(self, spawn_pos: np.ndarray, 
                      player_pos: np.ndarray) -> None:
        """Spawn a new hostile form."""
        self.hostiles.append(
            HostileForm.create_towards_player(spawn_pos, player_pos)
        )
    
    def spawn_portal(self, bounds: tuple = (-10, 10)) -> None:
        """Spawn a new portal."""
        self.portals.append(Portal.create_random(bounds))
    
    def spawn_glitch_zone(self, bounds: tuple = (-10, 10)) -> None:
        """Spawn a new glitch zone."""
        self.glitch_zones.append(GlitchZone.create_random(bounds))
    
    def update(self, dt: float, player_pos: np.ndarray) -> dict:
        """Update all entities. Returns events dict."""
        events = {
            'orbs_collected': 0,
            'damage_taken': 0.0,
            'portal_entered': None,
            'in_glitch_zone': False,
        }
        
        # Update and check orbs
        for orb in self.orbs:
            if not orb.collected:
                dist = np.linalg.norm(orb.position - player_pos)
                if dist < orb.radius + 0.5:
                    orb.collected = True
                    events['orbs_collected'] += orb.points
        
        # Update and check hostiles
        for hostile in self.hostiles:
            if hostile.active:
                hostile.update(dt, player_pos)
                if hostile.check_collision(player_pos):
                    events['damage_taken'] += hostile.damage
                    hostile.active = False
        
        # Check portals
        for portal in self.portals:
            if portal.active and portal.check_activation(player_pos):
                events['portal_entered'] = portal.target_world
                portal.active = False
        
        # Check glitch zones
        for zone in self.glitch_zones:
            if zone.active and zone.contains(player_pos):
                events['in_glitch_zone'] = True
                break
        
        return events
    
    def clear_collected(self) -> None:
        """Remove collected/dead entities."""
        self.orbs = [o for o in self.orbs if not o.collected]
        self.hostiles = [h for h in self.hostiles if h.active]
        self.portals = [p for p in self.portals if p.active]
    
    def reset(self) -> None:
        """Clear all entities."""
        self.orbs.clear()
        self.hostiles.clear()
        self.portals.clear()
        self.glitch_zones.clear()
