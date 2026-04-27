#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

Optimized for: Smart Component ROI Audit, Expanded Recommendations, 
Deep CVD Melt Insights, and Printability.
"""

import base64
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw

def image_to_base64(image, format='PNG'):
    buffered = BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format=format, quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_annotated_thumbnail(img_base64, b1, b2):
    if not img_base64 or not b1 or not b2: return None
    try:
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data)).convert('RGBA')
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        c1, c2 = (b1['center_x'], b1['center_y']), (b2['center_x'], b2['center_y'])
        draw.line([c1, c2], fill=(234, 179, 8, 200), width=4)
        
        r = 16 
        draw.ellipse([c1[0]-r, c1[1]-r, c1[0]+r, c1[1]+r], outline=(239, 68, 68, 255), width=4)
        draw.ellipse([c1[0]-4, c1[1]-4, c1[0]+4, c1[1]+4], fill=(239, 68, 68, 255))
        
        draw.ellipse([c2[0]-r, c2[1]-r, c2[0]+r, c2[1]+r], outline=(234, 179, 8, 255), width=4)
        draw.ellipse([c2[0]-4, c2[1]-4, c2[0]+4, c2[1]+4], fill=(234, 179, 8, 255))
        
        img = Image.alpha_composite(img, overlay).convert('RGB')
        img.thumbnail((600, 600))
        return image_to_base64(img, format='JPEG')
    except Exception: return None

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
        .tooltip-container {{ position: relative; display: inline-flex; align-items: center; cursor: help; z-index: 50; }}
        .tooltip-container .tooltiptext {{
            visibility: hidden; width: 260px; background-color: #1e293b; color: #f8fafc;
            text-align: left; border-radius: 6px; padding: 12px; position: absolute;
            bottom: 125%; left: 50%; transform: translateX(-50%); opacity: 0;
            transition: opacity 0.2s, visibility 0.2s; font-size: 0.75rem; line-height: 1.5; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
            pointer-events: none;
        }}
        .tooltip-container .tooltiptext::after {{ content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #1e293b transparent transparent transparent; }}
        .tooltip-container:hover .tooltiptext {{ visibility: visible; opacity: 1; }}
        @media print {{ * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} .no-print {{ display: none !important; }} body {{ background-color: white; }} }}
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
            <button onclick="window.print()" class="no-print text-xs px-3 py-1.5 bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-2">打印报告 / PDF</button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8" role="main">
'''

    html_content += f'''
        <div class="mb-2">
            <h2 class="text-2xl font-bold text-slate-800">系统包容性分析概览</h2>
            <p class="text-sm text-slate-500 mt-1">评估设计稿在多样化视觉群体（如色弱、低视力、不同光照环境）中的可读性与边界清晰度。</p>
        </div>

        <section class="grid grid-cols-1 lg:grid-cols-12 gap-6" aria-label="诊断概览">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-4 text-center flex flex-col justify-center">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">综合健康度总分</h3>
                <div class="text-6xl font-bold {score_color} tracking-tighter mb-4">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 mb-3"><div class="{score_bg} h-1.5 rounded-full" style="width: {overall_score}%"></div></div>
                <p class="text-[11px] text-slate-500">基于以下两大核心维度加权计算</p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                <div class="flex flex-col justify-center">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                            维度一：APCA 视知觉合规率
                            <div class="tooltip-container"><svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg><span class="tooltiptext">APCA 是 WCAG 3.0 的下一代算法，基于人类视网膜模型，能极其精准地测算“文字与背景”的真实阅读清晰度。</span></div>
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
                            <div class="tooltip-container"><svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg><span class="tooltiptext">确保界面上的按钮轮廓、输入框边缘等“非文字组件”能够被低视力用户清晰识别。</span></div>
                        </span>
                        <span class="text-lg font-bold text-sky-600">{ui_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
                    <p class="text-[10px] text-slate-400">关注对象：按钮、Icon、图形与分割线</p>
                </div>
            </div>
        </section>
'''

    # ========================================================
    # 新增模块：方案 A - UI 组件微观切割审查
    # ========================================================
    if 'component_rois' in analysis_data and analysis_data['component_rois']:
        html_content += generate_component_roi_section(analysis_data['component_rois'])

    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data)

    html_content += generate_recommendations_section(analysis_data)

    if 'cvd_analysis' in analysis_data or 'original_image_base64' in analysis_data:
        html_content += generate_cvd_section(analysis_data)

    html_content += generate_glossary_section()

    html_content += '''
    </main>
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 mt-8 border-t border-slate-200 text-center text-xs text-slate-400 no-print"><p>无障碍色彩审计系统 · 强驱动版本</p></footer>

    <div id="lightbox" class="fixed inset-0 z-[200] hidden bg-slate-900/90 backdrop-blur-sm flex items-center justify-center cursor-zoom-out opacity-0 transition-opacity duration-300 no-print">
        <img id="lightbox-img" src="" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl scale-95 transition-transform duration-300">
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const lightbox = document.getElementById('lightbox'); const lightboxImg = document.getElementById('lightbox-img');
            document.querySelectorAll('img').forEach(img => {
                img.classList.add('cursor-zoom-in');
                img.addEventListener('click', (e) => { lightboxImg.src = e.target.src; lightbox.classList.remove('hidden'); setTimeout(() => { lightbox.classList.remove('opacity-0'); lightboxImg.classList.remove('scale-95'); lightboxImg.classList.add('scale-100'); }, 10); });
            });
            lightbox.addEventListener('click', () => { lightbox.classList.add('opacity-0'); lightboxImg.classList.remove('scale-100'); lightboxImg.classList.add('scale-95'); setTimeout(() => { lightbox.classList.add('hidden'); lightboxImg.src = ''; }, 300); });
        });
    </script>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_component_roi_section(rois):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="UI 组件切割分析">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-1 flex items-center gap-2">
                    <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"></path></svg>
                    智能组件微观切割审查 (Smart ROI Audit)
                </h2>
                <p class="text-[11px] text-slate-500">通过机器视觉(CV)边缘检测算法，自动从原图中剥离出核心 UI 组件（如按钮、卡片、输入框），并进行独立审视。</p>
            </div>
            <div class="p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
    '''
    for i, roi in enumerate(rois[:4]):
        html += f'''
                <div class="border border-slate-200 rounded-lg bg-slate-50 flex flex-col justify-between overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                    <div class="h-28 flex items-center justify-center p-4 relative group">
                        <img src="data:image/jpeg;base64,{roi['image_base64']}" class="max-h-full max-w-full object-contain drop-shadow-sm">
                        <div class="absolute top-2 left-2 text-[9px] font-mono bg-slate-900/60 text-white px-1.5 py-0.5 rounded backdrop-blur">ROI #{i+1}</div>
                    </div>
                    <div class="bg-white p-3 border-t border-slate-100 text-center">
                        <div class="text-[10px] text-slate-400 font-mono">尺寸: {roi['width']}x{roi['height']} px</div>
                        <div class="mt-1 text-[10px] font-bold text-slate-600">组件孤立提取成功</div>
                    </div>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_contrast_section(color_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="色彩矩阵审计">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-2">色彩矩阵压力测试 (Color Matrix Audit)</h2>
                <div class="bg-indigo-50 border border-indigo-100 p-3 rounded text-xs text-indigo-800 leading-relaxed">
                    <b>工作原理：</b> 算法对整个界面进行高频采样，聚类提取最具代表性的 Top 15 主题色进行两两“交叉互切”。
                </div>
            </div>
            <div class="overflow-visible">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50/50">
                        <tr>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-400 uppercase">交叉颜色对 (前景/背景)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">WCAG 2.1 传统对比</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">APCA (Lc)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">UI 控件安全</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100 rounded-b-xl">
    '''
    for pair in color_analysis.get('color_pairs', [])[:6]:
        m = pair.get('metrics', {})
        html += f'''
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3 font-mono text-[11px]">
                                    <div class="flex -space-x-2">
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color1']['hex']}; z-index: 2;"></div>
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color2']['hex']}; z-index: 1;"></div>
                                    </div>
                                    <span class="text-slate-600">{pair['color1']['hex']}</span> <span class="text-slate-300">/</span> <span class="text-slate-600">{pair['color2']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-center"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold {'bg-emerald-100 text-emerald-700' if m.get("aa_normal") else 'bg-rose-100 text-rose-700'}">{m.get("ratio", 0):.2f}:1</span></td>
                            <td class="px-6 py-4 text-center"><span class="text-[11px] font-bold { 'text-indigo-600' if m.get("apca_pass_normal") else 'text-slate-400' }">Lc {m.get("apca_lc", 0):.0f}</span></td>
                            <td class="px-6 py-4 text-center">{'<span class="text-emerald-500">✓ 通过</span>' if m.get("ui_component") else '<span class="text-rose-400">✗ 隐患</span>'}</td>
                        </tr>
        '''
    html += '</tbody></table></div></section>'
    return html

def generate_similar_regions_section(analysis_data):
    regions = analysis_data.get('similar_regions', {}).get('similar_regions', [])
    orig_b64 = analysis_data.get('original_image_base64')

    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="相邻色块检测">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 flex items-center gap-2">视障边缘消融预警 (CVD Melt Detection)</h2>
                <p class="text-[11px] text-slate-500 mt-1">发现那些正常人看着清晰，但在色盲眼中彻底糊在一起的伪装边界。</p>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    
    # 扩容与深度分析：数量从 3 提升到 6
    for region in regions[:6]: 
        normal_de, cvd_de = region.get('delta_e', 0), region.get('worst_cvd_delta_e', region.get('delta_e', 0))
        melt_risks = region.get('melt_risks', [])
        b1, b2 = region.get('region1_boundaries'), region.get('region2_boundaries')

        if melt_risks:
            border_color, title, bg_col = "border-purple-300", "🚨 极高危：边缘消融", "bg-purple-50"
            advice = "明度差严重不足，导致色相丢失后融为一体。<b>强烈建议：加深其中一方的明度至少 20%，或增加 1px 的边框区隔。</b>"
        else:
            border_color, title, bg_col = "border-rose-200", "高危边界重叠", "bg-rose-50"
            advice = "基础色彩差异过小。<b>建议：加大两种颜色的对比度，避免视觉连片。</b>"

        melt_html = ""
        if melt_risks:
            melt_html = f'<div class="mt-2 p-2 {bg_col} border border-purple-100 rounded shadow-sm"><p class="text-[10px] text-purple-800 font-medium">在 <b>{", ".join([m.split()[0] for m in melt_risks])}</b> 眼中，色差暴跌至 ΔE {cvd_de:.1f}。</p></div>'

        annotated_img_b64 = generate_annotated_thumbnail(orig_b64, b1, b2)
        img_html = f'<div class="mt-3 mb-2 bg-slate-100 p-1 rounded border border-slate-200 group relative"><img src="data:image/jpeg;base64,{annotated_img_b64}" class="w-full h-32 object-cover rounded shadow-inner"></div>' if annotated_img_b64 else ""

        html += f'''
                <div class="border {border_color} rounded-lg p-5 bg-white shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-bold text-slate-600">{title}</span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-black bg-slate-100 text-slate-500">正常 ΔE {normal_de:.1f}</span>
                        </div>
                        {img_html}
                        {melt_html}
                        <div class="mt-3 text-[10px] text-slate-600 border-t border-slate-100 pt-2 leading-relaxed">
                            💡 <b>设计建议：</b> {advice}
                        </div>
                    </div>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-slate-900 rounded-xl shadow-xl no-print" aria-label="智能修复工单">
            <div class="px-6 py-5 bg-slate-800 border-b border-slate-700 rounded-t-xl">
                <h2 class="text-white font-bold flex items-center gap-2"><span class="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>智能修复建议中心</h2>
                <p class="text-[11px] text-slate-400 mt-1">系统已针对不合格的色彩配对，计算出最优的替代色谱。</p>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    pairs = analysis_data.get('color_analysis', {}).get('color_pairs', [])
    failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
    
    # 扩容与深度分析：数量从 3 提升到 6
    for idx, pair in enumerate(failed_pairs[:6]):
        orig_c, bg_c = pair['color1']['hex'], pair['color2']['hex']
        ratio = pair['metrics'].get('ratio', 0)
        
        # 深度诊断文本
        if ratio < 2.0:
            diag = "对比度极度匮乏，导致文本/图标在背景上几乎隐形。"
        else:
            diag = "对比度处于危险边缘，低视力用户在户外阳光下无法阅读。"

        html += f'''
            <div class="border border-slate-700 rounded-lg p-5 bg-slate-800/40 flex flex-col justify-between">
                <div>
                    <span class="text-[10px] font-black text-rose-400 uppercase tracking-widest mb-2 block">修复工单 #{idx+1}</span>
                    <p class="text-[11px] text-slate-300 leading-relaxed mb-4">
                        前景色 <span class="text-rose-300 font-mono">{orig_c}</span> 在底色 <span class="text-slate-500 font-mono">{bg_c}</span> 上不达标。
                        <br><span class="text-slate-400 mt-1 block"><b>深度诊断：</b>{diag}</span>
                    </p>
                </div>
        '''
        if pair.get('safe_palette_suggestion'):
            safe = pair['safe_palette_suggestion']
            html += f'''
                <div class="bg-slate-800 p-3 rounded border border-slate-700 mt-2">
                    <p class="text-[9px] text-indigo-400 font-bold uppercase mb-2">🏆 推荐：色盲安全色</p>
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded shadow-inner" style="background-color: {safe['hex']}"></div>
                        <div><div class="text-[11px] font-bold text-white">{safe['name']}</div><div class="text-[10px] font-mono text-emerald-400">{safe['hex']}</div></div>
                    </div>
                </div>
            '''
        elif pair.get('suggestion'):
            auto_c = pair['suggestion']['hex']
            html += f'''
                <div class="bg-slate-800 p-3 rounded border border-slate-700 mt-2">
                    <p class="text-[9px] text-slate-400 font-bold uppercase mb-2">备选：明度微调色</p>
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded shadow-inner" style="background-color: {auto_c}"></div>
                        <div class="text-[10px] font-mono text-indigo-400">{auto_c}</div>
                    </div>
                </div>
            '''
        html += '</div>'
        
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
    
    html = '''<section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="色盲视觉模拟"><div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl"><h2 class="font-bold text-slate-800">色觉障碍 (CVD) 视觉模拟对比</h2></div><div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-8">'''
    if orig_b64:
        html += f'''<div class="col-span-1 md:col-span-3 mb-2"><div class="flex justify-between items-center mb-3"><h3 class="text-sm font-bold text-slate-800 border-l-4 border-indigo-500 pl-2">基准视图 (Original Design)</h3></div><div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex justify-center p-2"><img src="data:image/png;base64,{orig_b64}" class="w-full h-auto object-contain max-h-[500px]"></div></div>'''
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'combined' in cvd_type.lower() or '对比' in cvd_data.get('name', ''): continue 
        meta = cvd_meta.get(cvd_type.lower(), {"desc": cvd_data.get('name', cvd_type), "pop": "-", "detail": "色觉异常模拟"})
        if 'image_base64' in cvd_data:
            html += f'''<div class="space-y-3"><div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 p-1"><img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto object-cover"></div><div><div class="flex justify-between items-center"><h3 class="text-sm font-bold text-slate-800">{meta['desc']}</h3><span class="text-[9px] px-1.5 py-0.5 bg-rose-50 border border-rose-100 text-rose-600 rounded">{meta['pop']}</span></div><p class="text-[11px] text-slate-500 mt-1.5 leading-relaxed">{meta['detail']}</p></div></div>'''
    html += '</div></section>'
    return html

def generate_glossary_section():
    return '''<section class="bg-indigo-50/50 rounded-xl border border-indigo-100 p-8 no-print"><h2 class="text-sm font-bold text-indigo-900 uppercase tracking-widest mb-6">术语速查手册 (Glossary)</h2><div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6"><div><h3 class="text-xs font-bold text-indigo-700 mb-1">APCA (WCAG 3.0 现代算法)</h3><p class="text-[11px] text-indigo-900/70">下一代视觉算法。比传统对比度更准确地模拟了字体大小和深浅背景下的人眼知觉差异。</p></div><div><h3 class="text-xs font-bold text-indigo-700 mb-1">Delta E (ΔE 色差单位)</h3><p class="text-[11px] text-indigo-900/70">衡量两个颜色视觉差异的国际单位。ΔE 小于 3 时，普通人眼已极难分辨边界。</p></div></div></section>'''