---
brand: "{{BRAND_NAME}}"
created: "{{DATE}}"
last_updated: "{{DATE}}"
status: "active"
---

# {{BRAND_NAME}} — Infographic Brand Guideline

## Brand Identity

- **Brand Name:** {{BRAND_NAME}}
- **Industry/Niche:** {{e.g., SaaS, Health & Wellness, Finance, Education}}
- **Brand Voice:** {{e.g., Professional yet approachable, Bold and playful, Authoritative and minimal}}
- **Target Audience:** {{e.g., B2B decision-makers, Gen Z consumers, Healthcare professionals}}

---

## Visual Style (extracted from sample)

### Overall Aesthetic
<!-- Describe the look and feel observed in the sample image -->
- **Design Style:** {{e.g., Clean minimalist, Bold maximalist, Hand-drawn organic, Flat modern, Geometric}}
- **Mood/Tone:** {{e.g., Corporate trust, Energetic startup, Calm wellness, Playful creative}}
- **Illustration Style:** {{e.g., Flat vector icons, Line-art illustrations, 3D isometric, Hand-drawn sketches, Photographic cutouts}}

### Color Palette
| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Primary | {{name}} | `#______` | Headlines, key elements, brand anchors |
| Secondary | {{name}} | `#______` | Supporting sections, cards, dividers |
| Accent | {{name}} | `#______` | CTAs, highlights, emphasis |
| Background | {{name}} | `#______` | Canvas, card fills |
| Text Primary | {{name}} | `#______` | Body text, labels |
| Text Secondary | {{name}} | `#______` | Captions, subtle text |

### Typography
- **Headline Font:** {{e.g., Montserrat Bold, Playfair Display}}
- **Body Font:** {{e.g., Open Sans, Inter, Roboto}}
- **Title Size:** {{e.g., 36-48pt bold}}
- **Section Header Size:** {{e.g., 20-28pt semi-bold}}
- **Body Text Size:** {{e.g., 12-16pt regular}}
- **Caption Size:** {{e.g., 10-12pt light}}

### Layout Preferences
- **Preferred Aspect Ratio:** {{e.g., 9:16 vertical, 16:9 horizontal, 1:1 square}}
- **Grid Structure:** {{e.g., 2-column, 3-column, single column flow}}
- **White Space Level:** {{e.g., Generous (40%+), Moderate (30%), Compact (20%)}}
- **Element Spacing:** {{e.g., Loose and airy, Tight and dense, Medium}}

### Icon & Visual Elements
- **Icon Style:** {{e.g., Outline/line, Filled/solid, Duotone, Hand-drawn}}
- **Icon Weight:** {{e.g., Thin (1px), Medium (2px), Bold (3px)}}
- **Shape Language:** {{e.g., Rounded corners, Sharp geometric, Organic blobs, Circles}}
- **Decorative Elements:** {{e.g., Subtle dot patterns, Gradient overlays, None, Subtle lines}}

---

## Brand-Specific Prompt Rules

### Always Include
<!-- Phrases that MUST appear in every prompt for this brand -->
```
{{e.g., "Clean minimalist design with generous white space, LinkedIn Blue (#0A66C2) primary color..."}}
```

### Always Avoid
<!-- Anti-patterns specific to this brand -->
```
{{e.g., "No gradients, no 3D effects, no clip-art style icons, no busy backgrounds..."}}
```

### Signature Elements
<!-- Unique design elements that make this brand recognizable -->
- {{e.g., "Always include a thin colored line separator between sections"}}
- {{e.g., "Numbers are always displayed in the accent color at 2x body text size"}}
- {{e.g., "Bottom of every infographic has a branded footer bar"}}

---

## Prompt Prefix (auto-injected)

This block is prepended to every infographic prompt for this brand:

```
Style: {{BRAND_NAME}} brand identity. {{Overall aesthetic description in 2-3 sentences covering colors, typography, icon style, spacing, and mood.}}
Colors: Primary {{hex}}, Secondary {{hex}}, Accent {{hex}}, Background {{hex}}.
Typography: {{headline font}} for titles, {{body font}} for text. Bold headline, clean body, no overlapping text.
Icons: {{icon style}} style, consistent weight, {{color}} color.
Layout: {{aspect ratio}}, {{grid structure}}, generous white space, balanced composition.
Anti-patterns: {{list of things to avoid for this brand}}.
```

---

## Sample Reference

- **Sample Image Path:** `brands/samples/{{brand_name}}_sample.png`
- **What was extracted:** {{Brief note on what design patterns were observed}}

---

## Usage Notes

<!-- Any special instructions or context for using this brand -->
{{e.g., "This brand's infographics are used for LinkedIn carousels — always use 1:1 square format."}}
{{e.g., "Client prefers data-heavy infographics — lean toward Statistical and Comparison types."}}
