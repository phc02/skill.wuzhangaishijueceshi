# WCAG 2.1/2.2 Color Accessibility Guidelines

## Overview

The Web Content Accessibility Guidelines (WCAG) provide standards for making web content accessible to people with disabilities, including color vision deficiencies.

## Relevant Success Criteria

### 1.4.1 Use of Color (Level A)

**Requirement**: Color is not the only means of conveying information.

**Implementation**:
- Use icons, patterns, or text labels in addition to color
- Ensure information is available without relying on color perception

**Examples**:
- ❌ Error messages shown only in red text
- ✅ Error messages with red text AND an error icon

### 1.4.3 Contrast (Minimum) (Level AA)

**Requirement**: Text and images of text have a contrast ratio of at least 4.5:1 (normal text) or 3:1 (large text).

**Implementation**:
- Normal text (below 18pt or 14pt bold): 4.5:1 minimum
- Large text (18pt+ or 14pt+ bold): 3:1 minimum

**Examples**:
- ❌ Light gray text on white background (1.5:1)
- ✅ Dark gray text on white background (12:1)

### 1.4.6 Contrast (Enhanced) (Level AAA)

**Requirement**: Text and images of text have a contrast ratio of at least 7:1 (normal text) or 4.5:1 (large text).

**Implementation**:
- Normal text: 7:1 minimum
- Large text: 4.5:1 minimum

### 1.4.11 Non-text Contrast (Level AA)

**Requirement**: UI components and graphical objects have a contrast ratio of at least 3:1.

**Implementation**:
- Form input borders: 3:1 against background
- Icons: 3:1 against background
- Graphical objects: 3:1 against adjacent colors

## Contrast Ratio Calculation

### Relative Luminance Formula

```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B
```

Where R, G, B are adjusted values:
- If c ≤ 0.03928: c' = c / 12.92
- If c > 0.03928: c' = ((c + 0.055) / 1.055) ^ 2.4

### Contrast Ratio Formula

```
Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)
```

Where L1 is the lighter color and L2 is the darker color.

## Color Vision Deficiencies

### Types of CVD

1. **Protanopia** (Red-Blind)
   - Affects ~1% of males
   - Difficulty distinguishing red and green

2. **Deuteranopia** (Green-Blind)
   - Affects ~1% of males
   - Difficulty distinguishing red and green

3. **Tritanopia** (Blue-Blind)
   - Very rare
   - Difficulty distinguishing blue and yellow

4. **Achromatopsia** (Total Color Blindness)
   - Very rare
   - No color perception

### Design Considerations for CVD

1. **Don't rely on color alone**
   - Use patterns, icons, or text labels
   - Example: Error states should have icons, not just red color

2. **Use sufficient contrast**
   - Ensure text is readable without color
   - Test in grayscale mode

3. **Choose CVD-friendly color palettes**
   - Avoid red-green combinations
   - Use blue-orange or blue-yellow instead

4. **Test with simulators**
   - Use colorblind simulation tools
   - Check designs in different CVD modes

## Testing Tools

### Online Contrast Checkers
- WebAIM Contrast Checker
- Contrast Ratio (Lea Verou)
- Stark (Figma/Sketch plugin)

### Colorblind Simulators
- Coblis Color Blind Simulator
- Color Oracle (desktop app)
- Chrome DevTools (Rendering tab)

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [Understanding WCAG 2.1](https://www.w3.org/WAI/WCAG21/Understanding/)
- [WebAIM Color Contrast Guide](https://webaim.org/articles/contrast/)
