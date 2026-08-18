"""Utility module for palette generation."""
import numpy as np


def generate_palette(seed: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Generate two psychedelic color palettes using cosine-based approach.
    
    Returns:
        Tuple of (palette_a, palette_b), each shape (4,) - coefficients for cosine palette
    """
    rng = np.random.default_rng(int(seed * 1000))
    
    # Palette A coefficients
    a = rng.uniform(0.5, 1.5)
    b = rng.uniform(0.3, 0.7)
    c = rng.uniform(0.5, 2.0)
    d = rng.uniform(0.0, 6.28)
    palette_a = np.array([a, b, c, d], dtype=np.float32)
    
    # Palette B - offset from A
    palette_b = np.array([
        a + rng.uniform(-0.3, 0.3),
        b + rng.uniform(-0.2, 0.2),
        c + rng.uniform(-0.5, 0.5),
        d + rng.uniform(-1.0, 1.0)
    ], dtype=np.float32)
    
    return palette_a, palette_b


def get_default_palettes() -> list[tuple[np.ndarray, np.ndarray]]:
    """Return preset palettes for manual selection (keys 1-4)."""
    presets = [
        # Rainbow
        (np.array([1.0, 0.5, 0.5, 0.0], dtype=np.float32),
         np.array([1.0, 0.5, 0.5, 0.33], dtype=np.float32)),
        # Fire
        (np.array([1.0, 0.6, 1.0, 0.0], dtype=np.float32),
         np.array([1.0, 0.6, 0.5, 0.2], dtype=np.float32)),
        # Ice
        (np.array([1.0, 0.4, 0.7, 0.5], dtype=np.float32),
         np.array([1.0, 0.4, 0.3, 0.8], dtype=np.float32)),
        # Neon
        (np.array([1.0, 0.8, 1.5, 0.2], dtype=np.float32),
         np.array([1.0, 0.8, 0.8, 0.6], dtype=np.float32)),
    ]
    return presets
