"""
wuzhangaishijueceshi - 无障碍色彩测试 (Accessibility Color Testing)

A comprehensive accessibility analysis skill for web pages and design images.
"""

__version__ = '1.0.0'
__author__ = 'Wuzhangaishijueceshi Team'

from .image_analyzer import analyze_image_file
from .web_analyzer import analyze_web_page
from .color_analysis import analyze_image_colors
from .similar_region_detector import analyze_similar_colors
from .colorblind_simulator import simulate_all_cvd_types
from .html_report_generator import generate_html_report

__all__ = [
    'analyze_image_file',
    'analyze_web_page',
    'analyze_image_colors',
    'analyze_similar_colors',
    'simulate_all_cvd_types',
    'generate_html_report',
]
