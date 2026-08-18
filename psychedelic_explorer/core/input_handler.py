"""Input handler for keyboard and mouse."""
import pygame
import numpy as np
from typing import Set, Tuple, Dict


class InputHandler:
    """Handles keyboard and mouse input with game-oriented actions."""
    
    def __init__(self):
        self.keys_pressed: Set[str] = set()
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_delta: Tuple[int, int] = (0, 0)
        self.mouse_buttons: Set[int] = set()
        self.key_events: Dict[str, bool] = {}  # key -> just pressed
        
        # Action states
        self.move_forward = 0.0
        self.move_backward = 0.0
        self.move_left = 0.0
        self.move_right = 0.0
        self.move_up = 0.0
        self.move_down = 0.0
        self.look_x = 0.0
        self.look_y = 0.0
        self.action_just_pressed = False
        self.boost_active = False
        self.pause_just_pressed = False
        self.world_switch_just_pressed = False
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a pygame event."""
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key).upper()
            self.keys_pressed.add(key_name)
            self.key_events[key_name] = True
            
            # One-shot events
            if event.key == pygame.K_SPACE:
                self.action_just_pressed = True
            elif event.key == pygame.K_ESCAPE:
                self.pause_just_pressed = True
            elif event.key == pygame.K_TAB:
                self.world_switch_just_pressed = True
                
        elif event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key).upper()
            self.keys_pressed.discard(key_name)
            
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_delta = event.rel
            self.mouse_pos = event.pos
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons.add(event.button)
            if event.button == 1:  # Left click = action
                self.action_just_pressed = True
            
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons.discard(event.button)
    
    def update(self) -> Dict:
        """Update input state and return current state dict.
        
        Returns:
            Dict with movement vectors, actions, and mouse data
        """
        keys = pygame.key.get_pressed()
        
        # WASD + QE for movement
        self.move_forward = 1.0 if keys[pygame.K_w] else 0.0
        self.move_backward = 1.0 if keys[pygame.K_s] else 0.0
        self.move_left = 1.0 if keys[pygame.K_a] else 0.0
        self.move_right = 1.0 if keys[pygame.K_d] else 0.0
        self.move_up = 1.0 if keys[pygame.K_q] else 0.0
        self.move_down = 1.0 if keys[pygame.K_e] else 0.0
        
        # Boost (Shift)
        self.boost_active = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Mouse look (scaled)
        self.look_x = self.mouse_delta[0] * 0.002
        self.look_y = self.mouse_delta[1] * 0.002
        
        # Build move vector
        move_vec = np.array([
            self.move_right - self.move_left,
            self.move_up - self.move_down,
            self.move_backward - self.move_forward
        ], dtype=np.float32)
        
        look_vec = np.array([self.look_x, self.look_y], dtype=np.float32)
        
        # Capture one-shot states before clearing
        action = self.action_just_pressed
        pause = self.pause_just_pressed
        switch_world = self.world_switch_just_pressed
        
        # Clear transient states
        self.action_just_pressed = False
        self.pause_just_pressed = False
        self.world_switch_just_pressed = False
        self.mouse_delta = (0, 0)
        self.key_events.clear()
        
        return {
            'move': move_vec,
            'look': look_vec,
            'action': action,
            'boost': self.boost_active,
            'pause': pause,
            'switch_world': switch_world,
            'mouse_pos': self.mouse_pos,
            'mouse_buttons': self.mouse_buttons.copy(),
            'quit': False
        }
    
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
        self.move_forward = 0.0
        self.move_backward = 0.0
        self.move_left = 0.0
        self.move_right = 0.0
        self.move_up = 0.0
        self.move_down = 0.0
        self.look_x = 0.0
        self.look_y = 0.0
        self.action_just_pressed = False
        self.boost_active = False
        self.pause_just_pressed = False
        self.world_switch_just_pressed = False

