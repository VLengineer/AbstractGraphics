"""Random event system for world parameter changes."""
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class EventType(Enum):
    PALETTE_SHIFT = auto()
    FRACTAL_MORPH = auto()
    GRAVITY_FLIP = auto()
    TIME_WARP = auto()
    COLOR_INVERT = auto()
    SDF_MUTATION = auto()
    ZOOM_PULSE = auto()


@dataclass
class RandomEvent:
    """Represents a random event that modifies world parameters."""
    type: EventType
    duration: float  # seconds
    intensity: float  # 0..1
    
    def __str__(self) -> str:
        return f"Event({self.type.name}, {self.duration:.1f}s, {self.intensity:.2f})"


class RandomEventSystem:
    """Generates random events at intervals."""
    
    EVENT_TYPES = list(EventType)
    
    def __init__(self, min_interval: float = 15.0, max_interval: float = 45.0):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self._time_until_event = random.uniform(min_interval, max_interval)
        self._current_event: Optional[RandomEvent] = None
        self._event_timer = 0.0
        
    def update(self, dt: float) -> Optional[RandomEvent]:
        """Update the event system. Returns new event if one starts."""
        # Handle current active event
        if self._current_event is not None:
            self._event_timer -= dt
            if self._event_timer <= 0:
                # Event ended
                ended_event = self._current_event
                self._current_event = None
                self._time_until_event = random.uniform(self.min_interval, self.max_interval)
                
        # Check if it's time for new event
        self._time_until_event -= dt
        if self._time_until_event <= 0 and self._current_event is None:
            self._current_event = self._generate_event()
            self._event_timer = self._current_event.duration
            return self._current_event
            
        return None
    
    def _generate_event(self) -> RandomEvent:
        """Generate a random event."""
        event_type = random.choice(self.EVENT_TYPES)
        
        # Different durations based on type
        duration_map = {
            EventType.PALETTE_SHIFT: (5.0, 15.0),
            EventType.FRACTAL_MORPH: (3.0, 8.0),
            EventType.GRAVITY_FLIP: (5.0, 10.0),
            EventType.TIME_WARP: (3.0, 7.0),
            EventType.COLOR_INVERT: (2.0, 5.0),
            EventType.SDF_MUTATION: (5.0, 12.0),
            EventType.ZOOM_PULSE: (4.0, 10.0),
        }
        
        min_dur, max_dur = duration_map.get(event_type, (3.0, 10.0))
        duration = random.uniform(min_dur, max_dur)
        intensity = random.uniform(0.3, 1.0)
        
        return RandomEvent(
            type=event_type,
            duration=duration,
            intensity=intensity
        )
    
    @property
    def active_event(self) -> Optional[RandomEvent]:
        """Get currently active event."""
        return self._current_event
    
    @property
    def time_until_event(self) -> float:
        """Get time until next event."""
        return max(0.0, self._time_until_event)
