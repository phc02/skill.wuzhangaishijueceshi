# 无障碍色彩测试 (Wuzhangaishijueceshi)

A comprehensive accessibility analysis skill for web pages and design images, with a unique focus on detecting similar color regions that may cause accessibility issues.

## Overview

This skill helps developers and designers ensure their web pages and design mockups are accessible to all users, including those with color vision deficiencies. It provides deep analysis of color usage, contrast ratios, and colorblind friendliness.

### Key Features

1. **Similar Color Region Detection** - Identifies areas with perceptually similar colors using CIEDE2000 metric
2. **WCAG Compliance Checking** - Validates against WCAG 2.1/2.2 AA and AAA standards
3. **Colorblind Friendliness Evaluation** - Simulates how designs appear to users with various CVD types
4. **Interactive HTML Reports** - Self-contained, elegant reports with embedded interactivity
5. **Developer-Focused Recommendations** - Actionable suggestions with code snippets

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd wuzhangaishijueceshi
pip install -r requirements.txt
```

For web page analysis (optional):

```bash
# Install Chrome browser and ChromeDriver
# Or use: pip install selenium webdriver-manager
```

## Usage

### Analyze an Image File

```bash
python scripts/main.py /path/to/design.png
```

### Analyze a Web Page URL

```bash
python scripts/main.py https://example.com
```

### Component-Level Testing

```bash
python scripts/main.py /path/to/button.png --component
```

### Custom Output Path

```bash
python scripts/main.py /path/to/image.png -o my_report.html
```

### Adjust Similarity Threshold

```bash
python scripts/main.py /path/to/image.png -t 3.0  # Stricter (Delta E < 3)
```

## Output

The skill generates a self-contained, interactive HTML report with the following sections:

1. **执行摘要 (Executive Summary)** - Overall accessibility score and key metrics
2. **色彩对比度分析 (Color Contrast Analysis)** - WCAG compliance table with color swatches
3. **相近区域颜色分析 (Similar Color Region Analysis)** - Interactive image viewer with region highlighting
4. **色盲友好性评估 (Colorblind Friendliness Evaluation)** - Simulation gallery for all CVD types
5. **开发者建议 (Developer Recommendations)** - Prioritized fixes with code snippets

## Technical Details

### Color Analysis Pipeline

1. **Input Processing** - Load image or capture web page screenshot
2. **Color Extraction** - K-means clustering for dominant colors
3. **Contrast Analysis** - WCAG relative luminance formula
4. **Similar Region Detection** - SLIC superpixel segmentation + CIEDE2000
5. **Colorblind Simulation** - Machado transformation matrices
6. **Report Generation** - Self-contained HTML with embedded JS/CSS

### WCAG Standards

- **1.4.1 Use of Color (Level A)** - Color not the only means of conveying information
- **1.4.3 Contrast (Minimum) (Level AA)** - Normal text: 4.5:1, Large text: 3:1
- **1.4.11 Non-text Contrast (Level AA)** - UI components: 3:1
- **1.4.6 Contrast (Enhanced) (Level AAA)** - Normal text: 7:1, Large text: 4.5:1

## File Structure

```
wuzhangaishijueceshi/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── scripts/
│   ├── __init__.py             # Package marker
│   ├── main.py                 # Main orchestrator
│   ├── image_analyzer.py       # Image color extraction
│   ├── color_analysis.py       # Contrast calculations
│   ├── colorblind_simulator.py # CVD simulation
│   ├── similar_region_detector.py  # Similar region detection
│   ├── html_report_generator.py    # Interactive HTML reports
│   └── web_analyzer.py         # Web page analysis
├── resources/
│   ├── wcag-guidelines.md      # WCAG reference
│   └── colorblind-info.md      # CVD reference
├── examples/
│   └── usage-examples.md       # Usage examples
├── reports/                    # Generated reports
└── requirements.txt            # Python dependencies
```

## Examples

### Example 1: Analyze Design Mockup

```bash
python scripts/main.py ./examples/design-mockup.png
```

Output: `reports/accessibility_report_20260424_143022.html`

### Example 2: Analyze Web Page

```bash
python scripts/main.py https://example.com -o web_report.html
```

### Example 3: Batch Analysis

```bash
for file in ./screenshots/*.png; do
    python scripts/main.py "$file" -o "reports/$(basename "$file" .png)_report.html"
done
```

## Dependencies

### Required

- Pillow - Image processing
- numpy - Numerical computing
- scikit-learn - Color extraction (K-means)
- scikit-image - Image segmentation
- colour-science - Color space conversions
- colormath - CIEDE2000 color difference
- Jinja2 - HTML generation

### Optional

- selenium - Web page screenshot capture
- requests - URL fetching
- beautifulsoup4 - HTML parsing

## License

This skill is part of the wuzhangaishijueceshi project.

## Contributing

Contributions are welcome! Please ensure all code follows the existing style and includes appropriate tests.

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [CIEDE2000 Color Difference](http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE2000.html)
- [Color Blindness Simulation](http://www.color-blindness.com/)
