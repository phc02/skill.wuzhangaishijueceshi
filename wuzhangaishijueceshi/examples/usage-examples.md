# Usage Examples for 无障碍色彩测试 (Wuzhangaishijueceshi)

## Basic Usage

### Example 1: Analyze an Image File

```bash
python scripts/main.py /path/to/design.png
```

**What happens:**
1. Loads the image file
2. Extracts dominant colors using K-means clustering
3. Calculates WCAG contrast ratios for all color pairs
4. Detects similar color regions using CIEDE2000 metric
5. Simulates colorblind views (Protanopia, Deuteranopia, Tritanopia)
6. Generates interactive HTML report

**Output:** `reports/accessibility_report_YYYYMMDD_HHMMSS.html`

### Example 2: Analyze a Web Page URL

```bash
python scripts/main.py https://example.com
```

**What happens:**
1. Captures screenshot of the web page using Selenium
2. Performs all image analysis steps
3. Generates comprehensive accessibility report

**Note:** Requires Selenium and Chrome/ChromeDriver to be installed.

### Example 3: Custom Output Path

```bash
python scripts/main.py /path/to/image.png -o my-accessibility-report.html
```

**Output:** `my-accessibility-report.html` in the current directory

## Advanced Usage

### Component-Level Testing

```bash
python scripts/main.py /path/to/button.png --component
```

**Use case:** Analyze a specific UI component in isolation

### Adjust Similarity Threshold

```bash
# Stricter detection (Delta E < 3)
python scripts/main.py /path/to/image.png -t 3.0

# More lenient detection (Delta E < 7)
python scripts/main.py /path/to/image.png -t 7.0
```

**Default:** 5.0 (moderate threshold)

### Verbose Output

```bash
python scripts/main.py /path/to/image.png -v
```

Shows detailed progress information during analysis.

## Batch Processing

### Process Multiple Images

```bash
# Using a for loop
for file in ./designs/*.png; do
    python scripts/main.py "$file" -o "reports/$(basename "$file" .png)_report.html"
done
```

### Process All Images in Directory

```bash
# Using find command
find ./screenshots -name "*.png" -exec python scripts/main.py {} -o reports/{}.html \;
```

## Integration Examples

### Python Script Integration

```python
import sys
sys.path.insert(0, '/path/to/wuzhangaishijueceshi/scripts')

from main import analyze_image_file
from html_report_generator import generate_html_report

# Analyze image
analysis_data = analyze_image_file('/path/to/design.png')

# Generate report
generate_html_report(analysis_data, 'my_report.html')
```

### Web Application Integration

```python
from flask import Flask, request, send_file
from scripts.main import analyze_image_file
from scripts.html_report_generator import generate_html_report
import tempfile

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get uploaded image
    image_file = request.files['image']
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image_file.save(tmp.name)
        
        # Analyze
        analysis_data = analyze_image_file(tmp.name)
        
        # Generate report
        report_path = '/tmp/accessibility_report.html'
        generate_html_report(analysis_data, report_path)
        
        return send_file(report_path, as_attachment=True)
```

## Common Workflows

### Workflow 1: Design Review Process

```bash
# 1. Analyze initial design
python scripts/main.py design-v1.png -o design-v1-report.html

# 2. Review report and make changes
# 3. Analyze updated design
python scripts/main.py design-v2.png -o design-v2-report.html

# 4. Compare reports to verify improvements
```

### Workflow 2: Pre-Launch Accessibility Check

```bash
# Check all page templates
for page in home about contact products; do
    python scripts/main.py screenshots/${page}.png \
        -o reports/${page}_accessibility.html
done

# Generate summary
echo "Accessibility reports generated in reports/"
```

### Workflow 3: Component Library Audit

```bash
# Analyze each component in library
for component in button input select modal; do
    python scripts/main.py components/${component}.png \
        -o reports/${component}_accessibility.html \
        --component
done
```

## Troubleshooting

### Issue: "Selenium not found"

**Solution:** Install Selenium and ChromeDriver
```bash
pip install selenium
# Download ChromeDriver from https://chromedriver.chromium.org/
```

### Issue: "Image file not found"

**Solution:** Check file path and permissions
```bash
ls -la /path/to/image.png  # Verify file exists
```

### Issue: Report not generating

**Solution:** Check output directory permissions
```bash
mkdir -p reports  # Create reports directory if it doesn't exist
```

## Tips

1. **Start with high-contrast designs** - Easier to achieve WCAG compliance
2. **Test early and often** - Catch issues before development
3. **Use the similarity threshold** - Adjust based on your design needs
4. **Review all sections** - Each section provides different insights
5. **Share reports with team** - HTML reports are easy to distribute

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [Color Blindness Simulation](http://www.color-blindness.com/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
