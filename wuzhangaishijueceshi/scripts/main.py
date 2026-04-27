#!/usr/bin/env python3
"""
Main orchestrator for wuzhangaishijueceshi (无障碍色彩测试) skill.

This script coordinates the analysis of web pages and images for accessibility
color issues, including similar color region detection, WCAG compliance checking,
and colorblind friendliness evaluation.
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
from html_report_generator import generate_html_report


def is_url(input_string):
    """Check if the input string is a URL."""
    return input_string.startswith(('http://', 'https://'))


def analyze_component_level(analysis_data, component_region=None):
    """
    Analyze a specific component/region of the image.

    Args:
        analysis_data: Dictionary containing analysis results
        component_region: Optional region coordinates (x, y, width, height)

    Returns:
        Dictionary with component-level analysis
    """
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

    parser.add_argument(
        'input',
        help='URL, image file path, or component identifier'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output HTML report path (default: accessibility_report_YYYYMMDD_HHMMSS.html)'
    )

    parser.add_argument(
        '-c', '--component',
        action='store_true',
        help='Enable component-level testing'
    )

    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=5.0,
        help='Color similarity threshold (Delta E, default: 5.0)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

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

    # Analyze input based on type
    if args.verbose:
        print(f"Analyzing: {args.input}")

    try:
        if is_url(args.input):
            if args.verbose:
                print("  → Detected URL, capturing screenshot...")
            analysis_data = analyze_web_page(args.input)
        else:
            if args.verbose:
                print("  → Detected image file, analyzing colors...")
            analysis_data = analyze_image_file(args.input)

        # Add metadata
        analysis_data['input_source'] = args.input
        analysis_data['analysis_date'] = datetime.now().isoformat()
        analysis_data['threshold'] = args.threshold

        # Component-level analysis if requested
        if args.component:
            if args.verbose:
                print("  → Performing component-level analysis...")
            analysis_data = analyze_component_level(analysis_data)

        # Generate HTML report
        if args.verbose:
            print(f"  → Generating HTML report: {output_path}")

        generate_html_report(analysis_data, output_path, threshold=args.threshold)

        if args.verbose:
            print(f"\n✓ Analysis complete!")
            print(f"  Report saved to: {output_path}")

        print(f"\nAccessibility report generated: {output_path}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
