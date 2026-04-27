#!/usr/bin/env python3
"""
HTML Report Generator for wuzhangaishijueceshi skill.

Optimized for: Actionable In-Context Fixes, Global Palette Analysis, 
Printability, and Deep Professional Insights.
"""

import base64
import json
import math
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw

def image_to_base64(image, format='PNG'):
    buffered = BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format=format, quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 画框与连线（靶心定位）
def generate_annotated_thumbnail(img_base64, b1, b2):
    if not img_base64 or not b1 or not b2:
        return None
    try:
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data)).convert('RGBA')
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        c1 = (b1['center_x'], b1['center_y'])
        c2 = (b2['center_x'], b2['center_y'])
        
        draw.line([c1, c2], fill=(234, 179, 8, 200), width=4)
        
        r = 16 
        draw.ellipse([c1[0]-r, c1[1]-r, c1[0]+r, c1[1]+r], outline=(239, 68, 68, 255), width=4)
        draw.ellipse([c1[0]-4, c1[1]-4, c1[0]+4, c1[1]+4], fill=(239, 68, 68, 255))
        
        draw.ellipse([c2[0]-r, c2[1]-r, c2[0]+r, c2[1]+r], outline=(234, 179, 8, 255), width=4)
        draw.ellipse([c2[0]-4, c2[1]-4, c2[0]+4, c2[1]+4], fill=(234, 179, 8, 255))
        
        img = Image.alpha_composite(img, overlay).convert('RGB')
        img.thumbnail((600, 600))
        return image_to_base64(img, format='JPEG')
    except Exception as e:
        return None

def calculate_relative_luminance(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

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
    <title>深度色彩资产审计报告 - {timestamp}</title>
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
        .tooltip-container .tooltiptext::after {{
            content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px;
            border-width: 5px; border-style: solid; border-color: #1e293b transparent transparent transparent;
        }}
        .tooltip-container:hover .tooltiptext {{ visibility: visible; opacity: 1; }}

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
                <h1 class="text-lg font-semibold text-white">深度色彩资产审计报告</h1>
            </div>
            <button onclick="window.print()" class="no-print text-xs px-3 py-1.5 bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-2">
                打印报告 / PDF
            </button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8" role="main">
'''

    # --- 概览仪表盘 ---
    html_content += f'''
        <section class="grid grid-cols-1 lg:grid-cols-12 gap-6" aria-label="诊断概览">
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-4 text-center flex flex-col justify-center">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">综合健康度总分</h3>
                <div class="text-6xl font-bold {score_color} tracking-tighter mb-4">{overall_score}</div>
                <div class="w-full bg-slate-100 rounded-full h-1.5 mb-3">
                    <div class="{score_bg} h-1.5 rounded-full" style="width: {overall_score}%"></div>
                </div>
            </div>
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm col-span-1 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                <div class="flex flex-col justify-center">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-semibold text-slate-700">维度一：APCA 视知觉合规率</span>
                        <span class="text-lg font-bold text-indigo-600">{apca_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-indigo-500 h-2 rounded-full" style="width: {apca_rate}%"></div></div>
                </div>
                <div class="flex flex-col justify-center border-t md:border-t-0 md:border-l border-slate-100 md:pl-8 pt-4 md:pt-0">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-semibold text-slate-700">维度二：UI 控件边界清晰度</span>
                        <span class="text-lg font-bold text-sky-600">{ui_rate:.1f}%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 mb-2"><div class="bg-sky-500 h-2 rounded-full" style="width: {ui_rate}%"></div></div>
                </div>
            </div>
        </section>
'''

    # ========================================================
    # 新增深度内容 1：全局色彩资产诊断 (Macro Palette Health)
    # ========================================================
    if 'color_analysis' in analysis_data and 'dominant_colors' in analysis_data['color_analysis']:
        html_content += generate_palette_health_section(analysis_data['color_analysis']['dominant_colors'])

    # ========================================================
    # 深度升级 2：带有内联解决方案的色彩矩阵
    # ========================================================
    if 'color_analysis' in analysis_data:
        html_content += generate_contrast_section(analysis_data['color_analysis'])

    if 'similar_regions' in analysis_data:
        html_content += generate_similar_regions_section(analysis_data)

    html_content += generate_recommendations_section(analysis_data)

    if 'cvd_analysis' in analysis_data or 'original_image_base64' in analysis_data:
        html_content += generate_cvd_section(analysis_data)

    html_content += generate_glossary_section()

    # Lightbox 代码
    html_content += '''
    </main>
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 mt-8 border-t border-slate-200 text-center text-xs text-slate-400 no-print">
        <p>无障碍色彩审计系统 · 企业级版本</p>
    </footer>

    <div id="lightbox" class="fixed inset-0 z-[200] hidden bg-slate-900/90 backdrop-blur-sm flex items-center justify-center cursor-zoom-out opacity-0 transition-opacity duration-300 no-print">
        <img id="lightbox-img" src="" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl scale-95 transition-transform duration-300">
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            document.querySelectorAll('img').forEach(img => {
                img.classList.add('cursor-zoom-in');
                img.addEventListener('click', (e) => {
                    lightboxImg.src = e.target.src;
                    lightbox.classList.remove('hidden');
                    setTimeout(() => {
                        lightbox.classList.remove('opacity-0');
                        lightboxImg.classList.remove('scale-95');
                        lightboxImg.classList.add('scale-100');
                    }, 10);
                });
            });
            lightbox.addEventListener('click', () => {
                lightbox.classList.add('opacity-0');
                lightboxImg.classList.remove('scale-100');
                lightboxImg.classList.add('scale-95');
                setTimeout(() => { lightbox.classList.add('hidden'); lightboxImg.src = ''; }, 300);
            });
        });
    </script>
</body>
</html>
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


# --- 深度核心：全局色彩资产健康度 ---
def generate_palette_health_section(dominant_colors):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="全局色彩资产诊断">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-1">🎨 全局色彩资产诊断 (Global Palette Health)</h2>
                <p class="text-[11px] text-slate-500">
                    宏观分析：从 UI 中提取出核心主色调，并进行“基因级”体检。评估这些品牌色自身是否具备良好的通用适应性。
                </p>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
    '''
    
    # 取前 6 个出现频率最高的主色进行深入分析
    for color in dominant_colors[:6]:
        hex_val = color['hex']
        rgb = color['rgb']
        lum = calculate_relative_luminance(rgb)
        
        # 评判基因：过亮或过暗都会限制使用场景
        if 0.15 < lum < 0.6:
            badge = '<span class="px-1.5 py-0.5 bg-rose-50 text-rose-600 text-[9px] rounded border border-rose-200">仅限纯装饰用途</span>'
            desc = "中等亮度，作为文字时既不适配白底，也不适配黑底，非常危险。"
        elif lum > 0.6:
            badge = '<span class="px-1.5 py-0.5 bg-amber-50 text-amber-600 text-[9px] rounded border border-amber-200">适合深色模式文本</span>'
            desc = "高亮度，严禁在白底或浅色背景上将其用作正文颜色。"
        else:
            badge = '<span class="px-1.5 py-0.5 bg-emerald-50 text-emerald-600 text-[9px] rounded border border-emerald-200">高通用性文本色</span>'
            desc = "低亮度，对比度极佳，可安全地在各类浅色背景上用作标题或正文。"

        text_color = "#ffffff" if lum < 0.5 else "#1e293b"

        html += f'''
                    <div class="flex flex-col border border-slate-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                        <div class="h-24 w-full flex items-center justify-center relative" style="background-color: {hex_val}">
                            <span class="font-mono text-sm font-bold tracking-wider" style="color: {text_color}">{hex_val}</span>
                        </div>
                        <div class="p-3 bg-white flex-1 flex flex-col justify-between">
                            <div class="mb-2">{badge}</div>
                            <p class="text-[9px] text-slate-500 leading-relaxed">{desc}</p>
                        </div>
                    </div>
        '''
    html += '''
                </div>
            </div>
        </section>
    '''
    return html

# --- 深度核心：内联修复色彩矩阵 ---
def generate_contrast_section(color_analysis):
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm" aria-label="色彩矩阵审计">
            <div class="px-6 py-5 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800 text-base mb-2">色彩矩阵压力测试 (Color Matrix Audit)</h2>
                <div class="bg-indigo-50 border border-indigo-100 p-3 rounded text-xs text-indigo-800 leading-relaxed flex items-start gap-2">
                    <svg class="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <div>
                        <b>工作原理：</b> 将高频色彩进行全排列组合，模拟“前景文字+背景底色”的应用场景。<br>
                        <b>闭环支持：</b> 遇到不合规的致命组合，系统会<b>直接在右侧列出修复后的色值</b>，无需跳转，即刻可用。
                    </div>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50/50">
                        <tr>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-400 uppercase tracking-widest">问题对 (前景/背景)</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">WCAG 2.1 比例</th>
                            <th class="px-6 py-3 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">严重等级</th>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-slate-600 uppercase tracking-widest bg-emerald-50 border-l border-emerald-100">✨ 智能内联修正方案</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-100 rounded-b-xl">
    '''
    pairs = color_analysis.get('color_pairs', [])
    for pair in pairs[:8]:
        m = pair.get('metrics', {})
        wcag_pass = m.get("aa_normal")
        ratio = m.get("ratio", 0)
        
        # 严重程度分级 (Severity Badges)
        if ratio >= 4.5:
            severity = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700">Pass (安全)</span>'
        elif ratio >= 3.0:
            severity = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700">Warning (轻微警告)</span>'
        else:
            severity = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700">Critical (致命盲区)</span>'

        # ========================================================
        # 核心逻辑：在表格直接提供所见即所得的解决方案
        # ========================================================
        fix_html = '<span class="text-slate-400 text-xs italic">当前对比度良好，无需修改</span>'
        if not wcag_pass:
            if pair.get('safe_palette_suggestion'):
                safe_c = pair['safe_palette_suggestion']['hex']
                fix_html = f'''
                    <div class="flex items-center gap-2">
                        <div class="w-4 h-4 rounded-full border border-slate-200 shadow-sm" style="background-color: {safe_c}"></div>
                        <span class="text-xs font-mono font-bold text-emerald-600">替换为 {safe_c}</span>
                        <span class="text-[9px] bg-slate-100 text-slate-500 px-1 py-0.5 rounded">Okabe-Ito 标准</span>
                    </div>
                '''
            elif pair.get('suggestion'):
                auto_c = pair['suggestion']['hex']
                fix_html = f'''
                    <div class="flex items-center gap-2">
                        <div class="w-4 h-4 rounded-full border border-slate-200 shadow-sm" style="background-color: {auto_c}"></div>
                        <span class="text-xs font-mono font-bold text-indigo-600">提亮至 {auto_c}</span>
                        <span class="text-[9px] bg-slate-100 text-slate-500 px-1 py-0.5 rounded">HSL 微调</span>
                    </div>
                '''

        html += f'''
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3 font-mono text-[11px]">
                                    <div class="flex -space-x-2">
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color1']['hex']}; z-index: 2;"></div>
                                        <div class="w-6 h-6 rounded-full border-2 border-white shadow-sm" style="background-color: {pair['color2']['hex']}; z-index: 1;"></div>
                                    </div>
                                    <span class="text-slate-700 font-bold">{pair['color1']['hex']}</span>
                                    <span class="text-slate-300">on</span>
                                    <span class="text-slate-500">{pair['color2']['hex']}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="text-xs font-bold text-slate-800">{ratio:.2f} : 1</span>
                            </td>
                            <td class="px-6 py-4 text-center">{severity}</td>
                            <td class="px-6 py-4 bg-emerald-50/30 border-l border-emerald-50">{fix_html}</td>
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
                </h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    '''
    
    for region in regions[:3]: 
        normal_de = region.get('delta_e', 0)
        cvd_de = region.get('worst_cvd_delta_e', normal_de)
        melt_risks = region.get('melt_risks', [])
        b1, b2 = region.get('region1_boundaries'), region.get('region2_boundaries')

        border_color = "border-purple-300" if melt_risks else "border-rose-200"
        title = "🚨 色盲边缘消融" if melt_risks else "高危边界重叠"

        annotated_img_b64 = generate_annotated_thumbnail(orig_b64, b1, b2)
        img_html = f'<img src="data:image/jpeg;base64,{annotated_img_b64}" class="w-full h-32 object-cover rounded shadow-inner" title="点击放大查看">' if annotated_img_b64 else ""

        html += f'''
                <div class="border {border_color} rounded-lg p-5 bg-white shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-slate-600 uppercase">{title}</span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-black bg-slate-100 text-slate-500">常规 ΔE {normal_de:.1f}</span>
                        </div>
                        <div class="mt-2 mb-2 bg-slate-100 p-1 rounded border border-slate-200 cursor-zoom-in">
                            {img_html}
                        </div>
                        <p class="text-[11px] text-slate-600 leading-relaxed text-center">
                            上方 <b class="text-rose-500">红点</b> 与 <b class="text-amber-500">黄点</b> 的连线处存在辨识隐患
                        </p>
                    </div>
                </div>
        '''
    html += '</div></section>'
    return html

def generate_recommendations_section(analysis_data):
    # 保留为技术开发者准备的 CSS 详细代码工单模块
    html = '''
        <section class="bg-slate-900 rounded-xl shadow-xl no-print">
            <div class="px-6 py-5 bg-slate-800 border-b border-slate-700 rounded-t-xl">
                <h2 class="text-white font-bold flex items-center gap-2">
                    <span class="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
                    开发组落实工单 (Developer CSS Fixes)
                </h2>
                <p class="text-[11px] text-slate-400 mt-1">详细的开发落地变量替换指南。</p>
            </div>
            <div class="p-6 space-y-4">
    '''
    pairs = analysis_data.get('color_analysis', {}).get('color_pairs', [])
    failed_pairs = [p for p in pairs if not p['metrics']['aa_normal']]
    
    for idx, pair in enumerate(failed_pairs[:2]):
        orig_c, bg_c = pair['color1']['hex'], pair['color2']['hex']
        auto_c = pair.get('safe_palette_suggestion', {}).get('hex') or pair.get('suggestion', {}).get('hex', '')
        
        html += f'''
            <div class="border border-slate-700 rounded-lg p-4 bg-slate-800/40 flex justify-between items-center gap-4">
                <div>
                    <span class="text-[10px] font-black text-rose-400 uppercase tracking-widest block mb-1">Issue #{idx+1}</span>
                    <p class="text-xs text-slate-300">将组件的文字色从 <span class="text-rose-300 font-mono">{orig_c}</span> 变更为合规安全色 <span class="text-emerald-400 font-mono">{auto_c}</span>。</p>
                </div>
                <div class="bg-slate-950 rounded p-3 font-mono text-[10px] border border-slate-800 shrink-0">
                    <div class="text-emerald-400">color: {auto_c};</div>
                    <div class="text-slate-400">background-color: {bg_c};</div>
                </div>
            </div>
        '''
    if not failed_pairs:
        html += '<div class="text-emerald-400 text-sm">暂无阻塞性开发工单。</div>'
    html += '</div></section>'
    return html

def generate_cvd_section(analysis_data):
    cvd_analysis = analysis_data.get('cvd_analysis', {})
    orig_b64 = analysis_data.get('original_image_base64', '')
    
    html = '''
        <section class="bg-white rounded-xl border border-slate-200 shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                <h2 class="font-bold text-slate-800">色觉障碍 (CVD) 视觉模拟对比</h2>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-8">
    '''
    if orig_b64:
        html += f'''
                <div class="col-span-1 md:col-span-3 mb-2">
                    <h3 class="text-sm font-bold text-slate-800 border-l-4 border-indigo-500 pl-2 mb-3">基准视图 (Original Design)</h3>
                    <div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex justify-center p-2">
                        <img src="data:image/png;base64,{orig_b64}" class="w-full h-auto object-contain max-h-[500px]">
                    </div>
                </div>
        '''

    for cvd_type, cvd_data in cvd_analysis.items():
        if 'combined' in cvd_type.lower() or '对比' in cvd_data.get('name', ''): continue 
        if 'image_base64' in cvd_data:
            html += f'''
                <div class="space-y-3">
                    <div class="rounded-lg overflow-hidden border border-slate-200 shadow-sm bg-slate-50 p-1">
                        <img src="data:image/png;base64,{cvd_data['image_base64']}" class="w-full h-auto object-cover">
                    </div>
                    <h3 class="text-sm font-bold text-slate-800 text-center">{cvd_data.get('name', cvd_type)}</h3>
                </div>
            '''
    html += '</div></section>'
    return html

def generate_glossary_section():
    return '''
        <section class="bg-indigo-50/50 rounded-xl border border-indigo-100 p-8 no-print">
            <h2 class="text-sm font-bold text-indigo-900 uppercase tracking-widest mb-6">术语速查手册 (Glossary)</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">APCA (WCAG 3.0 现代算法)</h3>
                    <p class="text-[11px] text-indigo-900/70">下一代视觉算法。比传统对比度更准确地模拟了字体大小和深浅背景下的人眼知觉差异。</p>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-indigo-700 mb-1">色盲边缘消融 (CVD Boundary Melt)</h3>
                    <p class="text-[11px] text-indigo-900/70">两颜色普通人看对比强烈，但色盲眼中色差 ΔE 会暴跌至 3 以下，导致组件边界完全消失。</p>
                </div>
            </div>
        </section>
    '''

if __name__ == '__main__':
    print("HTML Report Generator enhanced with Global Palette Health and In-Context Matrix Fixes.")