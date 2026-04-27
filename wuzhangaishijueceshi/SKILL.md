---
name: wuzhangaishijueceshi
description: Analyze web pages and design images for accessibility color issues with focus on similar color region detection. Use when users want WCAG compliance checking, colorblind friendliness evaluation, color contrast analysis, or similar color region detection. Generates interactive, self-contained HTML reports with developer-focused recommendations.
---

# 无障碍色彩测试 (Wuzhangaishijueceshi)

A comprehensive accessibility analysis skill that evaluates web pages and design images for color-related accessibility issues, with a unique focus on detecting similar color regions that may cause problems for users with color vision deficiencies.

## Overview

This skill helps developers and designers ensure their web pages and design mockups are accessible to all users, including those with color vision deficiencies. It provides deep analysis of color usage, contrast ratios, and colorblind friendliness, with a special emphasis on identifying areas where similar colors may cause confusion.

### Key Features

1. **Similar Color Region Detection** - Identifies areas with perceptually similar colors that may cause accessibility issues
2. **WCAG Compliance Checking** - Validates against WCAG 2.1/2.2 AA and AAA standards
3. **Colorblind Friendliness Evaluation** - Simulates how designs appear to users with various color vision deficiencies
4. **Interactive HTML Reports** - Self-contained, elegant reports with embedded interactivity
5. **Developer-Focused Recommendations** - Actionable suggestions with code snippets

### Target Users

- Web Developers
- UI/UX Designers
- Accessibility Specialists
- Product Managers
- Frontend Engineers

## Input Methods

### 1. Web Page URLs
Analyze live websites by providing a URL:
```
Analyze the accessibility of https://example.com
```

### 2. Image Files
Analyze design mockups or screenshots:
```
Analyze this design mockup for accessibility issues
[attach design.png]
```

### 3. Component-Level Testing
Analyze specific UI components:
```
Check if this button has sufficient color contrast
[attach button.png]
```

## Output Format

The skill generates a **self-contained, interactive HTML report** with the following sections:

### Report Sections

1. **执行摘要 (Executive Summary)**
   - Overall accessibility score (0-100)
   - Compliance breakdown (AA/AAA)
   - Critical issues count
   - Key findings summary

2. **色彩对比度分析 (Color Contrast Analysis)**
   - Interactive table with sorting and filtering
   - Visual color swatches
   - WCAG compliance indicators
   - Contrast ratio charts

3. **相近区域颜色分析 (Similar Color Region Analysis)** ⭐ NEW
   - Interactive image viewer with region highlighting
   - Color similarity heatmap
   - List of problematic regions with coordinates
   - Adjustable sensitivity threshold

4. **色盲友好性评估 (Colorblind Friendliness Evaluation)**
   - Simulation gallery for Protanopia, Deuteranopia, Tritanopia
   - Side-by-side comparisons
   - Impact assessment per CVD type

5. **开发者建议 (Developer Recommendations)**
   - Prioritized list by severity
   - Code snippets for implementation
   - Effort/impact analysis

## Usage Examples

### Example 1: Analyze Web Page URL
**Input:**
```
Check the accessibility of https://example.com for colorblind users
```

**Output:**
- Interactive HTML report with:
  - Color contrast analysis
  - Similar region detection
  - CVD simulation gallery
  - Developer recommendations

### Example 2: Analyze Design Mockup
**Input:**
```
Analyze this design mockup for accessibility issues
[attach design.png]
```

**Output:**
- HTML report with detailed analysis of:
  - Color contrast ratios
  - Similar color regions
  - Colorblind simulation
  - Specific improvement suggestions

### Example 3: Component-Level Testing
**Input:**
```
Check if this button component has sufficient color contrast
[attach button.png]
```

**Output:**
- Focused analysis of the component
- Specific contrast measurements
- WCAG compliance status
- Code snippets for fixes

## Technical Approach

### Color Analysis Pipeline

1. **Input Processing**
   - URL → Selenium screenshot capture
   - Image file → Direct loading with PIL
   - Component → Specific region extraction

2. **Color Extraction**
   - Resize image for performance (max 2000px)
   - Apply K-means clustering (k=10-20 colors)
   - Calculate color frequencies
   - Convert to Lab color space for perceptual uniformity

3. **Contrast Analysis**
   - Extract all color pairs from dominant colors
   - Calculate WCAG contrast ratios using relative luminance formula
   - Check AA (4.5:1) and AAA (7:1) compliance
   - Generate compliance report

4. **Similar Region Detection** ⭐ NEW
   - Convert to Lab color space
   - Apply SLIC superpixel segmentation
   - Calculate Delta E between adjacent regions using CIEDE2000
   - Flag regions with ΔE < 5 (moderate threshold)
   - Generate visual heatmap

5. **Colorblind Simulation**
   - Apply Machado matrices for each CVD type
   - Generate simulation images
   - Calculate post-simulation contrast ratios
   - Assess impact on accessibility

6. **Report Generation**
   - Compile all analysis data
   - Generate self-contained HTML with embedded JS/CSS
   - Include interactive elements (charts, viewers, tables)
   - Style with modern, elegant CSS

## WCAG 2.1/2.2 Compliance

### Relevant Success Criteria

**1.4.1 Use of Color (Level A)**
- Color is not the only means of conveying information
- Alternative indicators (icons, patterns, text) required

**1.4.3 Contrast (Minimum) (Level AA)**
- Normal text: minimum 4.5:1 contrast ratio
- Large text (18pt+): minimum 3:1 contrast ratio

**1.4.11 Non-text Contrast (Level AA)**
- UI components: minimum 3:1 contrast ratio
- Graphical objects: minimum 3:1 contrast ratio

**1.4.6 Contrast (Enhanced) (Level AAA)**
- Normal text: minimum 7:1 contrast ratio
- Large text: minimum 4.5:1 contrast ratio

## Triggering Contexts

This skill should trigger when users mention:
- "accessibility color test" / "无障碍色彩测试"
- "color contrast analysis" / "色彩对比度分析"
- "WCAG compliance check" / "WCAG合规性检查"
- "colorblind friendliness" / "色盲友好性"
- "similar color regions" / "相近区域颜色"
- "analyze this design" / "analyze this page"
- "check accessibility" / "检查无障碍性"

## Technical Requirements

### Required Environment
- **Python 3.8+** - For image processing and analysis
- **Pillow** - Image loading and processing
- **scikit-image** - Superpixel segmentation
- **colour-science** - Color space conversions
- **selenium** - Web page screenshot capture

### Installation Instructions
```bash
# Install Python from https://www.python.org/downloads/
# Ensure "Add Python to PATH" is checked during installation

# Install required libraries
python -m pip install -r requirements.txt
```

## File Structure

```
wuzhangaishijueceshi/
├── SKILL.md                    # Skill definition
├── README.md                   # Comprehensive documentation
├── scripts/
│   ├── __init__.py             # Package marker
│   ├── main.py                 # Main orchestrator
│   ├── image_analyzer.py       # Image color extraction
│   ├── color_analysis.py       # Contrast calculations
│   ├── colorblind_simulator.py # CVD simulation
│   ├── similar_region_detector.py  # NEW: Similar region detection
│   ├── html_report_generator.py    # Interactive HTML reports
│   └── web_analyzer.py         # Web page analysis
├── templates/
│   └── report_template.html    # HTML report template
├── resources/
│   ├── wcag-guidelines.md      # WCAG reference
│   └── colorblind-info.md      # CVD reference
├── examples/
│   └── usage-examples.md       # Usage examples
├── reports/                    # Generated reports
└── requirements.txt            # Python dependencies
```

## Notes

- This skill focuses on visual accessibility for color vision deficiencies
- Reports are based on WCAG 2.1/2.2 international standards
- Similar color region detection uses CIEDE2000 for perceptual accuracy
- All analysis is backed by accessibility standards and research
- Reports are self-contained and work offline
- Recommendations prioritize practical, implementable changes
