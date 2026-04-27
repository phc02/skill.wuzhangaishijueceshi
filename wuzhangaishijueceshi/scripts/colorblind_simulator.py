#!/usr/bin/env python3
"""
Colorblind Simulator for wuzhangaishijueceshi skill.

This module simulates how images appear to users with various types of
color vision deficiencies (CVD) using Machado transformation matrices.
"""

import numpy as np
from PIL import Image


# Machado transformation matrices for different CVD types
# Source: Machado et al. (2009) - "A Physiologically-based Model for Simulation of Color Vision Deficiency"
CVD_MATRICES = {
    'protanopia': {
        'name': 'Protanopia (Red-Blind)',
        'matrix': np.array([
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ])
    },
    'protanomaly': {
        'name': 'Protanomaly (Red-Weak)',
        'matrix': np.array([
            [0.817, 0.183, 0.000],
            [0.333, 0.667, 0.000],
            [0.000, 0.125, 0.875]
        ])
    },
    'deuteranopia': {
        'name': 'Deuteranopia (Green-Blind)',
        'matrix': np.array([
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ])
    },
    'deuteranomaly': {
        'name': 'Deuteranomaly (Green-Weak)',
        'matrix': np.array([
            [0.800, 0.200, 0.000],
            [0.258, 0.742, 0.000],
            [0.000, 0.142, 0.858]
        ])
    },
    'tritanopia': {
        'name': 'Tritanopia (Blue-Blind)',
        'matrix': np.array([
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ])
    },
    'tritanomaly': {
        'name': 'Tritanomaly (Blue-Weak)',
        'matrix': np.array([
            [0.967, 0.033, 0.000],
            [0.000, 0.733, 0.267],
            [0.000, 0.183, 0.817]
        ])
    },
    'achromatopsia': {
        'name': 'Achromatopsia (Total Color Blindness)',
        'matrix': np.array([
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114]
        ])
    },
    'achromatomaly': {
        'name': 'Achromatomaly (Partial Color Blindness)',
        'matrix': np.array([
            [0.618, 0.320, 0.062],
            [0.163, 0.775, 0.062],
            [0.163, 0.320, 0.516]
        ])
    }
}


def simulate_cvd(image_array, deficiency_type='deuteranopia'):
    """
    Simulate color vision deficiency on an image.

    Args:
        image_array: numpy array of shape (H, W, 3) with RGB values (0-255)
        deficiency_type: Type of CVD to simulate

    Returns:
        numpy array: Simulated image
    """
    if deficiency_type not in CVD_MATRICES:
        raise ValueError(f"Unknown deficiency type: {deficiency_type}")

    matrix = CVD_MATRICES[deficiency_type]['matrix']

    # Normalize to 0-1 range
    normalized = image_array.astype(np.float32) / 255.0

    # Apply transformation
    # Reshape for matrix multiplication: (H*W, 3) @ (3, 3) -> (H*W, 3)
    h, w, c = normalized.shape
    flattened = normalized.reshape(-1, 3)
    simulated = np.dot(flattened, matrix.T)

    # Clip and convert back to 0-255
    simulated = np.clip(simulated, 0, 1) * 255
    simulated = simulated.astype(np.uint8)

    # Reshape back to original dimensions
    simulated = simulated.reshape(h, w, c)

    return simulated


def simulate_all_cvd_types(image_array):
    """
    Simulate all CVD types on an image.

    Args:
        image_array: numpy array of shape (H, W, 3) with RGB values (0-255)

    Returns:
        dict: Dictionary of simulated images for each CVD type
    """
    simulations = {}

    for cvd_type in CVD_MATRICES.keys():
        simulations[cvd_type] = {
            'name': CVD_MATRICES[cvd_type]['name'],
            'image': simulate_cvd(image_array, cvd_type)
        }

    return simulations


def create_comparison_grid(original_image, simulations, output_path=None):
    """
    Create a comparison grid showing original and all CVD simulations.

    Args:
        original_image: Original PIL Image
        simulations: Dictionary of simulated images from simulate_all_cvd_types()
        output_path: Optional path to save the grid image

    Returns:
        PIL Image: Comparison grid
    """
    # Get dimensions
    orig_array = np.array(original_image)
    h, w = orig_array.shape[:2]

    # Grid layout: 2 columns, 5 rows (1 original + 8 simulations = 9 items)
    cols = 2
    rows = 5
    padding = 10

    grid_w = w * cols + padding * (cols + 1)
    grid_h = h * rows + padding * (rows + 1)

    # Create white background
    grid = np.ones((grid_h, grid_w, 3), dtype=np.uint8) * 255

    # Place original image at position (0, 0)
    grid[padding:padding+h, padding:padding+w] = orig_array

    # Place simulations starting from position (0, 1)
    cvd_types = list(simulations.keys())
    for i, cvd_type in enumerate(cvd_types):
        # Position in grid: original at (0,0), simulations at (0,1), (1,0), (1,1), etc.
        pos = i + 1  # Skip position 0 (original image)
        row = pos // cols
        col = pos % cols

        y_start = padding + row * (h + padding)
        x_start = padding + col * (w + padding)

        sim_array = simulations[cvd_type]['image']
        # Ensure sim_array has correct shape (resize if needed)
        if sim_array.shape[:2] != (h, w):
            sim_image = Image.fromarray(sim_array)
            sim_image = sim_image.resize((w, h), Image.Resampling.LANCZOS)
            sim_array = np.array(sim_image)

        grid[y_start:y_start+h, x_start:x_start+w] = sim_array

    # Convert to PIL Image
    grid_image = Image.fromarray(grid)

    if output_path:
        grid_image.save(output_path)

    return grid_image


def analyze_cvd_impact(image_array, dominant_colors):
    """
    Analyze how CVD affects the accessibility of dominant colors.

    Args:
        image_array: numpy array of shape (H, W, 3)
        dominant_colors: List of dominant colors from color_analysis.py

    Returns:
        dict: Analysis of CVD impact on color accessibility
    """
    impact_report = {}

    for cvd_type, cvd_info in CVD_MATRICES.items():
        simulated = simulate_cvd(image_array, cvd_type)

        # Analyze how colors change
        color_changes = []
        for color in dominant_colors:
            rgb = np.array([color['rgb']]).reshape(1, 1, 3).astype(np.float32)
            simulated_color = simulate_cvd(rgb, cvd_type)[0, 0]
            simulated_color = tuple(simulated_color.astype(int))

            color_changes.append({
                'original': color['rgb'],
                'simulated': simulated_color,
                'original_hex': color['hex'],
                'simulated_hex': '#{:02x}{:02x}{:02x}'.format(*simulated_color)
            })

        impact_report[cvd_type] = {
            'name': cvd_info['name'],
            'color_changes': color_changes
        }

    return impact_report


def simulate_cvd_on_image(image_path, deficiency_type='deuteranopia', output_path=None):
    """
    Complete CVD simulation on an image file.

    Args:
        image_path: Path to image file
        deficiency_type: Type of CVD to simulate
        output_path: Optional path to save simulated image

    Returns:
        dict: Simulation results
    """
    # Load image
    image = Image.open(image_path)
    image_array = np.array(image)

    # Ensure RGB format
    if image_array.shape[2] == 4:  # RGBA
        image_array = image_array[:, :, :3]

    # Simulate CVD
    simulated = simulate_cvd(image_array, deficiency_type)

    # Convert to PIL Image
    simulated_image = Image.fromarray(simulated)

    if output_path:
        simulated_image.save(output_path)

    return {
        'original': image,
        'simulated': simulated_image,
        'deficiency_type': deficiency_type,
        'deficiency_name': CVD_MATRICES[deficiency_type]['name']
    }


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python colorblind_simulator.py <image_path> [deficiency_type]")
        print(f"Available types: {', '.join(CVD_MATRICES.keys())}")
        sys.exit(1)

    image_path = sys.argv[1]
    deficiency_type = sys.argv[2] if len(sys.argv) > 2 else 'deuteranopia'

    if deficiency_type not in CVD_MATRICES:
        print(f"Error: Unknown deficiency type '{deficiency_type}'")
        print(f"Available types: {', '.join(CVD_MATRICES.keys())}")
        sys.exit(1)

    result = simulate_cvd_on_image(image_path, deficiency_type)

    print(f"Simulation complete!")
    print(f"Deficiency type: {result['deficiency_name']}")
    print(f"Original size: {result['original'].size}")
    print(f"Simulated size: {result['simulated'].size}")
