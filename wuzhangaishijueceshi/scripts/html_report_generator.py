#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

This module generates self-contained, interactive HTML accessibility reports
using Tailwind CSS for a modern, enterprise-grade UX dashboard experience.
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
        score -= int((1 - stats.get('apca_pass_rate', 1.0)) * 20) # 引入 APCA 惩罚权重
    if 'similar_regions' in analysis_data:
        similar = analysis_data['similar_regions']
        if 'total_issues' in similar:
            score -= min(30, similar['total_issues'] * 2)
    return max(0, min(100, score))

def generate_html_report(analysis_data, output_path, threshold=5.0):
    overall_score = calculate_overall_score(analysis_data)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    score_color = "text-emerald-500" if overall_score >= 90 else "text-amber-500" if overall_score >= 70 else "text-rose-500"
    score_bg = "bg-emerald-500" if overall_score >= 90 else "bg-amber-500" if overall_score >= 70 else "bg-rose-500"
    
    stats = analysis_data.get('color_analysis', {}).get('statistics', {})
    apca_rate = stats.get('apca_pass_rate', 0) * 100
    ui_rate = stats.get('ui_component_pass_rate', 0) * 100

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>企业级无障碍色彩分析控制台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{ extend: {{ fontFamily: {{ sans: ['Inter', 'sans-serif'] }} }} }}
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
    
    <header class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center text-white font-bold tracking-tighter">Wz</div>
                <h1 class="text-xl font-semibold text-white">Accessibility <span class="font-light">Audit</span></h1>
            </div>
            <div class="flex gap-4 items-center">
                <span class="text-xs px-2 py-1 bg-slate-800 text-slate-300 rounded border border-slate-700">WCAG 2.1 & 3.0(APCA)</span>
                <div class="text-sm text-slate-400">{timestamp}</div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
'''
    
    # 注入红绿冲突的顶级警告
    if analysis_data.get('requires_multimodal_check'):
        html_content += '''
        <div class="bg-rose-50 border-l-4 border-rose-500 p-4 rounded-r shadow-sm">
            <div class="flex">
                <div class="flex-shrink-0"><svg class="h-5 w-5 text-rose-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg></div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-rose-800">强制多通道设计原则 (WCAG 1.4.1) 预警</h3>
                    <p class="text-sm text-rose-700 mt-1">检测到画面中大面积存在红绿色系。如果您在使用这些颜色表示“错误/成功”状态，请务必同时附带 <b>图标 (Icons)</b> 或 <b>底纹图案</b>，不能仅依靠颜色传达信息，否则红色盲/绿色盲用户将无法分辨。</p>
                </div>
            </div>
        </div>
        '''

    html_content += f'''
        <section class="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 md:col-span-4 flex flex-col justify-center items-center">
                <h2 class="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">系统包容度总分</h2>
                <div class="text-6xl font-bold {score_color} mb-4 tracking-tighter">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-2"><div class="{score_bg} h-2 rounded-full" style="width: {overall_score}%"></div></div>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 md:col-span-8 flex flex-col justify-between">
                <h2 class="text-sm font-medium text-slate-800 mb-4 border-b border-slate-100 pb-2">现代评测指标 (Modern Metrics)</h2>
                <div class="space-y-5">
                    <div>
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-slate-600 font-medium">APCA (WCAG 3.0) 视知觉合规率</span>
                            <span class="font-bold text-slate-800">{apca_rate:.1f}%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-indigo-500 h-2 rounded-full" style="width: {apca_rate}%"></div></div>
                    </div>
                    <div>
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-slate-600 font-medium">UI 非文本控件可视度 (边界对比 > 3.0)</span>
                            <span class="font-bold text-slate-800">{ui_rate:.1f}%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
                    </div>
                </div>
            </div>
        </section>
    '''

    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data['similar_regions'])

    html_content += generate_recommendations_section(analysis_data)

    if 'cvd_analysis' in analysis_data:
        html_content += generate_cvd_section(analysis_data['cvd_analysis'])

    html_content += '''
    </main>
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-8 border-t border-slate-200 text-center text-sm text-slate-400">
        &copy; 2026 Accessibility Vision Tester · Powered by Wuzhangaishijueceshi Skill
    </footer>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_contrast_section(color_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">色彩矩阵审计 (Color Matrix Audit)</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">颜色对</th>
                            <th class="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase" title="古典算法">WCAG 2.1</th>
                            <th class="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase" title="现代感知算法">APCA 3.0 (Lc)</th>
                            <th class="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase" title="非文本/UI控件">UI 安全边界</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100">
    '''

    pairs = color_analysis.get('color_pairs', [])
    for pair in pairs[:8]:
        m = pair.get('metrics', {})
        
        wcag_badge = f'<span class="px-2 py-1 rounded text-xs font-medium {"bg-emerald-100 text-emerald-800" if m.get("aa_normal") else "bg-rose-100 text-rose-800"}">{m.get("ratio", 0):.2f}:1</span>'
        apca_badge = f'<span class="px-2 py-1 rounded text-xs font-medium {"bg-indigo-100 text-indigo-800" if m.get("apca_pass_normal") else "bg-slate-100 text-slate-500"}">Lc {m.get("apca_lc", 0):.0f}</span>'
        ui_icon = '<svg class="w-4 h-4 text-emerald-500 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>' if m.get("ui_component") else '<svg class="w-4 h-4 text-rose-400 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>'
        
        html += f'''
                        <tr class="hover:bg-slate-50">
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <div class="flex -space-x-2">
                                        <div class="w-8 h-8 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color1']['hex']}; z-index: 2;"></div>
                                        <div class="w-8 h-8 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color2']['hex']}; z-index: 1;"></div>
                                    </div>
                                    <div class="text-xs font-mono text-slate-500">{pair['color1']['hex']} on {pair['color2']['hex']}</div>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-center">{wcag_badge}</td>
                            <td class="px-6 py-4 text-center">{apca_badge}</td>
                            <td class="px-6 py-4 text-center">{ui_icon}</td>
                        </tr>
        '''
    html += '</tbody></table></div></section>'
    return html

def generate_similar_regions_section(similar_regions):
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">视障边界模糊预警 (Delta E)</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
    '''
    regions = similar_regions.get('similar_regions', [])
    for region in regions[:3]:
        delta_e = region['delta_e']
        border_color, tag_bg, tag_text = ("border-rose-200", "bg-rose-100", "text-rose-700") if delta_e < 3 else ("border-amber-200", "bg-amber-100", "text-amber-700")
        html += f'''
                <div class="border {border_color} rounded-lg p-4">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-sm font-medium text-slate-700">区域重叠风险</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold {tag_bg} {tag_text}">ΔE {delta_e:.1f}</span>
                    </div>
                    <p class="text-xs text-slate-500">区域 {region['region1']} 与 {region['region2']} 色差过小，色弱用户可能无法区分边界。</p>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-800 bg-slate-800/50">
                <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                    <svg class="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    智能修复中心 (Resolution Hub)
                </h2>
            </div>
            <div class="p-6 space-y-6">
    '''
    
    recommendations = []
    if 'color_analysis' in analysis_data:
        pairs = analysis_data['color_analysis'].get('color_pairs', [])
        failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
        
        for idx, pair in enumerate(failed_pairs[:3]):
            orig_c, bg_c = pair['color1']['hex'], pair['color2']['hex']
            
            # 提取 Okabe-Ito 安全色建议
            safe_html = ""
            if pair.get('safe_palette_suggestion'):
                safe_c = pair['safe_palette_suggestion']
                safe_html = f'''
                    <div class="mt-4 p-3 bg-slate-800 rounded border border-slate-700">
                        <p class="text-xs text-slate-400 mb-2 uppercase tracking-wide">🏆 首选：替换为权威色盲安全色 (Okabe-Ito Palette)</p>
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded shadow-inner border border-slate-600" style="background-color: {safe_c['hex']}"></div>
                            <div>
                                <div class="text-sm font-medium text-white">{safe_c['name']}</div>
                                <div class="text-xs font-mono text-emerald-400">{safe_c['hex']}</div>
                            </div>
                        </div>
                    </div>
                '''
            
            # 提取二分法推算建议
            auto_c = pair.get('suggestion', {}).get('hex', '')
            auto_html = f'''
                <div class="mt-3 text-sm text-slate-300">
                    <p>或者采用算法推算色：保留原色相，调整亮度至 <span class="font-mono text-indigo-400">{auto_c}</span>。</p>
                </div>
            ''' if auto_c else ""

            # 深色模式警告
            dark_warning = ""
            dm = pair.get('dark_mode_eval', {})
            if dm.get('applicable') and not dm.get('survives_dark_mode'):
                dark_warning = f'<span class="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">⚠️ 深色模式翻转失效</span>'

            html += f'''
                <div class="border border-slate-700 rounded-lg p-5 bg-slate-800/30">
                    <div class="text-xs font-bold text-rose-400 mb-1">Issue #{idx+1} {dark_warning}</div>
                    <p class="text-sm text-slate-300 mb-3">将 <span class="font-mono text-rose-300">{orig_c}</span> 应用于 <span class="font-mono text-slate-400">{bg_c}</span> 上会导致严重阅读障碍。</p>
                    {safe_html}
                    {auto_html}
                </div>
            '''
            
    if not failed_pairs:
        html += '<div class="text-emerald-400 text-sm">🎉 完美！暂未发现任何色彩对比度级别的阻断性问题。</div>'

    html += '</div></section>'
    return html

def generate_cvd_section(cvd_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50">
                <h2 class="text-lg font-semibold text-slate-800">视障模式仿真 (CVD Simulation)</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
    '''
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="group rounded-lg overflow-hidden border border-slate-200">
                    <img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto object-cover opacity-90 group-hover:opacity-100 transition-opacity">
                    <div class="p-3 bg-white border-t border-slate-100">
                        <h3 class="text-sm font-medium text-slate-800 text-center">{cvd_data['name']}</h3>
                    </div>
                </div>
            '''
    html += '</div></section>'
    return html

if __name__ == '__main__':
    print("Dashboard Generator optimized with APCA, Dark Mode, and Okabe-Ito integration.")