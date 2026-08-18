"""Noise utilities for procedural generation."""
import numpy as np


def perlin_noise_2d(x: np.ndarray, y: np.ndarray, seed: int = 0) -> np.ndarray:
    """Simple 2D Perlin-like noise using gradient interpolation."""
    rng = np.random.default_rng(seed)
    
    # Grid coordinates
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Fractional parts
    fx = x - x0
    fy = y - y0
    
    # Smoothstep
    sx = fx * fx * (3 - 2 * fx)
    sy = fy * fy * (3 - 2 * fy)
    
    # Generate gradients (pseudo-random based on grid position)
    def gradient(ix, iy):
        angle = rng.uniform(0, 2 * np.pi, size=(ix.max() - ix.min() + 2, 
                                                  iy.max() - iy.min() + 2))
        return np.stack([np.cos(angle), np.sin(angle)], axis=-1)
    
    # Simple hash-based gradients
    def get_grad(ix, iy):
        h = (ix * 374761393 + iy * 668265263) % 2147483647
        angle = 2 * np.pi * (h / 2147483647.0)
        return np.array([np.cos(angle), np.sin(angle)])
    
    # Interpolate
    g00 = get_grad(x0, y0)
    g10 = get_grad(x1, y0)
    g01 = get_grad(x0, y1)
    g11 = get_grad(x1, y1)
    
    d00 = (x - x0) * g00[0] + (y - y0) * g00[1]
    d10 = (x - x1) * g10[0] + (y - y0) * g10[1]
    d01 = (x - x0) * g01[0] + (y - y1) * g01[1]
    d11 = (x - x1) * g11[0] + (y - y1) * g11[1]
    
    # Bilinear interpolation with smoothstep
    result = (
        (1 - sx) * (1 - sy) * d00 +
        sx * (1 - sy) * d10 +
        (1 - sx) * sy * d01 +
        sx * sy * d11
    )
    
    return result


def value_noise_2d(x: np.ndarray, y: np.ndarray, octaves: int = 4, 
                   persistence: float = 0.5) -> np.ndarray:
    """Fractal Brownian Motion using value noise."""
    result = np.zeros_like(x)
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    
    for i in range(octaves):
        # Grid-based value noise
        xf = x * frequency
        yf = y * frequency
        
        xi = np.floor(xf).astype(int)
        yi = np.floor(yf).astype(int)
        fx = xf - xi
        fy = yf - yi
        
        # Smoothstep
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        
        # Hash values at corners
        def hash_val(ix, iy):
            h = (ix * 374761393 + iy * 668265263) % 2147483647
            return h / 2147483647.0
        
        v00 = hash_val(xi, yi)
        v10 = hash_val(xi + 1, yi)
        v01 = hash_val(xi, yi + 1)
        v11 = hash_val(xi + 1, yi + 1)
        
        noise = (
            (1 - sx) * (1 - sy) * v00 +
            sx * (1 - sy) * v10 +
            (1 - sx) * sy * v01 +
            sx * sy * v11
        )
        
        result += noise * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= 2
    
    return result / max_value if max_value > 0 else result
