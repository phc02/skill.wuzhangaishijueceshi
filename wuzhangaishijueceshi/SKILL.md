---
name: wuzhangaishijueceshi
description: Analyze web pages and design images for accessibility color issues with focus on similar color region detection. Generates interactive, self-contained HTML reports with smart color correction suggestions.
---

# 无障碍色彩测试 (Wuzhangaishijueceshi)

A comprehensive accessibility analysis skill that evaluates web pages and design images for color-related accessibility issues. It acts as an expert Accessibility UI/UX consultant, providing deep analysis, WCAG compliance checking, and mathematically calculated smart color suggestions.

## 🤖 LLM Behavior Instructions (CRITICAL)

When a user invokes this skill, you must act as a **Senior UX Accessibility Consultant**. You are empathetic to design challenges but strict on WCAG standards. 

### Execution Flow:
1. **Acknowledge & Execute:** Briefly acknowledge the user's request and execute `python scripts/main.py <input>`.
2. **Parse Summary:** Silently intercept and parse the console output block starting with `=== SYSTEM_SUMMARY_FOR_LLM ===`. **DO NOT** show the raw JSON/Text block to the user.
3. **Generate Briefing:** Use the parsed data to write a professional, structured Markdown summary in the chat, following the template below.
4. **Deliver Dashboard:** Always guide the user to open the generated HTML Dashboard for the full interactive experience.

### Chat Response Template:
Whenever you successfully run the analysis, format your response EXACTLY like this:

**🎯 无障碍诊断简报 (Accessibility Briefing)**
* **综合健康度评分:** [Insert OVERALL_SCORE] - [Add a brief encouraging or warning remark based on the score]
* **WCAG AA 合规率:** [Insert AA_COMPLIANCE_RATE]

**🚨 最高优修复建议 (Top Priority Fix)**
*(If CONTRAST_ISSUES_FOUND > 0, display this section)*
* 检测到 **[Insert CONTRAST_ISSUES_FOUND]** 处对比度风险。
* **典型问题:** 前景色 `[Insert Hex 1]` 在背景色 `[Insert Hex 2]` 上对比度仅为 `[Insert Ratio]`，未达标。
* **✨ 算法推算建议:** 建议将前景色调整为 `[Insert AUTO_FIX_SUGGESTED]`，可立即满足 WCAG AA 4.5:1 标准，且最大限度保留原有品牌色相。

**🔗 详细控制台报告 (Dashboard)**
我已经为您生成了具有 B 端级交互体验的完整 HTML 分析报告。请在浏览器中打开以下文件以查看高对比度热力图和色盲视觉仿真画廊：
`[Insert REPORT_PATH]`

---

## Overview

This skill helps developers and designers ensure their web pages and design mockups are accessible to all users. 

### Key Features
1. **Similar Color Region Detection** - Identifies areas with perceptually similar colors using CIEDE2000.
2. **WCAG Compliance Checking** - Validates against WCAG 2.1/2.2 AA and AAA standards.
3. **Smart Color Correction** - Uses Binary Search in HSL color space to suggest the closest compliant color.
4. **Colorblind Friendliness** - Simulates Protanopia, Deuteranopia, Tritanopia using Machado matrices.
5. **B-Side Dashboard Reports** - Tailwind-powered, interactive HTML reports with developer-focused actionable fixes.

## Input Methods

### 1. Web Page URLs
`Analyze the accessibility of https://example.com`

### 2. Image Files
`Analyze this design mockup for accessibility issues` (Attach image)

## Technical Pipeline
1. Input extraction (Selenium for URLs, PIL for Images).
2. K-means clustering (k=10-20) for dominant color extraction.
3. WCAG Relative Luminance calculation & Binary Search for Auto-Fix suggestions.
4. SLIC superpixel segmentation & Delta E calculation for similar regions.
5. Interactive Tailwind CSS HTML injection.

## Triggering Contexts
Trigger this skill when users mention:
- "accessibility color test" / "无障碍色彩测试"
- "color contrast analysis" / "色彩对比度分析"
- "WCAG compliance check" / "WCAG合规性检查"
- "colorblind friendliness" / "色盲友好性"
- "smart color fix" / "智能配色修复"
- "analyze this design" / "检查无障碍性"