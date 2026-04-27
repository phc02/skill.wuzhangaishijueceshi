#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

This module generates self-contained, interactive HTML accessibility reports
with embedded JavaScript and CSS (no CDN dependencies).
"""

import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image


def image_to_base64(image, format='PNG'):
    """
    Convert PIL Image to base64-encoded string.

    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG, etc.)

    Returns:
        str: Base64-encoded image string
    """
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def calculate_overall_score(analysis_data):
    """
    Calculate overall accessibility score (0-100).

    Args:
        analysis_data: Dictionary containing analysis results

    Returns:
        int: Overall accessibility score
    """
    score = 100

    # Deduct for contrast issues
    if 'color_analysis' in analysis_data:
        stats = analysis_data['color_analysis'].get('statistics', {})
        aa_pass_rate = stats.get('aa_pass_rate', 1.0)
        aaa_pass_rate = stats.get('aaa_pass_rate', 1.0)

        # Weighted deduction
        score -= int((1 - aa_pass_rate) * 30)
        score -= int((1 - aaa_pass_rate) * 20)

    # Deduct for similar color regions
    if 'similar_regions' in analysis_data:
        similar = analysis_data['similar_regions']
        if 'total_issues' in similar:
            # Deduct up to 30 points for similar regions
            score -= min(30, similar['total_issues'] * 2)

    # Deduct for CVD issues
    if 'cvd_analysis' in analysis_data:
        cvd_issues = analysis_data['cvd_analysis'].get('total_issues', 0)
        score -= min(20, cvd_issues * 2)

    return max(0, min(100, score))


def generate_html_report(analysis_data, output_path, threshold=5.0):
    """
    Generate a self-contained, interactive HTML accessibility report.

    Args:
        analysis_data: Dictionary containing all analysis results
        output_path: Path to save the HTML report
        threshold: Color similarity threshold used
    """
    # Calculate overall score
    overall_score = calculate_overall_score(analysis_data)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Build HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>无障碍色彩测试报告</title>
    <style>
        /* Modern, elegant styling - self-contained */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}

        .score-card {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin: 20px auto;
            max-width: 400px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .score-value {{
            font-size: 4em;
            font-weight: bold;
            color: #667eea;
            text-align: center;
        }}

        .score-label {{
            text-align: center;
            color: #666;
            margin-top: 10px;
        }}

        .score-bar {{
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            margin-top: 15px;
            overflow: hidden;
        }}

        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
            transition: width 0.5s ease;
        }}

        section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        section h2 {{
            color: #333;
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .summary-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .summary-item .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}

        .summary-item .label {{
            color: #666;
            margin-top: 5px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            cursor: pointer;
        }}

        th:hover {{
            background: #e9ecef;
        }}

        .color-swatch {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 4px;
            border: 1px solid #ddd;
            vertical-align: middle;
            margin-right: 10px;
        }}

        .pass {{
            color: #28a745;
            font-weight: bold;
        }}

        .fail {{
            color: #dc3545;
            font-weight: bold;
        }}

        .warning {{
            color: #ffc107;
            font-weight: bold;
        }}

        .image-viewer {{
            position: relative;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}

        .image-viewer img {{
            width: 100%;
            display: block;
        }}

        .simulation-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .simulation-item {{
            text-align: center;
        }}

        .simulation-item img {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}

        .simulation-item .label {{
            margin-top: 10px;
            font-weight: 500;
            color: #555;
        }}

        .recommendations-list {{
            list-style: none;
            padding: 0;
        }}

        .recommendations-list li {{
            padding: 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}

        .recommendations-list .priority {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }}

        .priority-high {{
            background: #dc3545;
            color: white;
        }}

        .priority-medium {{
            background: #ffc107;
            color: #333;
        }}

        .priority-low {{
            background: #28a745;
            color: white;
        }}

        .code-snippet {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .summary-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>无障碍色彩测试报告</h1>
            <p>Wuzhangaishijueceshi Accessibility Analysis</p>
        </header>

        <section id="summary">
            <h2>执行摘要</h2>
            <div class="score-card">
                <div class="score-value">{overall_score}</div>
                <div class="score-label">综合评分 (0-100)</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {overall_score}%"></div>
                </div>
            </div>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value">{timestamp}</div>
                    <div class="label">分析时间</div>
                </div>
                <div class="summary-item">
                    <div class="value">{analysis_data.get('input_source', 'N/A')}</div>
                    <div class="label">输入源</div>
                </div>
                <div class="summary-item">
                    <div class="value">{threshold}</div>
                    <div class="label">相似阈值 (Delta E)</div>
                </div>
            </div>
        </section>
'''

    # Add color contrast analysis section
    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    # Add similar regions section
    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(
            analysis_data['similar_regions'],
            analysis_data.get('original_image')
        )

    # Add colorblind simulation section
    if 'cvd_analysis' in analysis_data:
        html_content += generate_cvd_section(analysis_data['cvd_analysis'])

    # Add recommendations section
    html_content += generate_recommendations_section(analysis_data)

    # Close HTML
    html_content += '''
        <footer>
            <p>Generated by 无障碍色彩测试 (Wuzhangaishijueceshi) Skill</p>
            <p>Based on WCAG 2.1/2.2 Accessibility Standards</p>
        </footer>
    </div>

    <script>
        // Interactive table sorting
        document.querySelectorAll('th').forEach(th => {
            th.addEventListener('click', () => {
                const table = th.closest('table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const colIndex = Array.from(th.parentElement.children).indexOf(th);

                rows.sort((a, b) => {
                    const aVal = a.children[colIndex].textContent;
                    const bVal = b.children[colIndex].textContent;
                    return aVal.localeCompare(bVal);
                });

                rows.forEach(row => tbody.appendChild(row));
            });
        });
    </script>
</body>
</html>
'''

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_contrast_section(color_analysis):
    """Generate color contrast analysis section."""
    stats = color_analysis.get('statistics', {})

    html = '''
        <section id="contrast-analysis">
            <h2>色彩对比度分析</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value">{}</div>
                    <div class="label">AA 合规率</div>
                </div>
                <div class="summary-item">
                    <div class="value">{}</div>
                    <div class="label">AAA 合规率</div>
                </div>
                <div class="summary-item">
                    <div class="value">{}</div>
                    <div class="label">分析颜色对</div>
                </div>
            </div>

            <h3 style="margin-top: 20px;">问题颜色对 (最低对比度)</h3>
            <table>
                <thead>
                    <tr>
                        <th>颜色 1</th>
                        <th>颜色 2</th>
                        <th>对比度</th>
                        <th>WCAG 等级</th>
                        <th>AA 合规</th>
                        <th>AAA 合规</th>
                    </tr>
                </thead>
                <tbody>
    '''.format(
        f"{stats.get('aa_pass_rate', 0):.1%}",
        f"{stats.get('aaa_pass_rate', 0):.1%}",
        stats.get('total_pairs', 0)
    )

    # Add problematic color pairs
    pairs = color_analysis.get('color_pairs', [])
    for pair in pairs[:10]:  # Show top 10 problematic pairs
        html += f'''
                    <tr>
                        <td>
                            <span class="color-swatch" style="background: {pair['color1']['hex']}"></span>
                            {pair['color1']['hex']}
                        </td>
                        <td>
                            <span class="color-swatch" style="background: {pair['color2']['hex']}"></span>
                            {pair['color2']['hex']}
                        </td>
                        <td>{pair['contrast_ratio']:.2f}:1</td>
                        <td>{pair['wcag_level']}</td>
                        <td class="{'pass' if pair['compliance']['aa'] else 'fail'}">
                            {'✓' if pair['compliance']['aa'] else '✗'}
                        </td>
                        <td class="{'pass' if pair['compliance']['aaa'] else 'fail'}">
                            {'✓' if pair['compliance']['aaa'] else '✗'}
                        </td>
                    </tr>
        '''

    html += '''
                </tbody>
            </table>
        </section>
    '''

    return html


def generate_similar_regions_section(similar_regions, original_image=None):
    """Generate similar color regions section."""
    total_issues = similar_regions.get('total_issues', 0)
    threshold = similar_regions.get('threshold', 5.0)

    html = f'''
        <section id="similar-regions">
            <h2>相近区域颜色分析</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value">{total_issues}</div>
                    <div class="label">相似区域对</div>
                </div>
                <div class="summary-item">
                    <div class="value">{threshold}</div>
                    <div class="label">阈值 (Delta E)</div>
                </div>
            </div>

            <h3 style="margin-top: 20px;">问题区域列表</h3>
            <table>
                <thead>
                    <tr>
                        <th>区域 1</th>
                        <th>区域 2</th>
                        <th>Delta E</th>
                        <th>严重程度</th>
                    </tr>
                </thead>
                <tbody>
    '''

    # Add similar regions
    regions = similar_regions.get('similar_regions', [])
    for region in regions[:20]:  # Show top 20
        severity = '高' if region['delta_e'] < 3 else '中' if region['delta_e'] < 4 else '低'
        severity_class = 'priority-high' if region['delta_e'] < 3 else 'priority-medium' if region['delta_e'] < 4 else 'priority-low'

        html += f'''
                    <tr>
                        <td>区域 {region['region1']}</td>
                        <td>区域 {region['region2']}</td>
                        <td>{region['delta_e']:.2f}</td>
                        <td><span class="priority {severity_class}">{severity}</span></td>
                    </tr>
        '''

    html += '''
                </tbody>
            </table>
        </section>
    '''

    return html


def generate_cvd_section(cvd_analysis):
    """Generate colorblind simulation section."""
    html = '''
        <section id="colorblind-simulations">
            <h2>色盲友好性评估</h2>
            <p>以下模拟展示了页面在不同色盲类型用户眼中的外观：</p>

            <div class="simulation-gallery">
    '''

    # Add simulation images
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="simulation-item">
                    <img src="data:image/png;base64,{cvd_data['image_base64']}" alt="{cvd_data['name']}">
                    <div class="label">{cvd_data['name']}</div>
                </div>
            '''

    html += '''
            </div>
        </section>
    '''

    return html


def generate_recommendations_section(analysis_data):
    """Generate developer recommendations section."""
    html = '''
        <section id="recommendations">
            <h2>开发者建议</h2>
            <ul class="recommendations-list">
    '''

    # Generate recommendations based on analysis
    recommendations = []

    # Contrast issues
    if 'color_analysis' in analysis_data:
        stats = analysis_data['color_analysis'].get('statistics', {})
        if stats.get('aa_pass_rate', 1.0) < 0.8:
            recommendations.append({
                'priority': 'high',
                'text': '提升色彩对比度以满足 WCAG AA 标准',
                'code': '/* 增加文本与背景的对比度 */\ncolor: #333; /* 深色文本 */\nbackground: #fff; /* 浅色背景 */'
            })

    # Similar regions
    if 'similar_regions' in analysis_data:
        similar = analysis_data['similar_regions']
        if similar.get('total_issues', 0) > 5:
            recommendations.append({
                'priority': 'medium',
                'text': '调整相近区域的颜色以提高可区分性',
                'code': '/* 使用更明显的颜色差异 */\n.primary { color: #0066cc; }\n.secondary { color: #004499; }'
            })

    # Add default recommendations if none
    if not recommendations:
        recommendations = [
            {
                'priority': 'low',
                'text': '确保所有文本元素满足 WCAG AA 对比度要求 (4.5:1)',
                'code': '/* 使用在线对比度检查工具验证 */'
            },
            {
                'priority': 'low',
                'text': '为颜色编码的信息提供替代指示（图标、文本标签）',
                'code': '/* 示例：错误状态 */\n.error::before { content: "⚠️"; }\n.error::after { content: " 错误"; }'
            }
        ]

    for rec in recommendations:
        html += f'''
            <li>
                <span class="priority priority-{rec['priority']}">{rec['priority'].upper()}</span>
                {rec['text']}
                <div class="code-snippet">{rec['code']}</div>
            </li>
        '''

    html += '''
            </ul>
        </section>
    '''

    return html


if __name__ == '__main__':
    # Example usage
    print("HTML Report Generator Module")
    print("Use with main.py to generate accessibility reports")
