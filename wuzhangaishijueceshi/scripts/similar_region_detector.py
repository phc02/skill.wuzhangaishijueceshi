#!/usr/bin/env python3
"""
Similar Color Region Detector for wuzhangaishijueceshi skill.

This module detects regions with perceptually similar colors that may cause
accessibility issues for users with color vision deficiencies.

Uses CIEDE2000 color difference metric for perceptually accurate color comparison.
"""

import numpy as np
from PIL import Image
from skimage import segmentation, measure
from skimage.color import rgb2lab, lab2rgb
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# Patch for NumPy 2.x compatibility with colormath
if not hasattr(np, 'asscalar'):
    np.asscalar = lambda a: a.item()


def rgb_to_lab(rgb_array):
    """
    Convert RGB image array to Lab color space.

    Args:
        rgb_array: numpy array of shape (H, W, 3) with RGB values (0-255)

    Returns:
        numpy array of Lab color space values
    """
    # Normalize RGB to 0-1 range
    rgb_normalized = rgb_array.astype(np.float32) / 255.0

    # Convert to Lab using skimage
    lab_array = rgb2lab(rgb_normalized)

    return lab_array


def calculate_region_color(lab_image, segments, region_id):
    """
    Calculate the average Lab color of a region.

    Args:
        lab_image: Lab color space image array
        segments: Superpixel segmentation array
        region_id: ID of the region to analyze

    Returns:
        tuple: (L, a, b) Lab color values
    """
    mask = segments == region_id
    if not np.any(mask):
        return None

    region_pixels = lab_image[mask]
    avg_l = np.mean(region_pixels[:, 0])
    avg_a = np.mean(region_pixels[:, 1])
    avg_b = np.mean(region_pixels[:, 2])

    return (avg_l, avg_a, avg_b)


def get_adjacent_regions(segments, region_id):
    """
    Get IDs of regions adjacent to the specified region.

    Args:
        segments: Superpixel segmentation array
        region_id: ID of the region

    Returns:
        set: Set of adjacent region IDs
    """
    mask = segments == region_id
    if not np.any(mask):
        return set()

    # Find boundary pixels
    from scipy import ndimage
    boundary = ndimage.binary_dilation(mask) & ~mask

    # Get adjacent region IDs
    adjacent_ids = set(np.unique(segments[boundary]))
    adjacent_ids.discard(region_id)  # Remove self

    return adjacent_ids


def ciede2000(color1, color2):
    """
    Calculate CIEDE2000 color difference between two Lab colors.

    Args:
        color1: tuple of (L, a, b) Lab values
        color2: tuple of (L, a, b) Lab values

    Returns:
        float: Delta E (CIEDE2000) value
    """
    lab1 = LabColor(color1[0], color1[1], color1[2])
    lab2 = LabColor(color2[0], color2[1], color2[2])

    result = delta_e_cie2000(lab1, lab2)

    # Handle numpy array return value (colormath compatibility)
    if hasattr(result, 'item'):
        return result.item()
    elif hasattr(result, 'asscalar'):
        return result.asscalar()
    else:
        return float(result)


def analyze_similar_colors(image, threshold=5.0, n_segments=100):
    """
    Analyze similar color regions in image using CIEDE2000 metric.

    Args:
        image: PIL Image or numpy array (RGB, 0-255)
        threshold: Delta E threshold for flagging similar colors (default: 5.0)
        n_segments: Number of superpixels for segmentation (default: 100)

    Returns:
        dict: Analysis results with regions, similarities, and issues
    """
    # Convert to numpy array if PIL Image
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    # Ensure RGB format
    if image_array.shape[2] == 4:  # RGBA
        image_array = image_array[:, :, :3]

    # Convert to Lab color space
    lab_image = rgb_to_lab(image_array)

    # Apply SLIC superpixel segmentation
    segments = segmentation.slic(
        image_array,
        n_segments=n_segments,
        compactness=10,
        start_label=1
    )

    # Calculate color for each region
    region_colors = {}
    for region_id in np.unique(segments):
        color = calculate_region_color(lab_image, segments, region_id)
        if color:
            region_colors[region_id] = color

    # Find similar regions
    similar_regions = []
    checked_pairs = set()

    for region_id in region_colors.keys():
        neighbors = get_adjacent_regions(segments, region_id)

        for neighbor_id in neighbors:
            # Avoid duplicate checks
            pair = tuple(sorted([region_id, neighbor_id]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            if neighbor_id in region_colors:
                delta_e = ciede2000(
                    region_colors[region_id],
                    region_colors[neighbor_id]
                )

                if delta_e < threshold:
                    similar_regions.append({
                        'region1': int(region_id),
                        'region2': int(neighbor_id),
                        'delta_e': float(delta_e),
                        'color1': region_colors[region_id],
                        'color2': region_colors[neighbor_id]
                    })

    # Sort by delta_e (most similar first)
    similar_regions.sort(key=lambda x: x['delta_e'])

    return {
        'similar_regions': similar_regions,
        'threshold': threshold,
        'total_issues': len(similar_regions),
        'segments': segments,
        'region_colors': {int(k): v for k, v in region_colors.items()}
    }


def generate_similarity_heatmap(image, analysis_result):
    """
    Generate a heatmap visualization of similar color regions.

    Args:
        image: Original image (PIL Image or numpy array)
        analysis_result: Result from analyze_similar_colors()

    Returns:
        numpy array: Heatmap image
    """
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    # Create grayscale heatmap
    heatmap = np.zeros(image_array.shape[:2], dtype=np.float32)
    segments = analysis_result['segments']

    # Mark similar regions with intensity based on delta_e
    for issue in analysis_result['similar_regions']:
        region1_mask = segments == issue['region1']
        region2_mask = segments == issue['region2']

        # Higher intensity for more similar colors (lower delta_e)
        intensity = max(0, 1 - (issue['delta_e'] / analysis_result['threshold']))
        heatmap[region1_mask] = np.maximum(heatmap[region1_mask], intensity)
        heatmap[region2_mask] = np.maximum(heatmap[region2_mask], intensity)

    # Normalize to 0-255
    if heatmap.max() > 0:
        heatmap = (heatmap / heatmap.max() * 255).astype(np.uint8)
    else:
        heatmap = np.zeros_like(heatmap, dtype=np.uint8)

    return heatmap


def get_region_boundaries(segments, region_id):
    """
    Get the bounding box and boundary pixels of a region.

    Args:
        segments: Superpixel segmentation array
        region_id: ID of the region

    Returns:
        dict: Bounding box and boundary information
    """
    mask = segments == region_id
    if not np.any(mask):
        return None

    # Find bounding box
    rows, cols = np.where(mask)
    bbox = {
        'y_min': int(rows.min()),
        'y_max': int(rows.max()),
        'x_min': int(cols.min()),
        'x_max': int(cols.max())
    }

    # Calculate center
    bbox['center_x'] = (bbox['x_min'] + bbox['x_max']) // 2
    bbox['center_y'] = (bbox['y_min'] + bbox['y_max']) // 2

    # Calculate area
    bbox['area'] = int(np.sum(mask))

    return bbox


def analyze_image_for_similar_colors(image_path, threshold=5.0):
    """
    Complete analysis of an image for similar color regions.

    Args:
        image_path: Path to image file
        threshold: Delta E threshold (default: 5.0)

    Returns:
        dict: Complete analysis results
    """
    # Load image
    image = Image.open(image_path)

    # Analyze similar colors
    analysis_result = analyze_similar_colors(image, threshold=threshold)

    # Add region boundary information
    for issue in analysis_result['similar_regions']:
        for region_key in ['region1', 'region2']:
            region_id = issue[region_key]
            boundaries = get_region_boundaries(
                analysis_result['segments'],
                region_id
            )
            if boundaries:
                issue[f'{region_key}_boundaries'] = boundaries

    # Generate heatmap
    heatmap = generate_similarity_heatmap(image, analysis_result)
    analysis_result['heatmap'] = heatmap

    return analysis_result


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python similar_region_detector.py <image_path> [threshold]")
        sys.exit(1)

    image_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    result = analyze_image_for_similar_colors(image_path, threshold)

    print(f"Analysis complete!")
    print(f"Total similar regions found: {result['total_issues']}")
    print(f"Threshold: {result['threshold']} Delta E")

    if result['similar_regions']:
        print("\nTop 5 most similar regions:")
        for i, issue in enumerate(result['similar_regions'][:5], 1):
            print(f"  {i}. Region {issue['region1']} ↔ Region {issue['region2']}: "
                  f"ΔE = {issue['delta_e']:.2f}")
