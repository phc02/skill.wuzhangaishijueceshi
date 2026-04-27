#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

Optimized for: Printability, Tooltip Bug Fixes, Algorithm Transparency, 
Dynamic Image Drawing for Regions, and CVD Gallery Layout.
"""

import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw

def image_to_base64(image, format='PNG'):
    buffered = BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format=format, quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 新增：在原图上画框并生成局部缩略图的函数
def generate_annotated_thumbnail(img_base64, b1, b2):
    if not img_base64 or not b1 or not b2:
        return None
    try:
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data)).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # 用显眼的粗线框出两个有风险的区域
        draw.rectangle([b1['x_min'], b1['y_min'], b1['x_max'], b1['y_max']], outline="#ef4444", width=5) # 红色框
        draw.rectangle([b2['x_min'], b2['y_min'], b2['x_max'], b2['y_max']], outline="#eab308", width=5) # 黄色框
        
        # 缩小尺寸以节省 HTML 体积
        img.thumbnail((300, 300))
        return image_to_base64(img, format='JPEG')
    except Exception as e:
        return None

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
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', sans-serif; scroll-behavior: smooth; }}
        
        /* 修复 Tooltip 层级与遮挡问题 */
        .tooltip-container {{ position: relative; display: inline-flex; align-items: center; cursor: help; z-index: 50; }}
        .tooltip-container .tooltiptext {{
            visibility: hidden; width: 260px; background-color: #1e293b; color: #f8fafc;
            text-align: left; border-radius: 6px; padding: 12px; position: absolute;
            bottom: 125%; left: 50%; transform: translateX(-50%); opacity: 0;
            transition: opacity 0.2s, visibility 0.2s; font-size: 0.75rem; line-height: 1.5; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
            pointer-events: none;
        }}
        .tooltip-container .tooltiptext::after {{
            content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px;
            border-width: 5px; border-style: solid; border-color: #1e293b transparent transparent transparent;
        }}
        .tooltip-container:hover .tooltiptext {{ visibility: visible; opacity: 1; }}

        /* 打印适配 */
        @media print {{
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            .no-print {{ display: none !important; }}
            body {{ background-color: white; }}
        }}

        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
    </style>
</head>
<body class="text-slate-800 antialiased">
    <header class="bg-slate-900 border-b border-slate-800 sticky top-0 z-[100]">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center text-white font-bold">Wz</div>
                <h1 class="text-lg font-semibold text-white">色彩无障碍审计报告</h1>
            </div>
            <button onclick="window.print()" class="no-print text-xs px-3 py-1.5 bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-2">
                打印报告 / PDF
            </button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8" role="main">
'''

    # Dashboard 顶层重构
    html_content += f'''
        <div class="mb-2">
            <h2 class="text-2xl font-bold text-slate-800">系统包容性分析概览</h2>
            <p class="text-sm text-slate-500 mt-1">评估设计稿在多样化视觉群体（如色弱、低视力、不同光照环境）中的可读性与边界清晰度。</p>
        </div>

        <section class="grid grid-cols-1 lg:grid-cols-12 gap-6" aria-label="诊断概览">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-4 text-center flex flex-col justify-center">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">综合健康度总分</h3>
                <div class="text-6xl font-bold {score_color} tracking-tighter mb-4">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 mb-3">
                    <div class="{score_bg} h-1.5 rounded-full" style="width: {overall_score}%"></div>
                </div>
                <p class="text-[11px] text-slate-500">基于以下两大核心维度加权计算</p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                <div class="flex flex-col justify-center">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                            维度一：APCA 视知觉合规率
                            <div class="tooltip-container">
                                <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                <span class="tooltiptext"><b>意义：</b>传统 WCAG 算法在深色模式下容易失效。APCA 是 WCAG 3.0 的下一代算法，基于人类视网膜模型，能极其精准地测算“文字与背景”的真实阅读清晰度。</span>
                            </div>
                        </span>
                        <span class="text-lg font-bold text-indigo-600">{apca_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-indigo-500 h-2 rounded-full" style="width: {apca_rate}%"></div></div>
                    <p class="text-[10px] text-slate-400">关注对象：所有文本信息与排版</p>
                </div>

                <div class="flex flex-col justify-center border-t md:border-t-0 md:border-l border-slate-100 md:pl-8 pt-4 md:pt-0">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                            维度二：UI 控件边界清晰度
                            <div class="tooltip-container">
                                <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                <span class="tooltiptext"><b>意义：</b>确保界面上的按钮轮廓、输入框边缘、图表线条等“非文字组件”能够被低视力用户清晰识别，防止功能按键在背景中隐形。</span>
                            </div>
                        </span>
                        <span class="text-lg font-bold text-sky-600">{ui_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
                    <p class="text-[10px] text-slate-400">关注对象：按钮、Icon、图形与分割线</p>
                </div>
            </div>
        </section>
'''

    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    # 传入整个 analysis_data 以便读取 original_image_base64 来画框
    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data)

    html_content += generate_recommendations_section(analysis_data)

    if 'cvd_analysis' in analysis_data or 'original_image_base64' in analysis_data:
        html_content += generate_cvd_section(analysis_data)

    html_content += generate_glossary_section()

    html_content += '''
    </main>
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 mt-8 border-t border-slate-200 text-center text-xs text-slate-400 no-print">
        <p>无障碍色彩审计系统 · 强驱动版本</p>
    </footer>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_contrast_section(color_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="色彩矩阵审计">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-2">色彩矩阵压力测试 (Color Matrix Audit)</h2>
                <div class="bg-indigo-50 border border-indigo-100 p-3 rounded text-xs text-indigo-800 leading-relaxed">
                    <b>工作原理：</b> 本模块使用 <b>K-Means 机器学习算法</b> 对整个界面进行高频采样，聚类提取出最具代表性的 Top 15 主题色。<br>
                    <b>审计目的：</b> 算法会将这些核心色进行两两“交叉互切”（模拟它们互为前景和背景的情况），旨在暴露出设计稿中所有潜在的色彩雷区，防患于未然。
                </div>
            </div>
            <div class="overflow-visible">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50/50">
                        <tr>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-400 uppercase">交叉颜色对 (前景/背景)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">WCAG 2.1 传统对比</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">
                                <div class="flex items-center justify-center gap-1">
                                    APCA (Lc)
                                    <div class="tooltip-container">
                                        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        <span class="tooltiptext">分数单位为 Lc。普通文本要求绝对值大于 60，大标题要求大于 45。数值越高，对比越清晰。</span>
                                    </div>
                                </div>
                            </th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">UI 控件安全</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100 rounded-b-xl">
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
                                {'<span class="text-emerald-500">✓ 通过</span>' if m.get("ui_component") else '<span class="text-rose-400">✗ 隐患</span>'}
                            </td>
                        </tr>
        '''
    html += '</tbody></table></div></section>'
    return html

def generate_similar_regions_section(analysis_data):
    similar_data = analysis_data.get('similar_regions', {})
    regions = similar_data.get('similar_regions', [])
    orig_b64 = analysis_data.get('original_image_base64')

    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="相邻色块检测">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 flex items-center gap-2">
                    视障边缘消融预警 (CVD Melt Detection)
                    <div class="tooltip-container">
                        <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <span class="tooltiptext">结合 <b>CIEDE2000 国际色差公式</b>与<b>色盲生理矩阵</b>，能揪出那些正常人看着清晰，但在色盲眼中彻底糊在一起的伪装颜色，防止组件消失。</span>
                    </div>
                </h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    
    for region in regions[:3]: # 控制渲染数量，保证有图时排版美观
        normal_de = region.get('delta_e', 0)
        cvd_de = region.get('worst_cvd_delta_e', normal_de)
        melt_risks = region.get('melt_risks', [])

        b1 = region.get('region1_boundaries')
        b2 = region.get('region2_boundaries')

        if melt_risks:
            border_color, tag_bg, tag_text = "border-purple-300", "bg-purple-100", "text-purple-700"
            title = "🚨 色盲边缘消融"
        else:
            border_color, tag_bg, tag_text = "border-rose-200", "bg-rose-100", "text-rose-700"
            title = "高危边界重叠"

        melt_html = ""
        if melt_risks:
            melt_types = ", ".join([m.split()[0] for m in melt_risks])
            melt_html = f'''
                <div class="mt-3 p-2 bg-purple-50 border border-purple-100 rounded shadow-sm">
                    <p class="text-[10px] text-purple-800 font-medium leading-relaxed">
                        在 <b>{melt_types}</b> 用户眼中，该边界会彻底消失 (色差暴跌至 ΔE {cvd_de:.1f})。
                    </p>
                </div>
            '''
            
        # 绝杀：直接在后端动态画框
        annotated_img_b64 = generate_annotated_thumbnail(orig_b64, b1, b2)
        img_html = ""
        if annotated_img_b64:
            img_html = f'''
                <div class="mt-4 mb-2 bg-slate-100 p-1 rounded border border-slate-200">
                    <img src="data:image/jpeg;base64,{annotated_img_b64}" alt="标注的冲突区域" class="w-full h-32 object-cover rounded shadow-inner">
                    <p class="text-center text-[9px] text-slate-400 mt-1 uppercase tracking-wider">冲突定位 (红框与黄框)</p>
                </div>
            '''

        html += f'''
                <div class="border {border_color} rounded-lg p-5 bg-white shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-slate-600 uppercase">{title}</span>
                            <div class="tooltip-container">
                                <span class="px-2 py-0.5 rounded text-[10px] font-black cursor-help {tag_bg} {tag_text}">常规 ΔE {normal_de:.1f}</span>
                                <span class="tooltiptext"><b>Delta E (ΔE)：</b>衡量两种颜色视觉差异的国际单位。数值越小颜色越接近。当 ΔE 小于 3.0 时，人眼极难分清两者的边界。</span>
                            </div>
                        </div>
                        {img_html}
                        <p class="text-[11px] text-slate-600 leading-relaxed mt-2">
                            算法在上述标注位置检测到极其接近的相邻颜色，将导致严重的组件辨识困难。
                        </p>
                    </div>
                    {melt_html}
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-slate-900 rounded-xl shadow-xl no-print" aria-label="智能修复工单">
            <div class="px-6 py-5 bg-slate-800 border-b border-slate-700 rounded-t-xl">
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
        html += f'''
            <div class="border border-slate-700 rounded-lg p-5 bg-slate-800/40">
                <div class="flex justify-between items-start mb-4">
                    <span class="text-[10px] font-black text-rose-400 uppercase tracking-widest">修复工单 #{idx+1}</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <p class="text-xs text-slate-400">当前方案 <span class="text-rose-300 font-mono">{orig_c}</span> 在 <span class="text-slate-500 font-mono">{bg_c}</span> 上对比度不达标。推荐以下替代色：</p>
        '''
        if pair.get('safe_palette_suggestion'):
            safe = pair['safe_palette_suggestion']
            html += f'''
                        <div class="bg-slate-800 p-3 rounded border border-slate-700">
                            <p class="text-[9px] text-indigo-400 font-bold uppercase mb-2 italic">🏆 首选：色盲安全色 (Okabe-Ito)</p>
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded border border-slate-600 shadow-inner" style="background-color: {safe['hex']}"></div>
                                <div><div class="text-xs font-bold text-white">{safe['name']}</div><div class="text-[10px] font-mono text-emerald-400">{safe['hex']}</div></div>
                            </div>
                        </div>
            '''
        auto_c = pair.get('suggestion', {}).get('hex', '')
        if auto_c:
            html += f'''
                        <div class="bg-slate-800 p-3 rounded border border-slate-700">
                            <p class="text-[9px] text-slate-400 font-bold uppercase mb-2">备选：算法亮度微调色</p>
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded border border-slate-600 shadow-inner" style="background-color: {auto_c}"></div>
                                <div class="text-[10px] font-mono text-indigo-400">{auto_c}</div>
                            </div>
                        </div>
            '''
        html += f'''
                    </div>
                </div>
            </div>
        '''
    if not failed_pairs:
        html += '<div class="text-emerald-400 text-sm">🎉 完美！色彩对比度全线通过测试，无需修复。</div>'
    html += '</div></section>'
    return html

def generate_cvd_section(analysis_data):
    cvd_analysis = analysis_data.get('cvd_analysis', {})
    orig_b64 = analysis_data.get('original_image_base64', '')

    cvd_meta = {
        "protanopia": {"desc": "红色盲", "pop": "男性发病率 ~1.0%", "detail": "难以区分红绿色，红色常看成暗褐色。"},
        "deuteranopia": {"desc": "绿色盲", "pop": "男性发病率 ~1.1%", "detail": "最常见，难以辨别红、绿、褐色。"},
        "tritanopia": {"desc": "蓝色盲", "pop": "极罕见 <0.01%", "detail": "难以区分蓝绿色及紫红色。"}
    }
    
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="色盲视觉模拟">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800">色觉障碍 (CVD) 视觉模拟对比</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-8">
    '''
    
    # 顶部原图 (跨越三列)
    if orig_b64:
        html += f'''
                <div class="col-span-1 md:col-span-3 mb-2">
                    <div class="flex justify-between items-center mb-3">
                        <h3 class="text-sm font-bold text-slate-800 border-l-4 border-indigo-500 pl-2">基准视图 (Original Design)</h3>
                        <span class="text-[10px] px-2 py-1 bg-slate-100 text-slate-500 rounded font-medium">普通正常视力</span>
                    </div>
                    <div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex justify-center p-2">
                        <img src="data:image/png;base64,{orig_b64}" class="w-full h-auto object-contain max-h-[500px]">
                    </div>
                </div>
        '''

    # 过滤掉名为 combined / 对比总图 的数据，渲染其他所有的单体异常模拟图
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'combined' in cvd_type.lower() or '对比' in cvd_data.get('name', ''):
            continue  # 精准跳过对比总图
            
        meta = cvd_meta.get(cvd_type.lower(), {"desc": cvd_data.get('name', cvd_type), "pop": "-", "detail": "色觉异常模拟"})
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="space-y-3">
                    <div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 p-1">
                        <img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto object-cover">
                    </div>
                    <div>
                        <div class="flex justify-between items-center">
                            <h3 class="text-sm font-bold text-slate-800">{meta['desc']} <span class="text-[10px] text-slate-400">({cvd_type})</span></h3>
                            <span class="text-[9px] px-1.5 py-0.5 bg-rose-50 border border-rose-100 text-rose-600 rounded">{meta['pop']}</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-1.5 leading-relaxed">{meta['detail']}</p>
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
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">APCA (WCAG 3.0 现代算法)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">下一代视觉算法。比传统对比度更准确地模拟了字体大小和深浅背景下的人眼知觉差异。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">Delta E (ΔE 色差单位)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">衡量两个颜色视觉差异的国际单位。ΔE 小于 3 时，普通人眼已极难分辨边界。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">色盲边缘消融 (CVD Boundary Melt)</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">极端缺陷。两颜色普通人看对比强烈，但色盲眼中色差 ΔE 会暴跌至 3 以下，导致组件边界完全消失。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">Okabe-Ito 色盲安全色板</h3>
                    <p class="text-[11px] text-indigo-900/70 leading-relaxed">科学论证的 8 色调色盘，能被所有人群（含红/绿色盲）毫无障碍地辨认。</p>
                </div>
            </div>
        </section>
    '''

if __name__ == '__main__':
    print("HTML Report Generator optimized with dynamic Region bounding boxes and CVD layout fixes.")