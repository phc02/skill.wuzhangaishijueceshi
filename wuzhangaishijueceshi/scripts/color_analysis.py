#!/usr/bin/env python3
"""
Color Analysis Module for wuzhangaishijueceshi skill.

This module handles WCAG contrast ratio calculations, color accessibility analysis,
and smart color correction suggestions.
"""

import numpy as np
from PIL import Image
from collections import defaultdict
import colorsys  # 新增：用于 HSL 和 RGB 之间的转换


def calculate_relative_luminance(rgb):
    """
    Calculate relative luminance of an RGB color using WCAG formula.
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
    """
    l1 = calculate_relative_luminance(rgb1)
    l2 = calculate_relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_compliance(contrast_ratio, is_large_text=False):
    """
    Check if contrast ratio meets WCAG standards.
    """
    if is_large_text:
        aa_threshold = 3.0
        aaa_threshold = 4.5
    else:
        aa_threshold = 4.5
        aaa_threshold = 7.0

    return {
        'aa': contrast_ratio >= aa_threshold,
        'aaa': contrast_ratio >= aaa_threshold,
        'aa_threshold': aa_threshold,
        'aaa_threshold': aaa_threshold,
        'meets_minimum': contrast_ratio >= 3.0 
    }


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def suggest_compliant_color(adjustable_rgb, fixed_rgb, target_ratio=4.5):
    """
    【核心算法】智能色值推算：
    通过在 HSL 色彩空间使用二分查找法微调亮度 (Lightness)，
    计算出在保持色相和饱和度不变的前提下，能满足目标对比度的最接近颜色。

    Args:
        adjustable_rgb: 需要被调整的前景颜色 (R, G, B)
        fixed_rgb: 固定的背景颜色 (R, G, B)
        target_ratio: 目标对比度 (如 AA 标准为 4.5)

    Returns:
        tuple: 修正后的 (R, G, B) 颜色
    """
    current_ratio = calculate_contrast_ratio(adjustable_rgb, fixed_rgb)
    if current_ratio >= target_ratio:
        return adjustable_rgb

    # 将 RGB (0-255) 转换为 HLS (0.0-1.0)
    r, g, b = [c / 255.0 for c in adjustable_rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    l_adj = calculate_relative_luminance(adjustable_rgb)
    l_fixed = calculate_relative_luminance(fixed_rgb)

    # 判断调整方向：
    # 如果待调颜色比背景亮，说明需要让它更亮才能拉开对比度；
    # 如果待调颜色比背景暗，说明需要让它更暗。
    if l_adj > l_fixed or (l_adj == l_fixed and l_fixed < 0.5):
        low_l, high_l = l, 1.0  # 变亮区间
        make_lighter = True
    else:
        low_l, high_l = 0.0, l  # 变暗区间
        make_lighter = False

    best_rgb = adjustable_rgb
    
    # 执行二分查找 (10次迭代足以在 0-255 范围内找到精确值)
    for _ in range(10):
        mid_l = (low_l + high_l) / 2
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, mid_l, s)
        test_rgb = (int(new_r * 255), int(new_g * 255), int(new_b * 255))
        
        ratio = calculate_contrast_ratio(test_rgb, fixed_rgb)

        if ratio >= target_ratio:
            best_rgb = test_rgb
            # 已经及格了，尝试向原始颜色稍微靠拢一点（寻找及格线边缘的最优解）
            if make_lighter:
                high_l = mid_l
            else:
                low_l = mid_l
        else:
            # 还不及格，继续往极端方向走
            if make_lighter:
                low_l = mid_l
            else:
                high_l = mid_l

    # 最终的安全验证 (Edge Case fallback)
    # 有些极端颜色（比如中度灰背景），可能怎么调也达不到 7.0:1 的对比度
    # 此时直接退化为极端的纯白或纯黑
    final_ratio = calculate_contrast_ratio(best_rgb, fixed_rgb)
    if final_ratio < target_ratio:
        white_ratio = calculate_contrast_ratio((255, 255, 255), fixed_rgb)
        black_ratio = calculate_contrast_ratio((0, 0, 0), fixed_rgb)
        if white_ratio >= target_ratio:
            return (255, 255, 255)
        elif black_ratio >= target_ratio:
            return (0, 0, 0)
        else:
            return (255, 255, 255) if white_ratio > black_ratio else (0, 0, 0)

    return best_rgb


def extract_dominant_colors(image, num_colors=15):
    """Extract dominant colors from an image using K-means clustering."""
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    pixels = image_array.reshape(-1, image_array.shape[2])
    if pixels.shape[1] == 4:
        pixels = pixels[:, :3]

    if len(pixels) > 10000:
        indices = np.random.choice(len(pixels), 10000, replace=False)
        sample_pixels = pixels[indices]
    else:
        sample_pixels = pixels

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(sample_pixels)

    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.predict(sample_pixels)
    counts = np.bincount(labels, minlength=num_colors)

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


def analyze_color_pairs(dominant_colors):
    """
    Analyze all pairs of dominant colors and provide smart suggestions if they fail WCAG.
    """
    pairs = []

    for i, color1 in enumerate(dominant_colors):
        for j, color2 in enumerate(dominant_colors):
            if i >= j:  
                continue

            contrast = calculate_contrast_ratio(color1['rgb'], color2['rgb'])
            compliance = check_wcag_compliance(contrast)
            
            pair_data = {
                'color1': color1,
                'color2': color2,
                'contrast_ratio': contrast,
                'compliance': compliance,
                'wcag_level': 'AAA' if compliance['aaa'] else 'AA' if compliance['aa'] else 'Fail',
                'suggestion': None
            }

            # 如果不满足 AA 级别，则触发智能推算算法
            if not compliance['aa']:
                # 假设 color2 是底色，推算 color1 的合规色值
                suggested_rgb = suggest_compliant_color(color1['rgb'], color2['rgb'], 4.5)
                pair_data['suggestion'] = {
                    'hex': rgb_to_hex(suggested_rgb),
                    'rgb': suggested_rgb,
                    'target_ratio': 4.5
                }

            pairs.append(pair_data)

    pairs.sort(key=lambda x: x['contrast_ratio'])
    return pairs


def analyze_image_colors(image_path, num_colors=15):
    """Complete color analysis of an image."""
    image = Image.open(image_path)
    dominant_colors = extract_dominant_colors(image, num_colors)
    color_pairs = analyze_color_pairs(dominant_colors)

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
    """Simulate how colors appear to users with color vision deficiencies."""
    matrices = {
        'protanopia': [[0.567, 0.433, 0.000], [0.558, 0.442, 0.000], [0.000, 0.242, 0.758]],
        'deuteranopia': [[0.625, 0.375, 0.000], [0.700, 0.300, 0.000], [0.000, 0.300, 0.700]],
        'tritanopia': [[0.950, 0.050, 0.000], [0.000, 0.433, 0.567], [0.000, 0.475, 0.525]]
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
    import sys
    if len(sys.argv) < 2:
        print("Usage: python color_analysis.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    result = analyze_image_colors(image_path)

    print(f"Analysis complete!")
    print(f"Dominant colors found: {len(result['dominant_colors'])}")
    print(f"AA compliance: {result['statistics']['aa_pass_rate']:.1%}")
    
    print("\nTop 5 most problematic color pairs (lowest contrast):")
    for i, pair in enumerate(result['color_pairs'][:5], 1):
        suggestion_text = ""
        if pair['suggestion']:
            suggestion_text = f" -> Suggest modifying {pair['color1']['hex']} to {pair['suggestion']['hex']}"
            
        print(f"  {i}. {pair['color1']['hex']} ↔ {pair['color2']['hex']}: "
              f"{pair['contrast_ratio']:.2f}:1 ({pair['wcag_level']}){suggestion_text}")