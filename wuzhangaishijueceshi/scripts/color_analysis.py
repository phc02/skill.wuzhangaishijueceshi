#!/usr/bin/env python3
"""
Color Analysis Module for wuzhangaishijueceshi skill.

This module handles WCAG contrast ratio calculations and color accessibility analysis.
"""

import numpy as np
from PIL import Image
from collections import defaultdict


def calculate_relative_luminance(rgb):
    """
    Calculate relative luminance of an RGB color using WCAG formula.

    Args:
        rgb: tuple of (R, G, B) values (0-255)

    Returns:
        float: Relative luminance value (0-1)
    """
    r, g, b = [c / 255.0 for c in rgb]

    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def calculate_contrast_ratio(rgb1, rgb2):
    """
    Calculate contrast ratio between two RGB colors.

    Args:
        rgb1: tuple of (R, G, B) values (0-255)
        rgb2: tuple of (R, G, B) values (0-255)

    Returns:
        float: Contrast ratio (1:1 to 21:1)
    """
    l1 = calculate_relative_luminance(rgb1)
    l2 = calculate_relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_compliance(contrast_ratio, is_large_text=False):
    """
    Check if contrast ratio meets WCAG standards.

    Args:
        contrast_ratio: Calculated contrast ratio
        is_large_text: Whether text is large (18pt+ or 14pt+ bold)

    Returns:
        dict: Compliance status for AA and AAA levels
    """
    if is_large_text:
        # Large text requirements
        aa_threshold = 3.0
        aaa_threshold = 4.5
    else:
        # Normal text requirements
        aa_threshold = 4.5
        aaa_threshold = 7.0

    return {
        'aa': contrast_ratio >= aa_threshold,
        'aaa': contrast_ratio >= aaa_threshold,
        'aa_threshold': aa_threshold,
        'aaa_threshold': aaa_threshold,
        'meets_minimum': contrast_ratio >= 3.0  # For non-text elements
    }


def extract_dominant_colors(image, num_colors=15):
    """
    Extract dominant colors from an image using K-means clustering.

    Args:
        image: PIL Image or numpy array
        num_colors: Number of dominant colors to extract

    Returns:
        list: List of dominant RGB colors with frequencies
    """
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    # Flatten image to pixels
    pixels = image_array.reshape(-1, image_array.shape[2])

    # Remove alpha channel if present
    if pixels.shape[1] == 4:
        pixels = pixels[:, :3]

    # Sample pixels for efficiency (max 10000 pixels)
    if len(pixels) > 10000:
        indices = np.random.choice(len(pixels), 10000, replace=False)
        sample_pixels = pixels[indices]
    else:
        sample_pixels = pixels

    # Use K-means to find dominant colors
    from sklearn.cluster import KMeans

    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(sample_pixels)

    # Get cluster centers and counts
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.predict(sample_pixels)
    counts = np.bincount(labels, minlength=num_colors)

    # Sort by frequency
    sorted_indices = np.argsort(counts)[::-1]

    dominant_colors = []
    for idx in sorted_indices:
        color = tuple(colors[idx])
        frequency = counts[idx] / len(sample_pixels)
        dominant_colors.append({
            'rgb': color,
            'frequency': float(frequency),
            'hex': rgb_to_hex(color)
        })

    return dominant_colors


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def analyze_color_pairs(dominant_colors):
    """
    Analyze all pairs of dominant colors for contrast ratios.

    Args:
        dominant_colors: List of dominant colors from extract_dominant_colors()

    Returns:
        list: List of color pair analyses with contrast ratios
    """
    pairs = []

    for i, color1 in enumerate(dominant_colors):
        for j, color2 in enumerate(dominant_colors):
            if i >= j:  # Avoid duplicates and self-pairs
                continue

            contrast = calculate_contrast_ratio(color1['rgb'], color2['rgb'])
            compliance = check_wcag_compliance(contrast)

            pairs.append({
                'color1': color1,
                'color2': color2,
                'contrast_ratio': contrast,
                'compliance': compliance,
                'wcag_level': 'AAA' if compliance['aaa'] else 'AA' if compliance['aa'] else 'Fail'
            })

    # Sort by contrast ratio (lowest first - most problematic)
    pairs.sort(key=lambda x: x['contrast_ratio'])

    return pairs


def analyze_image_colors(image_path, num_colors=15):
    """
    Complete color analysis of an image.

    Args:
        image_path: Path to image file
        num_colors: Number of dominant colors to extract

    Returns:
        dict: Complete color analysis results
    """
    # Load image
    image = Image.open(image_path)

    # Extract dominant colors
    dominant_colors = extract_dominant_colors(image, num_colors)

    # Analyze color pairs
    color_pairs = analyze_color_pairs(dominant_colors)

    # Calculate overall statistics
    total_pairs = len(color_pairs)
    aa_pass = sum(1 for p in color_pairs if p['compliance']['aa'])
    aaa_pass = sum(1 for p in color_pairs if p['compliance']['aaa'])

    return {
        'dominant_colors': dominant_colors,
        'color_pairs': color_pairs,
        'statistics': {
            'total_pairs': total_pairs,
            'aa_pass': aa_pass,
            'aaa_pass': aaa_pass,
            'aa_pass_rate': aa_pass / total_pairs if total_pairs > 0 else 0,
            'aaa_pass_rate': aaa_pass / total_pairs if total_pairs > 0 else 0
        }
    }


def get_colorblind_friendly_colors(dominant_colors, deficiency_type='deuteranopia'):
    """
    Simulate how colors appear to users with color vision deficiencies.

    Args:
        dominant_colors: List of dominant colors
        deficiency_type: Type of color vision deficiency

    Returns:
        list: Colors with simulated appearance
    """
    # Colorblind simulation matrices (Machado)
    matrices = {
        'protanopia': [
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ],
        'deuteranopia': [
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ],
        'tritanopia': [
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ]
    }

    matrix = matrices.get(deficiency_type, matrices['deuteranopia'])

    simulated_colors = []
    for color in dominant_colors:
        r, g, b = color['rgb']
        sim_r = min(255, max(0, int(matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b)))
        sim_g = min(255, max(0, int(matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b)))
        sim_b = min(255, max(0, int(matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b)))

        simulated_colors.append({
            'original': color,
            'simulated': {
                'rgb': (sim_r, sim_g, sim_b),
                'hex': rgb_to_hex((sim_r, sim_g, sim_b))
            }
        })

    return simulated_colors


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python color_analysis.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    result = analyze_image_colors(image_path)

    print(f"Analysis complete!")
    print(f"Dominant colors found: {len(result['dominant_colors'])}")
    print(f"Color pairs analyzed: {result['statistics']['total_pairs']}")
    print(f"AA compliance: {result['statistics']['aa_pass_rate']:.1%}")
    print(f"AAA compliance: {result['statistics']['aaa_pass_rate']:.1%}")

    print("\nTop 5 most problematic color pairs (lowest contrast):")
    for i, pair in enumerate(result['color_pairs'][:5], 1):
        print(f"  {i}. {pair['color1']['hex']} ↔ {pair['color2']['hex']}: "
              f"{pair['contrast_ratio']:.2f}:1 ({pair['wcag_level']})")
