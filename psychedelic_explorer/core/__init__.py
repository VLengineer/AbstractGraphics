"""Core package."""
from .game import Game, main
from .input_handler import InputHandler
from .events import StateManager, GameState

__all__ = [
    'Game',
    'main',
    'InputHandler',
    'StateManager',
    'GameState',
]
