#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

Optimized for: Explanatory Tooltips for all professional terms, 
Data Source Traceability in Summary, and Printability.
"""

import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw

# 解除 PIL 长截图的安全限制，防止长网页报错
Image.MAX_IMAGE_PIXELS = None

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
        
        cx = (c1[0] + c2[0]) // 2
        cy = (c1[1] + c2[1]) // 2
        crop_box = (
            max(0, cx - 400),
            max(0, cy - 300),
            min(img.width, cx + 400),
            min(img.height, cy + 300)
        )
        img = img.crop(crop_box)
        img.thumbnail((600, 600))
        
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
        if 'total_issues' in similar: score -= min(20, similar['total_issues'] * 2)
        melt_issues = sum(1 for r in similar.get('similar_regions', []) if r.get('melt_risks'))
        if melt_issues > 0: score -= min(15, melt_issues * 3)
    return max(0, min(100, score))

def generate_html_report(analysis_data, output_path, threshold=5.0):
    overall_score = calculate_overall_score(analysis_data)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    score_color = "text-emerald-500" if overall_score >= 90 else "text-amber-500" if overall_score >= 70 else "text-rose-500"
    score_bg = "bg-emerald-500" if overall_score >= 90 else "bg-amber-500" if overall_score >= 70 else "bg-rose-500"
    
    stats = analysis_data.get('color_analysis', {}).get('statistics', {})
    apca_rate = stats.get('apca_pass_rate', 0) * 100
    ui_rate = stats.get('ui_component_pass_rate', 0) * 100

    # 公共的 Info Icon
    info_icon = '<svg class="w-4 h-4 text-slate-400 hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>无障碍审计报告 - {timestamp}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', sans-serif; scroll-behavior: smooth; }}
        .tooltip-container {{ position: relative; display: inline-flex; align-items: center; cursor: help; z-index: 50; }}
        .tooltip-container .tooltiptext {{
            visibility: hidden; width: 260px; background-color: #1e293b; color: #f8fafc;
            text-align: left; border-radius: 6px; padding: 12px; position: absolute;
            bottom: 135%; left: 50%; transform: translateX(-50%); opacity: 0;
            transition: opacity 0.2s, visibility 0.2s; font-size: 0.75rem; line-height: 1.5; font-weight: normal; text-transform: none; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); pointer-events: none;
        }}
        .tooltip-container .tooltiptext::after {{ content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #1e293b transparent transparent transparent; }}
        .tooltip-container:hover .tooltiptext {{ visibility: visible; opacity: 1; }}

        @media print {{
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            .no-print {{ display: none !important; }}
            body {{ background-color: white; }}
            .print-expanded {{ display: grid !important; }}
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
            <button onclick="window.print()" class="no-print text-xs px-3 py-1.5 bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700 transition-colors">打印报告 / PDF</button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12" role="main">
'''

    # ========================================================
    # 优化 1：系统包容性分析概览 - 加上完备的 Tooltip
    # ========================================================
    html_content += f'''
        <section id="overview" aria-label="诊断概览">
            <div class="mb-6 text-center">
                <h2 class="text-2xl font-bold text-slate-800">系统包容性分析概览</h2>
                <p class="text-sm text-slate-500 mt-1">评估设计稿在多样化视觉群体中的可读性与边界清晰度。</p>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-4 text-center flex flex-col justify-center">
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex justify-center items-center gap-1.5">
                        综合健康度总分
                        <div class="tooltip-container">{info_icon}<span class="tooltiptext">基础分 100 分，系统按对比度不达标率及高危色盲熔断区域数量进行加权惩罚扣分。</span></div>
                    </h3>
                    <div class="text-6xl font-bold {score_color} tracking-tighter mb-4">{overall_score}</div>
                    <div class="w-full bg-slate-100 rounded-full h-1.5 mb-3"><div class="{score_bg} h-1.5 rounded-full" style="width: {overall_score}%"></div></div>
                </div>
                <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                    <div class="flex flex-col justify-center">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                                APCA 视知觉合规率
                                <div class="tooltip-container">{info_icon}<span class="tooltiptext"><b>APCA (WCAG 3.0)：</b>下一代视网膜知觉算法。能精准测算深浅模式下“文字与背景”的真实阅读清晰度。普通文本建议通过。</span></div>
                            </span>
                            <span class="text-lg font-bold text-indigo-600">{apca_rate:.1f}%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-indigo-500 h-2 rounded-full" style="width: {apca_rate}%"></div></div>
                    </div>
                    <div class="flex flex-col justify-center border-t md:border-t-0 md:border-l border-slate-100 md:pl-8 pt-4 md:pt-0">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                                UI 控件边界清晰度
                                <div class="tooltip-container">{info_icon}<span class="tooltiptext"><b>非文本对比度：</b>用于评估界面上的按钮外框、输入框边缘、状态图标等 UI 控件能否被低视力用户清晰识别，安全阈值 3.0:1。</span></div>
                            </span>
                            <span class="text-lg font-bold text-sky-600">{ui_rate:.1f}%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
                    </div>
                </div>
            </div>
        </section>
'''

    if 'cvd_analysis' in analysis_data or 'original_image_base64' in analysis_data:
        html_content += generate_cvd_section(analysis_data)

    if 'grid_issues' in analysis_data:
        html_content += generate_grid_analysis_section(analysis_data['grid_issues'])

    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data)

    html_content += generate_recommendations_section(analysis_data)

    # 优化 2：带数据来源说明的终结结论
    html_content += generate_summary_section(overall_score, apca_rate, analysis_data)

    html_content += generate_glossary_section()

    html_content += '''
    </main>
    <div id="lightbox" class="fixed inset-0 z-[200] hidden bg-slate-900/90 backdrop-blur-sm flex items-center justify-center cursor-zoom-out opacity-0 transition-opacity duration-300 no-print">
        <img id="lightbox-img" src="" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl scale-95 transition-transform duration-300">
    </div>
    <script>
        function toggleGrid() {
            const content = document.getElementById('grid-content');
            const text = document.getElementById('grid-toggle-text');
            const icon = document.getElementById('grid-toggle-icon');
            if (content.classList.contains('hidden')) {
                content.classList.remove('hidden'); text.innerText = '收起异常网格'; icon.classList.add('rotate-180');
            } else {
                content.classList.add('hidden'); text.innerText = '展开异常网格'; icon.classList.remove('rotate-180');
            }
        }
        document.addEventListener('DOMContentLoaded', () => {
            const lightbox = document.getElementById('lightbox'); const lightboxImg = document.getElementById('lightbox-img');
            document.querySelectorAll('img').forEach(img => {
                img.classList.add('cursor-zoom-in');
                img.addEventListener('click', (e) => {
                    lightboxImg.src = e.target.src; lightbox.classList.remove('hidden');
                    setTimeout(() => { lightbox.classList.remove('opacity-0'); lightboxImg.classList.remove('scale-95'); lightboxImg.classList.add('scale-100'); }, 10);
                });
            });
            lightbox.addEventListener('click', () => {
                lightbox.classList.add('opacity-0'); lightboxImg.classList.remove('scale-100'); lightboxImg.classList.add('scale-95');
                setTimeout(() => { lightbox.classList.add('hidden'); lightboxImg.src = ''; }, 300);
            });
        });
    </script>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_grid_analysis_section(grid_issues):
    if not grid_issues: return ""
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl flex justify-between items-center cursor-pointer" onclick="toggleGrid()">
                <div><h2 class="font-bold text-slate-800 flex items-center gap-2">100×100 像素网格雷区定位</h2><p class="text-[11px] text-slate-500 mt-1">画面共发现 <b class="text-rose-500">{len(grid_issues)}</b> 个对比度过低的局部异常切片。</p></div>
                <div class="text-slate-500 no-print text-xs bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-sm flex items-center gap-1">
                    <span id="grid-toggle-text">展开异常网格</span> <svg id="grid-toggle-icon" class="w-4 h-4 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
            </div>
            <div id="grid-content" class="p-6 hidden print-expanded grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-3">
    '''
    for issue in grid_issues:
        html += f'''
                <div class="border border-rose-200 rounded-lg bg-rose-50/30 flex flex-col justify-between overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-zoom-in">
                    <div class="h-20 flex items-center justify-center p-1.5 border-b border-rose-100"><img src="data:image/jpeg;base64,{issue['image_base64']}" class="h-full w-full object-cover rounded-sm pointer-events-none"></div>
                    <div class="bg-white p-2 text-center flex-1 flex flex-col justify-center">
                        <div class="text-[8px] text-slate-400 font-mono truncate">{issue['coord']}</div>
                        <div class="mt-1 text-[10px] font-black text-rose-600">{issue['ratio']:.1f}:1</div>
                    </div>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_contrast_section(color_analysis):
    info_icon = '<svg class="w-3.5 h-3.5 text-slate-400 hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-visible">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-2">色彩矩阵压力测试 (Color Matrix Audit)</h2>
                <div class="bg-indigo-50 border border-indigo-100 p-3 rounded text-xs text-indigo-800">
                    <b>审计目的：</b> 算法会将核心色进行两两“交叉互切”，暴露出设计稿中所有潜在的色彩对比雷区。
                </div>
            </div>
            <table class="min-w-full divide-y divide-slate-200">
                <thead class="bg-slate-50/50">
                    <tr>
                        <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-400 uppercase">交叉颜色对 (前景/背景)</th>
                        
                        <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">
                            <div class="flex items-center justify-center gap-1">
                                WCAG 2.1
                                <div class="tooltip-container">{info_icon}<span class="tooltiptext"><b>经典无障碍国际标准。</b><br>要求普通文本对比度达到 4.5:1，大标题达到 3.0:1，否则将影响普通人群阅读。</span></div>
                            </div>
                        </th>
                        <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">
                            <div class="flex items-center justify-center gap-1">
                                APCA (Lc)
                                <div class="tooltip-container">{info_icon}<span class="tooltiptext"><b>下一代视觉感算标准。</b><br>分数单位为 Lc。普通文本要求绝对值大于 60。数值越高，文本的视觉对比越清晰。</span></div>
                            </div>
                        </th>
                        <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase">
                            <div class="flex items-center justify-center gap-1">
                                UI 控件安全
                                <div class="tooltip-container">{info_icon}<span class="tooltiptext"><b>非文本对比边界。</b><br>验证该色彩是否足以让“图标”或“组件边缘”在底色上被明确识别 (安全阈值 3.0:1)。</span></div>
                            </div>
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-slate-100">
    '''
    for pair in color_analysis.get('color_pairs', [])[:6]:
        m = pair.get('metrics', {})
        html += f'''
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3 font-mono text-[11px]">
                                    <div class="flex -space-x-2">
                                        <div class="w-6 h-6 rounded-full border-2 border-white" style="background-color: {pair['color1']['hex']}; z-index: 2;"></div>
                                        <div class="w-6 h-6 rounded-full border-2 border-white" style="background-color: {pair['color2']['hex']}; z-index: 1;"></div>
                                    </div>
                                    <span class="text-slate-600">{pair['color1']['hex']} / {pair['color2']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-center"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold {'bg-emerald-100 text-emerald-700' if m.get("aa_normal") else 'bg-rose-100 text-rose-700'}">{m.get("ratio", 0):.2f}:1</span></td>
                            <td class="px-6 py-4 text-center"><span class="text-[11px] font-bold { 'text-indigo-600' if m.get("apca_pass_normal") else 'text-slate-400' }">Lc {m.get("apca_lc", 0):.0f}</span></td>
                            <td class="px-6 py-4 text-center">{'✓' if m.get("ui_component") else '✗'}</td>
                        </tr>
        '''
    html += '</tbody></table></section>'
    return html

def generate_similar_regions_section(analysis_data):
    regions = analysis_data.get('similar_regions', {}).get('similar_regions', [])
    orig_b64 = analysis_data.get('original_image_base64')
    html = f'''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-visible">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800">视障边缘消融预警 (CVD Melt Detection)</h2>
                <p class="text-[11px] text-slate-500 mt-1">发现那些正常人看着清晰，但在色盲眼中彻底糊在一起的伪装边界。</p>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    for region in regions[:3]: 
        normal_de = region.get('delta_e', 0)
        cvd_de = region.get('worst_cvd_delta_e', normal_de)
        melt_risks = region.get('melt_risks', [])
        b1, b2 = region.get('region1_boundaries'), region.get('region2_boundaries')
        border_col, tag_bg, tag_text = ("border-purple-300", "bg-purple-100", "text-purple-700") if melt_risks else ("border-rose-200", "bg-rose-100", "text-rose-700")
        
        annotated_img_b64 = generate_annotated_thumbnail(orig_b64, b1, b2)
        img_html = f'<img src="data:image/jpeg;base64,{annotated_img_b64}" class="w-full h-32 object-cover rounded shadow-inner cursor-zoom-in">' if annotated_img_b64 else ""

        html += f'''
                <div class="border {border_col} rounded-lg p-5 bg-white shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-slate-600">{"🚨 色盲边缘消融" if melt_risks else "高危边界重叠"}</span>
                            <div class="tooltip-container">
                                <span class="px-2 py-0.5 rounded text-[10px] font-black {tag_bg} {tag_text}">常规 ΔE {normal_de:.1f}</span>
                                <span class="tooltiptext"><b>Delta E (ΔE)：</b>衡量两种颜色视觉差异。数值越小越接近。小于 3.0 则人眼极难分清边界。</span>
                            </div>
                        </div>
                        <div class="mt-2 mb-2 bg-slate-100 p-1 rounded border border-slate-200">{img_html}</div>
                        <p class="text-[11px] text-slate-600 leading-relaxed mt-2 text-center">上方标出的连线处存在显著的视觉辨识隐患</p>
                    </div>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    html = '''
        <section class="bg-slate-900 rounded-xl shadow-xl no-print">
            <div class="px-6 py-5 bg-slate-800 border-b border-slate-700 rounded-t-xl">
                <h2 class="text-white font-bold flex items-center gap-2">智能修复建议中心</h2>
                <p class="text-[11px] text-slate-400 mt-1">系统已针对不合格的色彩配对，计算出最优的替代色谱。</p>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    pairs = analysis_data.get('color_analysis', {}).get('color_pairs', [])
    failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
    for idx, pair in enumerate(failed_pairs[:6]):
        orig_c, bg_c = pair['color1']['hex'], pair['color2']['hex']
        html += f'''
            <div class="border border-slate-700 rounded-lg p-5 bg-slate-800/40 flex flex-col justify-between">
                <div><span class="text-[10px] font-black text-rose-400 uppercase mb-2 block">修复工单 #{idx+1}</span>
                <p class="text-[11px] text-slate-300 leading-relaxed mb-4">前景色 <span class="text-rose-300 font-mono">{orig_c}</span> 在底色 <span class="text-slate-500 font-mono">{bg_c}</span> 上不达标。</p></div>
        '''
        if pair.get('safe_palette_suggestion'):
            safe = pair['safe_palette_suggestion']
            html += f'''<div class="bg-slate-800 p-3 rounded border border-slate-700 mt-2"><p class="text-[9px] text-indigo-400 font-bold uppercase mb-2">🏆 首选方案</p><div class="flex items-center gap-3"><div class="w-8 h-8 rounded shadow-inner" style="background-color: {safe['hex']}"></div><div><div class="text-[11px] font-bold text-white">{safe['name']}</div><div class="text-[10px] font-mono text-emerald-400">{safe['hex']}</div></div></div></div>'''
        html += '</div>'
    if not failed_pairs:
        html += '<div class="text-emerald-400 text-sm">🎉 完美！色彩对比度全线通过测试，无需修复。</div>'
    html += '</div></section>'
    return html

def generate_cvd_section(analysis_data):
    cvd_analysis = analysis_data.get('cvd_analysis', {})
    orig_b64 = analysis_data.get('original_image_base64', '')
    cvd_meta = {
        "protanopia": {"desc": "红色盲", "pop": "男性发病率 ~1.0%", "detail": "难以区分红绿色。"},
        "deuteranopia": {"desc": "绿色盲", "pop": "男性发病率 ~1.1%", "detail": "最常见，难以辨别红、绿。"},
        "tritanopia": {"desc": "蓝色盲", "pop": "极罕见 <0.01%", "detail": "难以区分蓝绿色及紫红色。"}
    }
    html = '''<section class="bg-white rounded-xl border border-slate-200 shadow-sm"><div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl"><h2 class="font-bold text-slate-800">色觉障碍 (CVD) 视觉模拟对比</h2></div><div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-8">'''
    if orig_b64:
        html += f'''<div class="col-span-1 md:col-span-3 mb-2"><h3 class="text-sm font-bold text-slate-800 border-l-4 border-indigo-500 pl-2 mb-3">基准视图 (Original Design)</h3><div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex justify-center p-2 relative group"><img src="data:image/png;base64,{orig_b64}" class="w-full h-auto object-contain max-h-[500px] cursor-zoom-in"></div></div>'''
    for cvd_type, cvd_data in cvd_analysis.items():
        if 'combined' in cvd_type.lower() or '对比' in cvd_data.get('name', ''): continue 
        if 'image_base64' in cvd_data:
            html += f'''<div class="space-y-3"><div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 p-1 relative group"><img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto object-cover cursor-zoom-in"></div><h3 class="text-sm font-bold text-slate-800 text-center">{cvd_data.get('name', cvd_type)}</h3></div>'''
    html += '</div></section>'
    return html

def generate_summary_section(score, apca, analysis_data):
    verdict = "建议优化" if score < 90 else "表现优秀"
    verdict_color = "text-amber-400" if score < 90 else "text-emerald-400"
    border_color = "border-amber-500/30" if score < 90 else "border-emerald-500/30"
    
    issues_count = len(analysis_data.get('similar_regions', {}).get('similar_regions', []))
    pairs_count = len([p for p in analysis_data.get('color_analysis', {}).get('color_pairs', []) if not p['metrics'].get('aa_normal')])
    
    # 动态添加合理建议
    sugs = []
    if apca < 90: sugs.append("<b>提升文本清晰度：</b>排查低 APCA 的文字颜色，优先采用系统推荐的 Okabe-Ito 替代色。")
    if issues_count > 0: sugs.append("<b>阻断边界消融：</b>画面中存在视障边缘熔断点，请加大相邻组件的明度差，或添加实体描边。")
    if pairs_count > 0: sugs.append("<b>清理高危工单：</b>参考「智能修复建议中心」，落实核心 CSS 变量的色彩替换。")
    if score < 90: sugs.append("<b>全局对比度排查：</b>建议团队在下一次迭代时，引入 WCAG 2.1 AA 规范作为发版硬性标准。")
    if not sugs: sugs.append("<b>维持当前规范：</b>设计包容性极佳，建议将核心色彩组合沉淀至企业 Design System 中。")
    
    sug_html = "".join([f'<li class="flex items-start gap-2 before:content-[\'👉\'] before:shrink-0"><span>{s}</span></li>' for s in sugs])

    # 优化 2：总结板块带上数据出处说明，增强权威性
    return f'''
        <section class="bg-slate-900 rounded-2xl p-8 text-white relative overflow-hidden shadow-xl" aria-label="审计终审结论">
            <div class="relative z-10">
                <h2 class="text-2xl font-bold mb-6 flex items-center gap-2"><span class="w-1.5 h-6 bg-indigo-500 rounded-full"></span>审计终审结论 (Audit Verdict)</h2>
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    <div class="lg:col-span-8">
                        <p class="text-slate-300 text-base leading-relaxed mb-6 bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                            基于评估，本系统测算界面综合包容性健康度为 <b class="text-4xl {verdict_color} mx-1">{score}</b> 分，整体状态判定为：<b class="{verdict_color} text-2xl mx-1">{verdict}</b>。
                        </p>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-2">
                            <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 flex flex-col h-full">
                                <h4 class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">关键指标汇总</h4>
                                <ul class="space-y-4 text-sm text-slate-300 flex-1 flex flex-col justify-center">
                                    <li class="flex justify-between items-center border-b border-slate-700/50 pb-3"><span class="whitespace-nowrap">✅ APCA 合规率</span><span class="text-3xl font-black text-white pl-4">{apca:.1f}%</span></li>
                                    <li class="flex justify-between items-center border-b border-slate-700/50 pb-3"><span class="whitespace-nowrap">⚠️ 高危熔断点</span><span class="text-3xl font-black text-amber-400 pl-4">{issues_count}</span></li>
                                    <li class="flex justify-between items-center"><span class="whitespace-nowrap">🔧 待处理工单</span><span class="text-3xl font-black text-rose-400 pl-4">{pairs_count}</span></li>
                                </ul>
                                
                                <div class="mt-5 pt-4 border-t border-slate-700/50 text-[9px] text-slate-400 leading-relaxed space-y-1.5 bg-slate-900/40 p-3 rounded text-left">
                                    <b class="text-slate-300 block mb-1">📊 指标数据溯源说明：</b>
                                    <p>• <b>总分：</b>基础满分 100，根据各项不达标率及高危区域数进行扣分衰减得来。</p>
                                    <p>• <b>APCA率：</b>基于提取的 Top 15 主题色作矩阵交叉比对，满足 Lc 标准阈值的比例。</p>
                                    <p>• <b>熔断点：</b>基于机器视觉提取出的相邻色块，在色盲视界下运算出 ΔE < 3.0 的区域总数。</p>
                                    <p>• <b>工单数：</b>未能通过传统 WCAG 2.1 AA 级基础测试的交叉颜色对总计。</p>
                                </div>
                            </div>
                            <div class="bg-indigo-900/20 p-5 rounded-xl border border-indigo-500/30 flex flex-col h-full">
                                <h4 class="text-indigo-300 text-xs font-bold uppercase tracking-widest mb-4">下一步行动建议</h4>
                                <ul class="space-y-4 text-sm text-indigo-100/80 leading-relaxed flex-1">{sug_html}</ul>
                            </div>
                        </div>
                    </div>
                    <div class="lg:col-span-4 flex justify-center items-center">
                        <div class="border-[6px] {border_color} px-8 py-4 rounded-2xl rotate-[10deg] opacity-90 select-none shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                            <span class="text-5xl font-black uppercase tracking-tighter {verdict_color} drop-shadow-md">{verdict}</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    '''

def generate_glossary_section():
    return '''<section class="bg-indigo-50/50 rounded-xl border border-indigo-100 p-8 no-print"><h2 class="text-sm font-bold text-indigo-900 uppercase tracking-widest mb-6">术语速查手册 (Glossary)</h2><div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6"><div><h3 class="text-xs font-bold text-indigo-700 mb-1">APCA (WCAG 3.0 现代算法)</h3><p class="text-[11px] text-indigo-900/70">下一代视觉算法。比传统对比度更准确地模拟了字体大小和深浅背景下的人眼知觉差异。</p></div><div><h3 class="text-xs font-bold text-indigo-700 mb-1">CVD Boundary Melt</h3><p class="text-[11px] text-indigo-900/70">极端缺陷。两颜色普通人看对比强烈，但色盲眼中色差会暴跌，导致组件边界完全消失。</p></div></div></section>'''

if __name__ == '__main__':
    print("HTML Report Generator updated with Tooltips and Summary Data Sources.")