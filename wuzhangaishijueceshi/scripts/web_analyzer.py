#!/usr/bin/env python3
"""
Web Analyzer Module for wuzhangaishijueceshi skill.

This module handles web page screenshot capture and analysis.
"""

import os
import time
import tempfile
from io import BytesIO
from PIL import Image
import numpy as np

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def capture_screenshot(url, output_path=None, timeout=30):
    """
    Capture a screenshot of a web page using Selenium.

    Args:
        url: URL of the web page
        output_path: Optional path to save screenshot
        timeout: Maximum time to wait for page load

    Returns:
        PIL Image object
    """
    if not SELENIUM_AVAILABLE:
        raise ImportError(
            "Selenium is not installed. Install with: pip install selenium"
        )

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-gpu')

    driver = None
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)

        # Load page
        driver.get(url)

        # Wait for page to load
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Additional wait for dynamic content
        time.sleep(2)

        # Get page dimensions
        total_height = driver.execute_script("return document.body.scrollHeight")
        total_width = driver.execute_script("return document.body.scrollWidth")

        # Set window size to capture full page
        driver.set_window_size(total_width, total_height)

        # Take screenshot
        screenshot = driver.get_screenshot_as_png()

        # Convert to PIL Image
        image = Image.open(BytesIO(screenshot))

        # Save if output path provided
        if output_path:
            image.save(output_path)

        return image

    except Exception as e:
        raise ValueError(f"Error capturing screenshot of '{url}': {e}")

    finally:
        if driver:
            driver.quit()


def analyze_web_page(url):
    """
    Complete analysis of a web page.

    Args:
        url: URL of the web page

    Returns:
        dict: Complete analysis results
    """
    # Import analysis modules
    from image_analyzer import load_image
    from color_analysis import analyze_image_colors
    from similar_region_detector import analyze_similar_colors, generate_similarity_heatmap
    from colorblind_simulator import simulate_all_cvd_types, create_comparison_grid
    from html_report_generator import image_to_base64
    from io import BytesIO

    # Create temporary file for screenshot
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        screenshot_path = tmp_file.name

    try:
        # Capture screenshot
        image = capture_screenshot(url, screenshot_path)

        # Analyze using image analyzer logic
        image_array = np.array(image)

        # Analyze colors
        color_analysis = analyze_image_colors(screenshot_path)

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
            'input_source': url,
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

    finally:
        # Clean up temporary file
        if os.path.exists(screenshot_path):
            os.unlink(screenshot_path)


if __name__ == '__main__':
    # Example usage
    import sys
    import numpy as np
    from io import BytesIO

    if len(sys.argv) < 2:
        print("Usage: python web_analyzer.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        result = analyze_web_page(url)
        print(f"Analysis complete!")
        print(f"URL: {result['input_source']}")
        print(f"Screenshot size: {result['image_info']['size']}")
        print(f"Dominant colors: {len(result['color_analysis']['dominant_colors'])}")
        print(f"Similar regions: {result['similar_regions']['total_issues']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
