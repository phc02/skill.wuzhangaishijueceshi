#!/usr/bin/env python3
"""
Color Analysis Module for wuzhangaishijueceshi skill.

This module handles WCAG contrast ratio calculations, color accessibility analysis,
APCA (WCAG 3.0) perception modeling, Dark Mode robustness, and smart color correction suggestions.
"""

import numpy as np
from PIL import Image
import colorsys
import math

# ==========================================
# 权威数据字典：Okabe-Ito 色盲安全调色盘
# ==========================================
OKABE_ITO_PALETTE = [
    {"name": "Black", "hex": "#000000", "rgb": (0, 0, 0)},
    {"name": "Orange", "hex": "#E69F00", "rgb": (230, 159, 0)},
    {"name": "Sky Blue", "hex": "#56B4E9", "rgb": (86, 180, 233)},
    {"name": "Bluish Green", "hex": "#009E73", "rgb": (0, 158, 115)},
    {"name": "Yellow", "hex": "#F0E442", "rgb": (240, 228, 66)},
    {"name": "Blue", "hex": "#0072B2", "rgb": (0, 114, 178)},
    {"name": "Vermilion", "hex": "#D55E00", "rgb": (213, 94, 0)},
    {"name": "Reddish Purple", "hex": "#CC79A7", "rgb": (204, 121, 167)}
]


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb).upper()


# ==========================================
# WCAG 2.1 古典算法 (相对亮度与对比度比例)
# ==========================================
def calculate_relative_luminance(rgb):
    """
    Calculate relative luminance of an RGB color using WCAG 2.1 formula.
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
    Calculate WCAG 2.1 contrast ratio between two RGB colors.
    """
    l1 = calculate_relative_luminance(rgb1)
    l2 = calculate_relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


# ==========================================
# APCA (WCAG 3.0) 现代算法核心
# ==========================================
def calculate_apca_contrast(txt_rgb, bg_rgb):
    """
    计算 APCA (Accessible Perceptual Contrast Algorithm) 的 Lc 值。
    这个算法对文本在亮底和暗底上的表现做了不对称处理，更贴近人类视觉感知。
    注意：这里实现的是 APCA 0.0.98G 简化近似版，用于概念验证和诊断。
    
    Returns:
        float: Lightness Contrast (Lc) 值，范围通常在 -108 到 106 之间。
               正值表示暗字亮底，负值表示亮字暗底。绝对值越大对比度越好。
    """
    # 转换为 0-255 空间的线性亮度 (sRGB 简单反色调映射)
    def to_y(c):
        c = c / 255.0
        return math.pow(c, 2.4) if c > 0.022 else c / 12.92

    txt_y = 0.2126 * to_y(txt_rgb[0]) + 0.7152 * to_y(txt_rgb[1]) + 0.0722 * to_y(txt_rgb[2])
    bg_y  = 0.2126 * to_y(bg_rgb[0])  + 0.7152 * to_y(bg_rgb[1])  + 0.0722 * to_y(bg_rgb[2])

    # APCA 常数 (近似值)
    norm_bg = 0.56
    norm_txt = 0.57
    rev_txt = 0.62
    rev_bg = 0.65
    blk_thrs = 0.022
    blk_clmp = 0.01414

    # 软钳制暗色
    if txt_y < blk_thrs: txt_y += (blk_thrs - txt_y) ** 1.414
    if bg_y < blk_thrs: bg_y += (blk_thrs - bg_y) ** 1.414

    # 计算对比度 (SAPCs)
    if abs(bg_y - txt_y) < 0.0005: return 0.0

    if bg_y > txt_y:
        # 暗文本在亮背景上
        sapc = (math.pow(bg_y, norm_bg) - math.pow(txt_y, norm_txt)) * 1.14
        return sapc * 100 if sapc > 0.1 else 0.0
    else:
        # 亮文本在暗背景上
        sapc = (math.pow(bg_y, rev_bg) - math.pow(txt_y, rev_txt)) * 1.14
        return sapc * 100 if sapc < -0.1 else 0.0


# ==========================================
# 综合合规性校验引擎
# ==========================================
def check_comprehensive_compliance(rgb1, rgb2):
    """
    进行全面的合规性校验，包括 WCAG 2.1 (文本与非文本) 和 APCA。
    """
    contrast = calculate_contrast_ratio(rgb1, rgb2)
    # APCA 结果，取绝对值以便后续评估
    apca_lc = abs(calculate_apca_contrast(rgb1, rgb2))
    
    return {
        # WCAG 2.1 经典指标
        'ratio': contrast,
        'aa_normal': contrast >= 4.5,
        'aaa_normal': contrast >= 7.0,
        'aa_large': contrast >= 3.0,
        'aaa_large': contrast >= 4.5,
        'ui_component': contrast >= 3.0,  # 新增：非文本 UI 控件标准 (WCAG 1.4.11)
        
        # APCA 指标 (WCAG 3.0 候选)
        'apca_lc': apca_lc,
        'apca_pass_normal': apca_lc >= 60,  # Lc 60 是普通文本的推荐基线
        'apca_pass_large': apca_lc >= 45    # Lc 45 适合大文本
    }


# ==========================================
# 深色模式翻转鲁棒性评估
# ==========================================
def test_dark_mode_robustness(fg_rgb, bg_rgb):
    """
    测试这对颜色在深色模式下的表现。
    如果背景色较亮，我们将其“翻转”为一个深色背景（如深灰 #1E1E1E），
    然后测试前景文本在这个新深底上的对比度，看是否会“糊掉”。
    """
    l_bg = calculate_relative_luminance(bg_rgb)
    
    # 如果原本就是深色背景，就不做深色模式翻转测试了
    if l_bg < 0.2:
        return {'applicable': False}
        
    # 模拟标准的深色背景 (约 #1E1E1E)
    simulated_dark_bg = (30, 30, 30)
    
    # 测试原前景色在深色背景上的表现
    robust_contrast = calculate_contrast_ratio(fg_rgb, simulated_dark_bg)
    
    return {
        'applicable': True,
        'simulated_bg_hex': rgb_to_hex(simulated_dark_bg),
        'contrast_on_dark': robust_contrast,
        'survives_dark_mode': robust_contrast >= 4.5
    }


# ==========================================
# 智能修复工单算法
# ==========================================
def find_nearest_okabe_ito_color(target_rgb, bg_rgb, min_ratio=4.5):
    """
    在 Okabe-Ito 色盲安全库中，寻找在背景上合规且色彩空间距离最近的安全色。
    """
    best_color = None
    min_dist = float('inf')
    
    for safe_color in OKABE_ITO_PALETTE:
        safe_rgb = safe_color['rgb']
        if calculate_contrast_ratio(safe_rgb, bg_rgb) >= min_ratio:
            # 简单的欧氏距离比较 (在 RGB 空间粗略估计颜色差异)
            dist = math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(target_rgb, safe_rgb)))
            if dist < min_dist:
                min_dist = dist
                best_color = safe_color
                
    return best_color


def suggest_compliant_color(adjustable_rgb, fixed_rgb, target_ratio=4.5):
    """
    使用二分查找法在 HSL 色彩空间微调亮度，推算出满足对比度的最接近颜色。
    """
    current_ratio = calculate_contrast_ratio(adjustable_rgb, fixed_rgb)
    if current_ratio >= target_ratio:
        return adjustable_rgb

    r, g, b = [c / 255.0 for c in adjustable_rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    l_adj = calculate_relative_luminance(adjustable_rgb)
    l_fixed = calculate_relative_luminance(fixed_rgb)

    if l_adj > l_fixed or (l_adj == l_fixed and l_fixed < 0.5):
        low_l, high_l, make_lighter = l, 1.0, True
    else:
        low_l, high_l, make_lighter = 0.0, l, False

    best_rgb = adjustable_rgb
    
    for _ in range(10):
        mid_l = (low_l + high_l) / 2
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, mid_l, s)
        test_rgb = (int(new_r * 255), int(new_g * 255), int(new_b * 255))
        
        ratio = calculate_contrast_ratio(test_rgb, fixed_rgb)

        if ratio >= target_ratio:
            best_rgb = test_rgb
            if make_lighter: high_l = mid_l
            else: low_l = mid_l
        else:
            if make_lighter: low_l = mid_l
            else: high_l = mid_l

    # Fallback to white/black if impossible
    final_ratio = calculate_contrast_ratio(best_rgb, fixed_rgb)
    if final_ratio < target_ratio:
        w_ratio = calculate_contrast_ratio((255, 255, 255), fixed_rgb)
        b_ratio = calculate_contrast_ratio((0, 0, 0), fixed_rgb)
        if w_ratio >= target_ratio: return (255, 255, 255)
        elif b_ratio >= target_ratio: return (0, 0, 0)
        return (255, 255, 255) if w_ratio > b_ratio else (0, 0, 0)

    return best_rgb


# ==========================================
# 图像处理与流程管线
# ==========================================
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
    Analyze all pairs of dominant colors and provide comprehensive data.
    """
    pairs = []

    for i, color1 in enumerate(dominant_colors):
        for j, color2 in enumerate(dominant_colors):
            if i >= j:  
                continue

            # 假设 color2 (频率更高或者在下层) 是背景
            compliance_data = check_comprehensive_compliance(color1['rgb'], color2['rgb'])
            dark_mode_data = test_dark_mode_robustness(color1['rgb'], color2['rgb'])
            
            pair_data = {
                'color1': color1,
                'color2': color2,
                'metrics': compliance_data,
                'dark_mode_eval': dark_mode_data,
                'suggestion': None,
                'safe_palette_suggestion': None
            }

            # 如果不满足 AA 级别，提供智能修复方案
            if not compliance_data['aa_normal']:
                # 方案 1: 算法微调亮度
                suggested_rgb = suggest_compliant_color(color1['rgb'], color2['rgb'], 4.5)
                pair_data['suggestion'] = {
                    'hex': rgb_to_hex(suggested_rgb),
                    'rgb': suggested_rgb
                }
                
                # 方案 2: 推荐 Okabe-Ito 安全分类色
                safe_color = find_nearest_okabe_ito_color(color1['rgb'], color2['rgb'], 4.5)
                if safe_color:
                    pair_data['safe_palette_suggestion'] = safe_color

            pairs.append(pair_data)

    # 按照 WCAG 比例从小到大排序 (问题最严重的放前面)
    pairs.sort(key=lambda x: x['metrics']['ratio'])
    return pairs


def analyze_image_colors(image_path, num_colors=15):
    """Complete color analysis of an image."""
    image = Image.open(image_path)
    dominant_colors = extract_dominant_colors(image, num_colors)
    color_pairs = analyze_color_pairs(dominant_colors)

    total_pairs = len(color_pairs)
    aa_pass = sum(1 for p in color_pairs if p['metrics']['aa_normal'])
    aaa_pass = sum(1 for p in color_pairs if p['metrics']['aaa_normal'])
    apca_pass = sum(1 for p in color_pairs if p['metrics']['apca_pass_normal'])
    ui_component_pass = sum(1 for p in color_pairs if p['metrics']['ui_component'])

    return {
        'dominant_colors': dominant_colors,
        'color_pairs': color_pairs,
        'statistics': {
            'total_pairs': total_pairs,
            'aa_pass': aa_pass,
            'aaa_pass': aaa_pass,
            'aa_pass_rate': aa_pass / total_pairs if total_pairs > 0 else 0,
            'aaa_pass_rate': aaa_pass / total_pairs if total_pairs > 0 else 0,
            
            # 新增统计维度
            'apca_pass_rate': apca_pass / total_pairs if total_pairs > 0 else 0,
            'ui_component_pass_rate': ui_component_pass / total_pairs if total_pairs > 0 else 0
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
    print(f"WCAG AA compliance: {result['statistics']['aa_pass_rate']:.1%}")
    print(f"APCA compliance (Lc >= 60): {result['statistics']['apca_pass_rate']:.1%}")
    
    print("\nTop 3 most problematic color pairs:")
    for i, pair in enumerate(result['color_pairs'][:3], 1):
        print(f"  {i}. {pair['color1']['hex']} ↔ {pair['color2']['hex']}")
        print(f"     - WCAG Ratio: {pair['metrics']['ratio']:.2f}:1")
        print(f"     - APCA Lc: {pair['metrics']['apca_lc']:.1f}")
        
        if pair['suggestion']:
            print(f"     💡 HSL Auto-Fix: Change fg to {pair['suggestion']['hex']}")
        if pair['safe_palette_suggestion']:
            print(f"     🎨 Okabe-Ito Safe Color: Use {pair['safe_palette_suggestion']['name']} ({pair['safe_palette_suggestion']['hex']})")