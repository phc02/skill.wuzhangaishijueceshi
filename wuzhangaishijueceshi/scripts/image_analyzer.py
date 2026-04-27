#!/usr/bin/env python3
"""
Image Analyzer Module for wuzhangaishijueceshi skill.

This module handles image loading, preprocessing, and color extraction.
"""

import os
import numpy as np
from PIL import Image


def load_image(image_path, max_size=2000):
    """
    Load and preprocess an image for analysis.

    Args:
        image_path: Path to image file
        max_size: Maximum dimension for resizing (maintains aspect ratio)

    Returns:
        PIL Image object
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        image = Image.open(image_path)

        # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if too large (for performance)
        width, height = image.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image

    except Exception as e:
        raise ValueError(f"Error loading image '{image_path}': {e}")


def analyze_image_file(image_path):
    """
    Complete analysis of an image file.

    Args:
        image_path: Path to image file

    Returns:
        dict: Complete analysis results
    """
    # Import analysis modules
    from color_analysis import analyze_image_colors
    from similar_region_detector import analyze_similar_colors, generate_similarity_heatmap
    from colorblind_simulator import simulate_all_cvd_types, create_comparison_grid
    from html_report_generator import image_to_base64

    # Load image
    image = load_image(image_path)
    image_array = np.array(image)

    # Analyze colors
    color_analysis = analyze_image_colors(image_path)

    # Analyze similar regions
    similar_result = analyze_similar_colors(image, threshold=5.0)

    # Generate heatmap
    heatmap = generate_similarity_heatmap(image, similar_result)
    heatmap_image = Image.fromarray(heatmap)

    # Simulate colorblindness
    cvd_simulations = simulate_all_cvd_types(image_array)

    # Create comparison grid
    comparison_grid = create_comparison_grid(image, cvd_simulations)

    # Prepare CVD analysis data
    cvd_analysis = {}
    for cvd_type, cvd_data in cvd_simulations.items():
        cvd_image = Image.fromarray(cvd_data['image'])
        cvd_analysis[cvd_type] = {
            'name': cvd_data['name'],
            'image_base64': image_to_base64(cvd_image)
        }

    # Add comparison grid to CVD analysis
    cvd_analysis['comparison_grid'] = {
        'name': '对比图',
        'image_base64': image_to_base64(comparison_grid)
    }

    # Prepare similar regions data
    similar_regions_data = {
        'similar_regions': similar_result['similar_regions'],
        'threshold': similar_result['threshold'],
        'total_issues': similar_result['total_issues'],
        'heatmap_base64': image_to_base64(heatmap_image)
    }

    # Compile results
    results = {
        'input_source': image_path,
        'original_image': image,
        'color_analysis': color_analysis,
        'similar_regions': similar_regions_data,
        'cvd_analysis': cvd_analysis,
        'image_info': {
            'size': image.size,
            'mode': image.mode
        }
    }

    return results


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python image_analyzer.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        result = analyze_image_file(image_path)
        print(f"Analysis complete!")
        print(f"Image size: {result['image_info']['size']}")
        print(f"Dominant colors: {len(result['color_analysis']['dominant_colors'])}")
        print(f"Similar regions: {result['similar_regions']['total_issues']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
