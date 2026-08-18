"""Game state management (FSM)."""
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game


class GameState(Enum):
    """Possible game states."""
    MENU = auto()
    PLAY = auto()
    PAUSE = auto()
    GAMEOVER = auto()


class StateManager:
    """Manages game state transitions."""
    
    def __init__(self, initial_state: GameState = GameState.MENU):
        self._state = initial_state
        self._previous_state: Optional[GameState] = None
        self._state_changed = False
        
    @property
    def current(self) -> GameState:
        """Get current state."""
        return self._state
    
    @property
    def previous(self) -> Optional[GameState]:
        """Get previous state."""
        return self._previous_state
    
    @property
    def changed(self) -> bool:
        """Check if state changed this frame."""
        return self._state_changed
    
    def set(self, new_state: GameState) -> None:
        """Set new state."""
        if new_state != self._state:
            self._previous_state = self._state
            self._state = new_state
            self._state_changed = True
    
    def to_menu(self) -> None:
        """Transition to menu."""
        self.set(GameState.MENU)
    
    def to_play(self) -> None:
        """Transition to play."""
        self.set(GameState.PLAY)
    
    def to_pause(self) -> None:
        """Transition to pause."""
        self.set(GameState.PAUSE)
    
    def to_gameover(self) -> None:
        """Transition to game over."""
        self.set(GameState.GAMEOVER)
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._state == GameState.PLAY
    
    def is_menu(self) -> bool:
        """Check if in menu."""
        return self._state == GameState.MENU
    
    def is_paused(self) -> bool:
        """Check if paused."""
        return self._state == GameState.PAUSE
    
    def is_gameover(self) -> bool:
        """Check if game over."""
        return self._state == GameState.GAMEOVER
    
    def update(self) -> None:
        """Call at end of frame to reset changed flag."""
        self._state_changed = False
