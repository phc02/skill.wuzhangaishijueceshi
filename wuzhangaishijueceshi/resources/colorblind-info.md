# Color Vision Deficiency (CVD) Information

## Overview

Color vision deficiency (CVD), commonly known as color blindness, is a condition where a person cannot distinguish between certain colors. It affects approximately 8% of men and 0.5% of women worldwide.

## Types of Color Vision Deficiency

### 1. Protanopia (Red-Blind)

**Prevalence**: ~1% of males

**Characteristics**:
- Cannot perceive red light
- Red appears dark or black
- Difficulty distinguishing red from green
- Purple appears blue

**Design Considerations**:
- Avoid red-green combinations
- Use blue-yellow instead
- Add patterns or icons to differentiate

### 2. Protanomaly (Red-Weak)

**Prevalence**: ~1% of males

**Characteristics**:
- Reduced sensitivity to red light
- Red appears more orange/brown
- Difficulty with red-green discrimination
- Less severe than protanopia

### 3. Deuteranopia (Green-Blind)

**Prevalence**: ~1% of males

**Characteristics**:
- Cannot perceive green light
- Green appears brownish-yellow
- Difficulty distinguishing red from green
- Most common form of color blindness

**Design Considerations**:
- Avoid red-green combinations
- Use blue-orange or blue-yellow
- Ensure sufficient contrast

### 4. Deuteranomaly (Green-Weak)

**Prevalence**: ~5% of males

**Characteristics**:
- Reduced sensitivity to green light
- Green appears more red/orange
- Most common form of color weakness
- Less severe than deuteranopia

### 5. Tritanopia (Blue-Blind)

**Prevalence**: Very rare (~0.001%)

**Characteristics**:
- Cannot perceive blue light
- Blue appears green
- Yellow appears violet or gray
- Difficulty with blue-yellow discrimination

### 6. Achromatopsia (Total Color Blindness)

**Prevalence**: Very rare (~0.0001%)

**Characteristics**:
- No color perception (monochromatic vision)
- See only shades of gray
- Often accompanied by light sensitivity (photophobia)
- Reduced visual acuity

## Impact on Web Design

### Common Problems

1. **Color-Coded Information**
   - Charts with color-only legends
   - Form validation using only color
   - Status indicators (red/green dots)

2. **Low Contrast**
   - Light gray text on white background
   - Similar colors for important elements
   - Insufficient contrast ratios

3. **Color Combinations**
   - Red-green (most problematic)
   - Blue-purple
   - Green-brown

### Design Solutions

#### 1. Use Multiple Indicators
```css
/* Bad: Color only */
.error { color: red; }

/* Good: Color + icon + text */
.error { 
    color: red; 
    font-weight: bold;
}
.error::before { content: "⚠️ "; }
```

#### 2. Ensure Sufficient Contrast
- Normal text: 4.5:1 minimum (AA)
- Large text: 3:1 minimum (AA)
- UI components: 3:1 minimum

#### 3. Use CVD-Friendly Palettes
- Blue-Orange (works for most CVD types)
- Blue-Yellow
- Avoid Red-Green combinations

#### 4. Provide Text Alternatives
- Always include text labels
- Use patterns in addition to color
- Provide data tables for charts

## Testing for CVD Accessibility

### Manual Testing
1. Convert designs to grayscale
2. Check if information is still clear
3. Verify contrast ratios

### Simulation Tools
- **Coblis**: Online colorblind simulator
- **Color Oracle**: Desktop application
- **Chrome DevTools**: Rendering tab with CVD simulation
- **Figma/Sketch Plugins**: Stark, Color Blind

### Automated Testing
- Use contrast checking tools
- Run accessibility audits
- Test with screen readers

## Resources

### Tools
- [Coblis Color Blind Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Color Oracle](https://colororacle.org/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### References
- [Color Blindness Facts](https://www.color-blindness.com/)
- [NCBI: Color Vision Deficiency](https://www.ncbi.nlm.nih.gov/books/NBK541036/)
- [W3C: Understanding Color and Accessibility](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
