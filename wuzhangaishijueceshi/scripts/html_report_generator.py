#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

This module generates self-contained, interactive HTML accessibility reports
using Tailwind CSS for a modern, B-side product dashboard experience.
"""

import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image

def image_to_base64(image, format='PNG'):
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def calculate_overall_score(analysis_data):
    score = 100
    if 'color_analysis' in analysis_data:
        stats = analysis_data['color_analysis'].get('statistics', {})
        score -= int((1 - stats.get('aa_pass_rate', 1.0)) * 30)
        score -= int((1 - stats.get('aaa_pass_rate', 1.0)) * 20)
    if 'similar_regions' in analysis_data:
        similar = analysis_data['similar_regions']
        if 'total_issues' in similar:
            score -= min(30, similar['total_issues'] * 2)
    if 'cvd_analysis' in analysis_data:
        score -= min(20, analysis_data['cvd_analysis'].get('total_issues', 0) * 2)
    return max(0, min(100, score))

def generate_html_report(analysis_data, output_path, threshold=5.0):
    overall_score = calculate_overall_score(analysis_data)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Determine score color
    score_color = "text-emerald-500" if overall_score >= 90 else "text-amber-500" if overall_score >= 70 else "text-rose-500"
    score_bg = "bg-emerald-500" if overall_score >= 90 else "bg-amber-500" if overall_score >= 70 else "bg-rose-500"

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>无障碍色彩分析控制台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }},
                }}
            }}
        }}
    </script>
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', sans-serif; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}
    </style>
</head>
<body class="text-slate-800 antialiased selection:bg-indigo-100 selection:text-indigo-900">
    
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">W</div>
                <h1 class="text-xl font-semibold text-slate-900">Accessibility Insight <span class="text-slate-400 font-normal text-sm ml-2">无障碍色彩测试报告</span></h1>
            </div>
            <div class="text-sm text-slate-500">生成时间: {timestamp}</div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        <section class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-center items-center col-span-1 md:col-span-1">
                <h2 class="text-sm font-medium text-slate-500 mb-2">系统健康度综合评分</h2>
                <div class="text-5xl font-bold {score_color} mb-4">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                    <div class="{score_bg} h-2 rounded-full" style="width: {overall_score}%"></div>
                </div>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 md:col-span-3 grid grid-cols-3 gap-6">
                <div class="flex flex-col justify-center border-r border-slate-100">
                    <span class="text-sm font-medium text-slate-500">测试来源</span>
                    <span class="text-lg font-semibold text-slate-800 mt-1">{analysis_data.get('input_source', 'Web Screenshot')}</span>
                </div>
                <div class="flex flex-col justify-center border-r border-slate-100 pl-4">
                    <span class="text-sm font-medium text-slate-500">WCAG 标准级别</span>
                    <span class="text-lg font-semibold text-slate-800 mt-1">AA & AAA (2.1)</span>
                </div>
                <div class="flex flex-col justify-center pl-4">
                    <span class="text-sm font-medium text-slate-500">相似色阈值 (ΔE)</span>
                    <span class="text-lg font-semibold text-slate-800 mt-1">{threshold}</span>
                </div>
            </div>
        </section>
'''

    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data['similar_regions'])

    if 'cvd_analysis' in analysis_data:
        html_content += generate_cvd_section(analysis_data['cvd_analysis'])

    html_content += generate_recommendations_section(analysis_data)

    html_content += '''
    </main>
    
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-8 border-t border-slate-200">
        <div class="text-center text-sm text-slate-400">
            &copy; 2026 Accessibility Vision Tester · Designed for Inclusive Web · Powered by Wuzhangaishijueceshi Skill
        </div>
    </footer>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_contrast_section(color_analysis):
    stats = color_analysis.get('statistics', {})
    
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                <h2 class="text-lg font-semibold text-slate-800">WCAG 对比度合规矩阵</h2>
                <div class="flex gap-4 text-sm">
                    <div class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-500"></span> AA 合规率: <span class="font-bold">{stats.get('aa_pass_rate', 0):.1%}</span></div>
                    <div class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-indigo-500"></span> AAA 合规率: <span class="font-bold">{stats.get('aaa_pass_rate', 0):.1%}</span></div>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">前景内容色</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">背景底色</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">测定对比度</th>
                            <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">AA 标准</th>
                            <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">智能算法建议</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100">
    '''

    pairs = color_analysis.get('color_pairs', [])
    for pair in pairs[:10]:
        aa_pass = pair['compliance']['aa']
        
        aa_badge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Pass</span>' if aa_pass else '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800">Fail</span>'
        
        # 动态渲染算法推送的建议色值
        suggestion_html = '<span class="text-slate-400 text-sm italic">无需修改</span>'
        suggestion = pair.get('suggestion')
        if suggestion:
            suggestion_html = f'''
                <div class="flex items-center justify-center gap-2">
                    <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    <div class="w-6 h-6 rounded border border-slate-200 shadow-inner" style="background-color: {suggestion['hex']}"></div>
                    <span class="text-sm font-mono text-emerald-700 font-medium">{suggestion['hex']}</span>
                </div>
            '''

        html += f'''
                        <tr class="hover:bg-slate-50 transition-colors duration-150">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="w-6 h-6 rounded border border-slate-200 shadow-inner mr-3" style="background-color: {pair['color1']['hex']}"></div>
                                    <span class="text-sm font-mono text-slate-700">{pair['color1']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="w-6 h-6 rounded border border-slate-200 shadow-inner mr-3" style="background-color: {pair['color2']['hex']}"></div>
                                    <span class="text-sm font-mono text-slate-700">{pair['color2']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-sm font-semibold text-slate-900">{pair['contrast_ratio']:.2f} : 1</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-center">{aa_badge}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-center bg-slate-50 border-l border-slate-100">{suggestion_html}</td>
                        </tr>
        '''
    html += '''
                    </tbody>
                </table>
            </div>
        </section>
    '''
    return html

def generate_similar_regions_section(similar_regions):
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">相似视觉块检测 (Delta E)</h2>
                <p class="mt-1 text-sm text-slate-500">检测界面中差异过小的相邻颜色，这可能导致视障用户无法区分组件边界。</p>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    '''
    
    regions = similar_regions.get('similar_regions', [])
    for region in regions[:6]:
        delta_e = region['delta_e']
        if delta_e < 3:
            border_color, tag_bg, tag_text = "border-rose-200", "bg-rose-100", "text-rose-700"
            level = "高风险"
        else:
            border_color, tag_bg, tag_text = "border-amber-200", "bg-amber-100", "text-amber-700"
            level = "中风险"

        html += f'''
                <div class="border {border_color} rounded-lg p-4 bg-white flex flex-col justify-between">
                    <div class="flex justify-between items-start mb-4">
                        <span class="text-sm text-slate-600 font-medium">区域 {region['region1']} & {region['region2']}</span>
                        <span class="px-2 py-1 rounded text-xs font-semibold {tag_bg} {tag_text}">{level}</span>
                    </div>
                    <div>
                        <div class="text-xs text-slate-400 uppercase tracking-wide">色差 (ΔE)</div>
                        <div class="text-2xl font-bold text-slate-800">{delta_e:.2f}</div>
                    </div>
                </div>
        '''
    html += '''
            </div>
        </section>
    '''
    return html

def generate_cvd_section(cvd_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">色觉障碍 (CVD) 视觉仿真画廊</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="group rounded-lg overflow-hidden border border-slate-200 hover:shadow-md transition-shadow">
                    <div class="aspect-video bg-slate-100 overflow-hidden relative">
                        <img src="data:image/png;base64,{cvd_data['image_base64']}" alt="{cvd_data['name']}" class="w-full h-full object-cover">
                    </div>
                    <div class="p-4 bg-white">
                        <h3 class="font-medium text-slate-800">{cvd_data['name']}</h3>
                        <p class="text-xs text-slate-500 mt-1">模拟该群体眼中的界面渲染效果</p>
                    </div>
                </div>
            '''
    html += '''
            </div>
        </section>
    '''
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">智能修复工单 (Actionable Fixes)</h2>
                <p class="mt-1 text-sm text-slate-500">基于二分查找算法为您推算的最近合规 CSS 色值，可直接复制使用。</p>
            </div>
            <div class="p-6 space-y-4">
    '''
    
    recommendations = []
    
    # 核心：动态提取底层计算出的 suggestion 并生成精准修复工单
    if 'color_analysis' in analysis_data:
        pairs = analysis_data['color_analysis'].get('color_pairs', [])
        failed_pairs = [p for p in pairs if p.get('suggestion')]
        
        # 提取问题最严重的 top 3 生成独立工单
        for idx, pair in enumerate(failed_pairs[:3]):
            orig_color = pair['color1']['hex']
            bg_color = pair['color2']['hex']
            new_color = pair['suggestion']['hex']
            contrast = pair['contrast_ratio']
            
            recommendations.append({
                'type': f'Action Item #{idx+1}',
                'bg': 'bg-rose-50 border-rose-200',
                'icon_text': 'text-rose-600',
                'title': f'修正低对比度元素 ({contrast:.2f}:1)',
                'desc': f'前景内容色 <span class="font-mono bg-white px-1 border border-slate-200 rounded">{orig_color}</span> 在背景 <span class="font-mono bg-white px-1 border border-slate-200 rounded">{bg_color}</span> 上无法清晰阅读。算法已推算出最佳替代色。',
                'code': f'/* 修复建议：直接替换组件 CSS 变量或属性 */\n.text-element {{\n  color: {new_color}; /* 已满足 WCAG AA 4.5:1 标准 */\n  background-color: {bg_color};\n}}'
            })

    # 如果所有对比度都完美通过，给出一个系统级的 Best Practice
    if not recommendations:
        recommendations.append({
            'type': 'Best Practice',
            'bg': 'bg-indigo-50 border-indigo-200',
            'icon_text': 'text-indigo-500',
            'title': '多模态状态提示',
            'desc': '所有的颜色对比度均已通过测试。建议进一步确保系统状态（如报错、成功）不要仅依赖颜色传达，应配合图标或文字说明。',
            'code': '\n<div class="text-emerald-600">\n  <svg class="w-4 h-4 inline">...</svg> \n  操作成功\n</div>'
        })

    for rec in recommendations:
        html += f'''
                <div class="border rounded-lg p-5 {rec['bg']} shadow-sm">
                    <div class="flex items-start gap-4">
                        <div class="mt-1 {rec['icon_text']}">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                        </div>
                        <div class="flex-1">
                            <div class="text-xs font-bold uppercase tracking-wider {rec['icon_text']} mb-1">{rec['type']}</div>
                            <h3 class="text-base font-semibold text-slate-900 mb-2">{rec['title']}</h3>
                            <p class="text-sm text-slate-700 mb-4 leading-relaxed">{rec['desc']}</p>
                            <div class="bg-slate-900 rounded-md p-4 overflow-x-auto border border-slate-700">
                                <pre class="text-sm font-mono text-emerald-400"><code>{rec['code']}</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
        '''
    html += '''
            </div>
        </section>
    '''
    return html

if __name__ == '__main__':
    print("HTML Report Generator Module optimized with Tailwind CSS and Smart Suggestions.")