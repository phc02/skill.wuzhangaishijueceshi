#!/usr/bin/env python3
"""
Similar Color Region Detector for wuzhangaishijueceshi skill.

UPGRADED: Includes "CVD Boundary Melt Detection". It detects regions that 
look distinct to normal vision but melt together for colorblind users.
Uses CIEDE2000 color difference metric for perceptually accurate color comparison.
"""

import numpy as np
from PIL import Image
from skimage import segmentation
from skimage.color import rgb2lab
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000

# Patch for NumPy 2.x compatibility with colormath
if not hasattr(np, 'asscalar'):
    np.asscalar = lambda a: a.item()

# ==========================================
# Machado 色觉障碍 (CVD) 仿真矩阵
# ==========================================
CVD_MATRICES = {
    'Protanopia (红色盲)': [[0.567, 0.433, 0.000], [0.558, 0.442, 0.000], [0.000, 0.242, 0.758]],
    'Deuteranopia (绿色盲)': [[0.625, 0.375, 0.000], [0.700, 0.300, 0.000], [0.000, 0.300, 0.700]],
    'Tritanopia (蓝色盲)': [[0.950, 0.050, 0.000], [0.000, 0.433, 0.567], [0.000, 0.475, 0.525]]
}

def rgb_to_lab(rgb_array):
    """Convert RGB image array to Lab color space."""
    rgb_normalized = rgb_array.astype(np.float32) / 255.0
    return rgb2lab(rgb_normalized)

def calculate_region_colors(lab_image, rgb_image, segments, region_id):
    """
    同时计算该区域的 Lab 平均值和 RGB 平均值，
    RGB 值将用于后续的色盲仿真矩阵运算。
    """
    mask = segments == region_id
    if not np.any(mask):
        return None, None

    # 获取 Lab 平均值
    lab_pixels = lab_image[mask]
    avg_l = np.mean(lab_pixels[:, 0])
    avg_a = np.mean(lab_pixels[:, 1])
    avg_b = np.mean(lab_pixels[:, 2])

    # 获取 RGB 平均值
    rgb_pixels = rgb_image[mask]
    avg_r = np.mean(rgb_pixels[:, 0])
    avg_g = np.mean(rgb_pixels[:, 1])
    avg_b = np.mean(rgb_pixels[:, 2])

    return (avg_l, avg_a, avg_b), (avg_r, avg_g, avg_b)

def get_adjacent_regions(segments, region_id):
    """Get IDs of regions adjacent to the specified region."""
    mask = segments == region_id
    if not np.any(mask):
        return set()

    from scipy import ndimage
    boundary = ndimage.binary_dilation(mask) & ~mask
    adjacent_ids = set(np.unique(segments[boundary]))
    adjacent_ids.discard(region_id)
    return adjacent_ids

def ciede2000(color1, color2):
    """Calculate CIEDE2000 color difference between two Lab colors."""
    lab1 = LabColor(color1[0], color1[1], color1[2])
    lab2 = LabColor(color2[0], color2[1], color2[2])
    result = delta_e_cie2000(lab1, lab2)

    if hasattr(result, 'item'): return result.item()
    elif hasattr(result, 'asscalar'): return result.asscalar()
    else: return float(result)

def simulate_cvd_lab(rgb_tuple, matrix):
    """将普通 RGB 颜色应用色盲矩阵后，转为 Lab 色彩空间供 ΔE 计算。"""
    r, g, b = rgb_tuple
    sim_r = min(255, max(0, matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b))
    sim_g = min(255, max(0, matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b))
    sim_b = min(255, max(0, matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b))
    
    # 构造单像素图像以复用 skimage 的 rgb2lab
    sim_array = np.array([[[sim_r, sim_g, sim_b]]], dtype=np.uint8)
    sim_lab = rgb_to_lab(sim_array)[0, 0]
    return (sim_lab[0], sim_lab[1], sim_lab[2])


def analyze_similar_colors(image, threshold=5.0, n_segments=100):
    """
    Analyze similar color regions and perform CVD Boundary Melt Detection.
    """
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    if image_array.shape[2] == 4:
        image_array = image_array[:, :, :3]

    lab_image = rgb_to_lab(image_array)

    segments = segmentation.slic(
        image_array,
        n_segments=n_segments,
        compactness=10,
        start_label=1
    )

    region_lab_colors = {}
    region_rgb_colors = {}
    for region_id in np.unique(segments):
        lab_c, rgb_c = calculate_region_colors(lab_image, image_array, segments, region_id)
        if lab_c:
            region_lab_colors[region_id] = lab_c
            region_rgb_colors[region_id] = rgb_c

    similar_regions = []
    checked_pairs = set()

    for region_id in region_lab_colors.keys():
        neighbors = get_adjacent_regions(segments, region_id)

        for neighbor_id in neighbors:
            pair = tuple(sorted([region_id, neighbor_id]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            if neighbor_id in region_lab_colors:
                lab1, lab2 = region_lab_colors[region_id], region_lab_colors[neighbor_id]
                rgb1, rgb2 = region_rgb_colors[region_id], region_rgb_colors[neighbor_id]

                # 1. 计算正常视力下的色差
                normal_delta_e = ciede2000(lab1, lab2)
                
                melt_risks = []
                worst_cvd_delta_e = normal_delta_e

                # 2. 核心绝杀：遍历 3 种色觉障碍，进行边缘消融检测
                for cvd_name, matrix in CVD_MATRICES.items():
                    cvd_lab1 = simulate_cvd_lab(rgb1, matrix)
                    cvd_lab2 = simulate_cvd_lab(rgb2, matrix)
                    cvd_delta_e = ciede2000(cvd_lab1, cvd_lab2)
                    
                    # 记录最差的情况
                    if cvd_delta_e < worst_cvd_delta_e:
                        worst_cvd_delta_e = cvd_delta_e
                        
                    # 边缘消融判定规则：正常人看边界清晰 (ΔE >= 3)，但色盲看着模糊 (ΔE < 3)
                    # 或者本身对正常人就模糊，但色盲看着更灾难 (ΔE < 2.0)
                    if cvd_delta_e < 3.0 and (normal_delta_e >= 3.0 or cvd_delta_e < normal_delta_e - 1.0):
                        melt_risks.append(cvd_name)

                # 3. 拦截问题：正常视觉色差小，或者触发了色盲边缘消融
                if normal_delta_e < threshold or melt_risks:
                    similar_regions.append({
                        'region1': int(region_id),
                        'region2': int(neighbor_id),
                        'delta_e': float(normal_delta_e),
                        'worst_cvd_delta_e': float(worst_cvd_delta_e),
                        'melt_risks': melt_risks,
                        'color1': lab1,
                        'color2': lab2
                    })

    # 根据最严重的边缘消融（或正常色差）进行排序
    similar_regions.sort(key=lambda x: min(x['delta_e'], x['worst_cvd_delta_e']))

    return {
        'similar_regions': similar_regions,
        'threshold': threshold,
        'total_issues': len(similar_regions),
        'segments': segments,
        'region_colors': {int(k): v for k, v in region_lab_colors.items()}
    }

def generate_similarity_heatmap(image, analysis_result):
    if isinstance(image, Image.Image):
        image_array = np.array(image)
    else:
        image_array = image

    heatmap = np.zeros(image_array.shape[:2], dtype=np.float32)
    segments = analysis_result['segments']

    for issue in analysis_result['similar_regions']:
        region1_mask = segments == issue['region1']
        region2_mask = segments == issue['region2']

        # 使用最差的 Delta E (可能是色盲视图下的) 来渲染热力图严重程度
        effective_delta = min(issue['delta_e'], issue['worst_cvd_delta_e'])
        intensity = max(0, 1 - (effective_delta / analysis_result['threshold']))
        
        heatmap[region1_mask] = np.maximum(heatmap[region1_mask], intensity)
        heatmap[region2_mask] = np.maximum(heatmap[region2_mask], intensity)

    if heatmap.max() > 0:
        heatmap = (heatmap / heatmap.max() * 255).astype(np.uint8)
    else:
        heatmap = np.zeros_like(heatmap, dtype=np.uint8)

    return heatmap

def get_region_boundaries(segments, region_id):
    mask = segments == region_id
    if not np.any(mask): return None

    rows, cols = np.where(mask)
    bbox = {
        'y_min': int(rows.min()), 'y_max': int(rows.max()),
        'x_min': int(cols.min()), 'x_max': int(cols.max())
    }
    bbox['center_x'] = (bbox['x_min'] + bbox['x_max']) // 2
    bbox['center_y'] = (bbox['y_min'] + bbox['y_max']) // 2
    bbox['area'] = int(np.sum(mask))

    return bbox

def analyze_image_for_similar_colors(image_path, threshold=5.0):
    image = Image.open(image_path)
    analysis_result = analyze_similar_colors(image, threshold=threshold)

    for issue in analysis_result['similar_regions']:
        for region_key in ['region1', 'region2']:
            region_id = issue[region_key]
            boundaries = get_region_boundaries(analysis_result['segments'], region_id)
            if boundaries:
                issue[f'{region_key}_boundaries'] = boundaries

    analysis_result['heatmap'] = generate_similarity_heatmap(image, analysis_result)
    return analysis_result

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python similar_region_detector.py <image_path> [threshold]")
        sys.exit(1)

    image_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    result = analyze_image_for_similar_colors(image_path, threshold)

    print(f"Analysis complete! Total issues found: {result['total_issues']}")
    if result['similar_regions']:
        for i, issue in enumerate(result['similar_regions'][:5], 1):
            melt = f" | CVD Melt Risks: {', '.join(issue['melt_risks'])}" if issue['melt_risks'] else ""
            print(f"  {i}. R{issue['region1']} ↔ R{issue['region2']}: Normal ΔE = {issue['delta_e']:.2f}{melt}")