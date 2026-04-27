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

        # Add metadata
        analysis_data['input_source'] = args.input
        analysis_data['analysis_date'] = datetime.now().isoformat()
        analysis_data['threshold'] = args.threshold

        if args.component:
            analysis_data = analyze_component_level(analysis_data)

        # Generate HTML report
        generate_html_report(analysis_data, output_path, threshold=args.threshold)

        # ---------------------------------------------------------
        # 新增：专为 Claude LLM 准备的终端数据摘要 (LLM Readout)
        # ---------------------------------------------------------
        overall_score = calculate_overall_score(analysis_data)
        
        print("\n=== SYSTEM_SUMMARY_FOR_LLM ===")
        print(f"STATUS: SUCCESS")
        print(f"REPORT_PATH: {output_path}")
        print(f"OVERALL_SCORE: {overall_score}/100")
        
        if 'color_analysis' in analysis_data:
            stats = analysis_data['color_analysis'].get('statistics', {})
            print(f"AA_COMPLIANCE_RATE: {stats.get('aa_pass_rate', 0):.1%}")
            
            pairs = analysis_data['color_analysis'].get('color_pairs', [])
            failed_pairs = [p for p in pairs if p.get('suggestion')]
            print(f"CONTRAST_ISSUES_FOUND: {len(failed_pairs)}")
            if failed_pairs:
                print(f"TOP_ISSUE: Hex {failed_pairs[0]['color1']['hex']} on {failed_pairs[0]['color2']['hex']} (Ratio {failed_pairs[0]['contrast_ratio']:.2f}:1)")
                print(f"AUTO_FIX_SUGGESTED: {failed_pairs[0]['suggestion']['hex']}")
                
        print("==============================\n")
        
        # 面向用户的常规输出
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