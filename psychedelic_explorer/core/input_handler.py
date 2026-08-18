"""Input handler for keyboard and mouse."""
import pygame
from typing import Set, Tuple, Dict


class InputHandler:
    """Handles keyboard and mouse input."""
    
    def __init__(self):
        self.keys_pressed: Set[str] = set()
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_delta: Tuple[int, int] = (0, 0)
        self.mouse_buttons: Set[int] = set()
        self.key_events: Dict[str, bool] = {}  # key -> just pressed
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a pygame event."""
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key).upper()
            self.keys_pressed.add(key_name)
            self.key_events[key_name] = True
            
        elif event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key).upper()
            self.keys_pressed.discard(key_name)
            
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_delta = event.rel
            self.mouse_pos = event.pos
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons.add(event.button)
            
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons.discard(event.button)
    
    def update(self) -> Dict:
        """Update input state and return current state dict.
        
        Returns:
            Dict with keys: keys_pressed, mouse_delta, mouse_pos, mouse_buttons
        """
        state = {
            'keys_pressed': self.keys_pressed.copy(),
            'mouse_delta': self.mouse_delta,
            'mouse_pos': self.mouse_pos,
            'mouse_buttons': self.mouse_buttons.copy(),
        }
        
        # Clear transient states
        self.mouse_delta = (0, 0)
        self.key_events.clear()
        
        return state
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is currently held down."""
        return key.upper() in self.keys_pressed
    
    def is_key_just_pressed(self, key: str) -> bool:
        """Check if a key was just pressed this frame."""
        return self.key_events.get(key.upper(), False)
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is held (1=left, 2=middle, 3=right)."""
        return button in self.mouse_buttons
    
    def reset(self) -> None:
        """Reset all input state."""
        self.keys_pressed.clear()
        self.mouse_delta = (0, 0)
        self.mouse_buttons.clear()
        self.key_events.clear()
