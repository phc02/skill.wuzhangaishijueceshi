#!/usr/bin/env python3
"""
Main orchestrator for wuzhangaishijueceshi (无障碍色彩测试) skill.

This script coordinates the analysis of web pages and images for accessibility
color issues, and outputs both an HTML dashboard and a terminal summary for LLMs.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_analyzer import analyze_image_file
from web_analyzer import analyze_web_page
from html_report_generator import generate_html_report, calculate_overall_score


def is_url(input_string):
    """Check if the input string is a URL."""
    return input_string.startswith(('http://', 'https://'))


def analyze_component_level(analysis_data, component_region=None):
    if component_region:
        analysis_data['component_region'] = component_region
        analysis_data['analysis_type'] = 'component'
    else:
        analysis_data['analysis_type'] = 'full'
    return analysis_data


def main():
    """Main entry point for wuzhangaishijueceshi skill."""
    parser = argparse.ArgumentParser(
        description='Analysis of web pages/images for accessibility color issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://example.com
  %(prog)s /path/to/design.png
  %(prog)s /path/to/button.png --component
  %(prog)s /path/to/image.png -o my_report.html -t 3.0
        '''
    )

    parser.add_argument('input', help='URL, image file path, or component identifier')
    parser.add_argument('-o', '--output', help='Output HTML report path')
    parser.add_argument('-c', '--component', action='store_true', help='Enable component-level testing')
    parser.add_argument('-t', '--threshold', type=float, default=5.0, help='Color similarity threshold (Delta E, default: 5.0)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input) and not is_url(args.input):
        print(f"Error: Input '{args.input}' is not a valid file or URL")
        sys.exit(1)

    # Generate timestamp for default output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_dir = Path('reports')
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f'accessibility_report_{timestamp}.html')

    try:
        if is_url(args.input):
            analysis_data = analyze_web_page(args.input)
        else:
            analysis_data = analyze_image_file(args.input)

        # =========================================================
        # 修复：直接从内存中读取原图对象，防止网页截图临时文件被删除后报错
        # =========================================================
        try:
            from html_report_generator import image_to_base64
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = None 
            
            # 直接获取之前分析产生的 PIL Image 对象
            img = analysis_data.get('original_image')
            if img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                analysis_data['original_image_base64'] = image_to_base64(img)
        except Exception as e:
            print(f"  [Warning] 无法加载原图用于报告展示: {e}")

        # =========================================================
        # 100x100 像素网格微观盲区排查 (Grid Micro-Analysis) 修复长图限制
        # =========================================================
        try:
            from color_analysis import extract_dominant_colors, check_comprehensive_compliance
            from html_report_generator import image_to_base64
            from PIL import Image
            
            Image.MAX_IMAGE_PIXELS = None 
            
            img = analysis_data.get('original_image')
            if img:
                img = img.convert('RGB')
                w, h = img.size
                
                # 长网页防爆优化：如果图片非常长，我们只扫描网页首屏到中部的黄金区域 (最高 4000px)，防止崩溃
                max_scan_height = min(h, 4000)
                
                # 根据屏幕宽度动态调整块大小，保证横向数量不要太多导致OOM
                block_size = max(100, int(w / 15)) 
                grid_issues = []
                
                for y in range(0, max_scan_height, block_size):
                    for x in range(0, w, block_size):
                        box = (x, y, min(x+block_size, w), min(y+block_size, h))
                        if box[2] - box[0] < 50 or box[3] - box[1] < 50: 
                            continue 
                        
                        crop_img = img.crop(box)
                        dom_colors = extract_dominant_colors(crop_img, num_colors=2)
                        
                        if len(dom_colors) >= 2 and dom_colors[1]['frequency'] > 0.10:
                            c1, c2 = dom_colors[0], dom_colors[1]
                            metrics = check_comprehensive_compliance(c1['rgb'], c2['rgb'])
                            
                            if metrics['ratio'] < 3.0:
                                grid_issues.append({
                                    'coord': f"X:{box[0]}-{box[2]}, Y:{box[1]}-{box[3]}",
                                    'image_base64': image_to_base64(crop_img, format='JPEG'),
                                    'c1': c1['hex'],
                                    'c2': c2['hex'],
                                    'ratio': metrics['ratio']
                                })
                                
                analysis_data['grid_issues'] = grid_issues
        except Exception as e:
            print(f"  [Warning] 网格分析失败: {e}")

        # 多通道传达启发式规则
        requires_multimodal = False
        if 'color_analysis' in analysis_data:
            dominant_colors = analysis_data['color_analysis'].get('dominant_colors', [])
            has_red = any(c['rgb'][0] > 180 and c['rgb'][1] < 100 and c['rgb'][2] < 100 for c in dominant_colors)
            has_green = any(c['rgb'][1] > 150 and c['rgb'][0] < 120 for c in dominant_colors)
            if has_red and has_green:
                requires_multimodal = True
        
        analysis_data['requires_multimodal_check'] = requires_multimodal

        # Add metadata
        analysis_data['input_source'] = args.input
        analysis_data['analysis_date'] = datetime.now().isoformat()
        analysis_data['threshold'] = args.threshold

        if args.component:
            analysis_data = analyze_component_level(analysis_data)

        # Generate HTML report
        generate_html_report(analysis_data, output_path, threshold=args.threshold)

        # 终端数据摘要
        overall_score = calculate_overall_score(analysis_data)
        
        print("\n=== SYSTEM_SUMMARY_FOR_LLM ===")
        print(f"STATUS: SUCCESS")
        print(f"REPORT_PATH: {output_path}")
        print(f"OVERALL_SCORE: {overall_score}/100")
        print(f"REQUIRES_MULTIMODAL_CHECK: {requires_multimodal}")
        
        if 'color_analysis' in analysis_data:
            stats = analysis_data['color_analysis'].get('statistics', {})
            print(f"AA_COMPLIANCE_RATE: {stats.get('aa_pass_rate', 0):.1%}")
            print(f"APCA_COMPLIANCE_RATE: {stats.get('apca_pass_rate', 0):.1%}")
            print(f"UI_COMPONENT_PASS_RATE: {stats.get('ui_component_pass_rate', 0):.1%}")
            
            pairs = analysis_data['color_analysis'].get('color_pairs', [])
            failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
            print(f"CONTRAST_ISSUES_FOUND: {len(failed_pairs)}")
            
            if failed_pairs:
                top_issue = failed_pairs[0]
                color1 = top_issue['color1']['hex']
                color2 = top_issue['color2']['hex']
                ratio = top_issue['metrics']['ratio']
                apca_lc = top_issue['metrics']['apca_lc']
                
                print(f"TOP_ISSUE: Hex {color1} on {color2} (Ratio {ratio:.2f}:1, APCA Lc {apca_lc:.1f})")
                
                if top_issue.get('suggestion'):
                    print(f"AUTO_FIX_SUGGESTED: {top_issue['suggestion']['hex']}")
                if top_issue.get('safe_palette_suggestion'):
                    safe_color = top_issue['safe_palette_suggestion']
                    print(f"SAFE_PALETTE_SUGGESTED: {safe_color['name']} ({safe_color['hex']})")
                    
        print("==============================\n")
        print(f"✨ 无障碍分析完成！评分: {overall_score}/100")
        print(f"📄 详细 Dashboard 报告已生成: {output_path}")

    except Exception as e:
        print(f"\n=== SYSTEM_SUMMARY_FOR_LLM ===")
        print(f"STATUS: ERROR")
        print(f"ERROR_MSG: {str(e)}")
        print("==============================\n")
        print(f"执行出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()