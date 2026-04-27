#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

Optimized for: Readability, Professional Terminology Explanations, 
Printability, User Empathy, and CVD Boundary Melt Detection Visualization.
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
        score -= int((1 - stats.get('apca_pass_rate', 1.0)) * 20)
    
    if 'similar_regions' in analysis_data:
        similar = analysis_data['similar_regions']
        if 'total_issues' in similar:
            score -= min(20, similar['total_issues'] * 2)
        # 绝杀功能：色盲边缘消融额外扣分
        melt_issues = sum(1 for r in similar.get('similar_regions', []) if r.get('melt_risks'))
        if melt_issues > 0:
            score -= min(15, melt_issues * 3)
            
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
    <title>无障碍色彩审计报告 - {timestamp}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{ extend: {{ fontFamily: {{ sans: ['Inter', 'sans-serif'] }} }} }}
        }}
    </script>
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', sans-serif; scroll-behavior: smooth; }}
        
        .tooltip {{ position: relative; display: inline-block; cursor: help; }}
        .tooltip .tooltiptext {{
            visibility: hidden; width: 240px; background-color: #1e293b; color: #fff;
            text-align: left; border-radius: 6px; padding: 10px; position: absolute;
            z-index: 100; bottom: 125%; left: 50%; margin-left: -120px; opacity: 0;
            transition: opacity 0.3s; font-size: 0.75rem; line-height: 1.4; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }}
        .tooltip:hover .tooltiptext {{ visibility: visible; opacity: 1; }}

        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background-color: white; }}
            .container {{ max-width: 100% !important; margin: 0 !important; padding: 0 !important; }}
            .shadow-sm, .shadow-md, .shadow-lg {{ shadow: none !important; border: 1px solid #e2e8f0 !important; }}
            header {{ background-color: #0f172a !important; -webkit-print-color-adjust: exact; }}
        }}

        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
    </style>
</head>
<body class="text-slate-800 antialiased">
    
    <header class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center text-white font-bold">Wz</div>
                <h1 class="text-lg font-semibold text-white">色彩无障碍审计报告</h1>
            </div>
            <div class="flex gap-3">
                <button onclick="window.print()" class="no-print text-xs px-3 py-1.5 bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-2">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
                    打印报告 / PDF
                </button>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6" role="main">
'''
    
    if analysis_data.get('requires_multimodal_check'):
        html_content += '''
        <div class="bg-rose-50 border-l-4 border-rose-500 p-4 rounded shadow-sm" role="alert">
            <div class="flex">
                <div class="flex-shrink-0">⚠️</div>
                <div class="ml-3">
                    <h3 class="text-sm font-bold text-rose-800">强制规则：多通道信息传达 (WCAG 1.4.1)</h3>
                    <p class="text-sm text-rose-700 mt-1">检测到典型的红绿功能色。<b>色盲用户无法通过颜色区分状态</b>，请务必在 UI 中补充图标 (如 ✅/❌) 或文字标签。</p>
                </div>
            </div>
        </div>
        '''

    html_content += f'''
        <section class="grid grid-cols-1 md:grid-cols-12 gap-6" aria-label="诊断概览">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 md:col-span-4 text-center">
                <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">包容性健康度</h2>
                <div class="text-6xl font-bold {score_color} tracking-tighter mb-4">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 mb-2">
                    <div class="{score_bg} h-1.5 rounded-full transition-all duration-1000" style="width: {overall_score}%"></div>
                </div>
                <p class="text-xs text-slate-400">基于 WCAG 2.1 与 APCA 综合计算</p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 md:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <div class="flex justify-between items-end mb-2">
                        <span class="text-sm font-semibold text-slate-600">
                            APCA 视知觉合规率
                            <span class="tooltip">ⓘ<span class="tooltiptext"><b>APCA (WCAG 3.0):</b> 现代视觉算法，根据人眼对不同背景下的文字亮度的真实感知来评分，比老标准更精准。</span></span>
                        </span>
                        <span class="text-lg font-bold text-indigo-600">{apca_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-indigo-500 h-2 rounded-full" style="width: {apca_rate}%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between items-end mb-2">
                        <span class="text-sm font-semibold text-slate-600">
                            UI 控件边界清晰度
                        </span>
                        <span class="text-lg font-bold text-sky-600">{ui_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
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

    html_content += generate_glossary_section()

    html_content += '''
    </main>
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 mt-8 border-t border-slate-200 text-center text-xs text-slate-400 no-print">
        <p>无障碍色彩审计系统 · 企业级版本</p>
        <p class="mt-2 text-slate-300 leading-relaxed">依据 WCAG 2.1/2.2 及 APCA 0.98G 标准生成</p>
    </footer>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_contrast_section(color_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden" aria-label="色彩对比度矩阵">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                <h2 class="font-bold text-slate-800">色彩矩阵审计</h2>
                <span class="text-[10px] text-slate-400 uppercase tracking-widest">Top Issues</span>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-400 uppercase">颜色对 (前景/背景)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">WCAG 2.1</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">APCA (Lc)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">UI 安全</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100">
    '''
    pairs = color_analysis.get('color_pairs', [])
    for pair in pairs[:6]:
        m = pair.get('metrics', {})
        wcag_pass = m.get("aa_normal")
        apca_pass = m.get("apca_pass_normal")
        
        html += f'''
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3 font-mono text-[11px]">
                                    <div class="flex -space-x-2">
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color1']['hex']}; z-index: 2;"></div>
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color2']['hex']}; z-index: 1;"></div>
                                    </div>
                                    <span class="text-slate-600">{pair['color1']['hex']}</span>
                                    <span class="text-slate-300">/</span>
                                    <span class="text-slate-600">{pair['color2']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {'bg-emerald-100 text-emerald-700' if wcag_pass else 'bg-rose-100 text-rose-700'}">
                                    {m.get("ratio", 0):.2f}:1
                                </span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="text-[11px] font-bold { 'text-indigo-600' if apca_pass else 'text-slate-400' }">Lc {m.get("apca_lc", 0):.0f}</span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                {'<span class="text-emerald-500">✓</span>' if m.get("ui_component") else '<span class="text-rose-300">✗</span>'}
                            </td>
                        </tr>
        '''
    html += '</tbody></table></div></section>'
    return html

def generate_similar_regions_section(similar_regions):
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden" aria-label="相邻色块检测">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50">
                <h2 class="font-bold text-slate-800">
                    视障边缘消融预警 (CVD Melt Detection)
                    <span class="tooltip">ⓘ<span class="tooltiptext">结合 <b>CIEDE2000 色差</b>与<b>色盲生理矩阵</b>，揪出那些正常人看着清晰，但在色盲眼中彻底糊在一起的伪装颜色。</span></span>
                </h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    '''
    regions = similar_regions.get('similar_regions', [])
    for region in regions[:6]:
        normal_de = region.get('delta_e', 0)
        cvd_de = region.get('worst_cvd_delta_e', normal_de)
        melt_risks = region.get('melt_risks', [])

        # 核心逻辑：基于 melt_risks 的存在与否决定 UI 等级
        if melt_risks:
            # 紫色高危告警 (色盲边缘消融)
            border_color, tag_bg, tag_text = "border-purple-300", "bg-purple-100", "text-purple-700"
            title = "🚨 色盲边缘消融"
        elif normal_de < 3:
            # 常规红色告警
            border_color, tag_bg, tag_text = "border-rose-200", "bg-rose-100", "text-rose-700"
            title = "高危边界重叠"
        else:
            # 常规黄色警告
            border_color, tag_bg, tag_text = "border-amber-200", "bg-amber-100", "text-amber-700"
            title = "中度边界模糊"

        # 渲染特定的色盲暴跌警告
        melt_html = ""
        if melt_risks:
            # 提取如 "Protanopia" 这样的词缀
            melt_types = ", ".join([m.split()[0] for m in melt_risks])
            melt_html = f'''
                <div class="mt-3 p-2 bg-purple-50 border border-purple-100 rounded shadow-sm">
                    <p class="text-[10px] text-purple-800 font-medium leading-relaxed">
                        <svg class="w-3 h-3 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                        在 <b>{melt_types}</b> 用户眼中，色差将暴跌至 <span class="font-black text-purple-900 bg-purple-200 px-1 rounded">ΔE {cvd_de:.1f}</span>，该边界将彻底消失。
                    </p>
                </div>
            '''

        html += f'''
                <div class="border {border_color} rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-bold text-slate-500 uppercase">{title}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-black {tag_bg} {tag_text}">常规 ΔE {normal_de:.1f}</span>
                    </div>
                    <p class="text-[11px] text-slate-600 leading-relaxed">区域 {region['region1']} 与区域 {region['region2']} 相邻。</p>
                    {melt_html}
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-slate-900 rounded-xl shadow-xl overflow-hidden no-print" aria-label="智能修复工单">
            <div class="px-6 py-5 bg-slate-800 border-b border-slate-700">
                <h2 class="text-white font-bold flex items-center gap-2">
                    <span class="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
                    智能修复建议中心
                </h2>
            </div>
            <div class="p-6 space-y-6">
    '''
    pairs = analysis_data.get('color_analysis', {}).get('color_pairs', [])
    failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
    
    for idx, pair in enumerate(failed_pairs[:3]):
        orig_c, bg_c = pair['color1']['hex'], pair['color2']['hex']
        dm = pair.get('dark_mode_eval', {})
        dark_warning = f'<span class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[9px] border border-amber-500/30 ml-2">深色模式失效风险</span>' if (dm.get('applicable') and not dm.get('survives_dark_mode')) else ""

        html += f'''
            <div class="border border-slate-700 rounded-lg p-5 bg-slate-800/40">
                <div class="flex justify-between items-start mb-4">
                    <span class="text-[10px] font-black text-rose-400 uppercase tracking-widest">问题单 #{idx+1} {dark_warning}</span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <p class="text-xs text-slate-400">当前方案 <span class="text-rose-300 font-mono">{orig_c}</span> 在 <span class="text-slate-500 font-mono">{bg_c}</span> 上对比度极差。我们为您计算了替代方案：</p>
                        '''
        if pair.get('safe_palette_suggestion'):
            safe = pair['safe_palette_suggestion']
            html += f'''
                        <div class="bg-slate-800 p-3 rounded border border-slate-700 hover:border-indigo-500/50 transition-colors">
                            <p class="text-[9px] text-indigo-400 font-bold uppercase mb-2 italic">🏆 方案 A：色盲安全色 (Okabe-Ito Palette)</p>
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded border border-slate-600 shadow-inner" style="background-color: {safe['hex']}"></div>
                                <div>
                                    <div class="text-xs font-bold text-white">{safe['name']}</div>
                                    <div class="text-[10px] font-mono text-emerald-400">{safe['hex']}</div>
                                </div>
                            </div>
                        </div>
            '''
        
        auto_c = pair.get('suggestion', {}).get('hex', '')
        if auto_c:
            html += f'''
                        <div class="bg-slate-800 p-3 rounded border border-slate-700">
                            <p class="text-[9px] text-slate-400 font-bold uppercase mb-2">方案 B：算法亮度微调 (HSL 二分查找)</p>
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded border border-slate-600 shadow-inner" style="background-color: {auto_c}"></div>
                                <div class="text-[10px] font-mono text-indigo-400">{auto_c}</div>
                            </div>
                        </div>
            '''
            
        html += f'''
                    </div>
                    <div class="bg-slate-950 rounded p-4 font-mono text-[11px] border border-slate-800">
                        <div class="text-slate-600 mb-2">// 修复代码片段</div>
                        <div class="text-emerald-400">.ui-component {{</div>
                        <div class="text-slate-300 pl-4">color: <span class="text-indigo-400">{safe['hex'] if pair.get('safe_palette_suggestion') else auto_c}</span>;</div>
                        <div class="text-slate-300 pl-4">background: {bg_c};</div>
                        <div class="text-emerald-400">}}</div>
                    </div>
                </div>
            </div>
        '''
    if not failed_pairs:
        html += '<div class="text-emerald-400 text-sm">🎉 完美！暂未发现任何色彩对比度级别的阻断性问题。</div>'
    html += '</div></section>'
    return html

def generate_cvd_section(cvd_analysis):
    cvd_meta = {
        "protanopia": {"desc": "红色盲", "pop": "男性发病率 ~1.0%", "detail": "由于缺乏长波长感光色素，难以区分红色与绿色。"},
        "deuteranopia": {"desc": "绿色盲", "pop": "男性发病率 ~1.1%", "detail": "最常见的色盲类型，难以辨别红、绿、褐色。"},
        "tritanopia": {"desc": "蓝色盲", "pop": "极为罕见 <0.01%", "detail": "难以区分蓝色与绿色、紫色与红色。"}
    }
    
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden" aria-label="色盲视觉模拟">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50">
                <h2 class="font-bold text-slate-800">色觉障碍 (CVD) 视觉模拟</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-8">
    '''
    for cvd_type, cvd_data in cvd_analysis.items():
        meta = cvd_meta.get(cvd_type.lower(), {"desc": cvd_type, "pop": "-", "detail": ""})
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="space-y-3">
                    <div class="rounded-lg overflow-hidden border border-slate-100 shadow-sm">
                        <img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto grayscale-0 hover:scale-105 transition-transform duration-500">
                    </div>
                    <div>
                        <div class="flex justify-between items-center">
                            <h3 class="text-sm font-bold text-slate-800">{meta['desc']} <span class="text-[10px] text-slate-400 font-normal">({cvd_data['name']})</span></h3>
                            <span class="text-[9px] px-1.5 py-0.5 bg-slate-100 rounded text-slate-500">{meta['pop']}</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-1 leading-relaxed">{meta['detail']}</p>
                    </div>
                </div>
            '''
    html += '</div></section>'
    return html

def generate_glossary_section():
    return '''
        <section class="bg-indigo-50/50 rounded-xl border border-indigo-100 p-8 no-print" aria-label="术语表">
            <h2 class="text-sm font-bold text-indigo-900 uppercase tracking-widest mb-6">术语速查手册 (Glossary)</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">WCAG 2.1 对比度 (Contrast Ratio)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">传统的无障碍标准。计算文本与背景的亮度比例。普通文本要求 4.5:1 (AA级)，大文本要求 3.0:1。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">APCA (WCAG 3.0 现代算法)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">下一代视觉算法。它考虑了字体大小和人眼在不同背景下的知觉差异。分数单位是 Lc，绝对值越高越清晰。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">色盲边缘消融 (CVD Boundary Melt)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">一种极端的隐形缺陷。两个颜色在正常人眼中对比强烈，但在红绿色盲眼中由于缺失某种感光色素，色差 (ΔE) 会暴跌至 3 以下，导致两个色块融为一体，边界完全消失。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">Okabe-Ito 色盲安全色板</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">一套经过科学严谨测试的 8 色调色盘，能够同时被红色盲、绿色盲和正常视力的人群毫无障碍地辨认。</p>
                </div>
            </div>
        </section>
    '''

if __name__ == '__main__':
    print("HTML Report Generator optimized with CVD Boundary Melt Detection Visualization.")