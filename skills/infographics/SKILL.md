---
name: infographics
description: "Create professional, brand-consistent infographics using Kie AI Nano Banana 2. Brand-first workflow: analyze sample images, build reusable brand guidelines, then generate on-brand infographics via the Nano Banana 2 async task API."
tags: [infographics, branding, kie-ai, image-generation, visual]
trigger_keywords: [infographic, create infographic, make infographic, brand infographic, visual content, data visualization]
summary: Brand-first infographic generation via Kie AI Nano Banana 2 — onboard brand once, generate on-brand infographics async with quality scoring. Requires KIE_API_KEY.
---

# Infographics Skill (Nano Banana 2)

## Philosophy

Generic prompts produce cluttered, clip-art-filled images. **The secret to professional infographics is a brand-first workflow** — you define a detailed visual style guide BEFORE you ever generate an image, then every infographic inherits that identity automatically.

This skill follows a two-step prompting system inspired by professional design workflows:
1. **Step 1 — Brand Style Guide** (one-time per brand): Analyze a sample, ask refinement questions, save a reusable `.md` file.
2. **Step 2 — Generate** (every time): Inject the brand's prompt prefix + your content into Nano Banana 2 via Kie AI.

> **API**: Kie AI Nano Banana 2 — requires `KIE_API_KEY` from [kie.ai/api-key](https://kie.ai/api-key)
> **Review** (optional): OpenRouter — requires `OPENROUTER_API_KEY` for quality review iterations

---

## How Nano Banana 2 Works

Unlike synchronous image APIs, Nano Banana 2 uses an **async task model**:

```
1. POST /api/v1/jobs/createTask  →  returns taskId
2. GET  /api/v1/jobs/recordInfo?taskId=...  →  poll until state = "success"
3. Download result from resultUrls
```

The generation script handles all of this automatically. See `resources/style-details.md` for full API docs.

### Key Capabilities
- **Resolution**: 1K, 2K, 4K
- **Aspect Ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto
- **Reference Images**: Up to 14 input images for style transfer
- **Google Search**: Real-time info grounding
- **Output Formats**: PNG, JPG

---

## Folder Structure

```
infographicsM2/
├── SKILL.md                    # This file — the skill definition
├── brands/                     # Brand guideline files (one .md per brand)
│   ├── _TEMPLATE.md            # Template for creating new brand guidelines
│   ├── {{brand_name}}.md       # Completed brand guideline
│   └── ...
├── references/                 # Design reference docs
│   ├── design_principles.md
│   ├── color_palettes.md
│   └── infographic_types.md
├── resources/                  # API documentation
│   └── style-details.md        # Nano Banana 2 API reference
└── scripts/                    # Generation scripts
    ├── generate_infographic.py     # CLI wrapper
    └── generate_infographic_ai.py  # Core AI generation engine
```

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER REQUEST                         │
│         "Create an infographic about X"                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Brand exists?  │
              └───┬────────┬───┘
                  │        │
                 YES       NO
                  │        │
                  │        ▼
                  │  ┌──────────────────────────┐
                  │  │  BRAND ONBOARDING FLOW   │
                  │  │  1. Collect sample image  │
                  │  │  2. Analyze visual style  │
                  │  │  3. Ask refinement Qs     │
                  │  │  4. Save brand .md file   │
                  │  └──────────┬───────────────┘
                  │             │
                  ▼             ▼
          ┌─────────────────────────────┐
          │   GENERATE INFOGRAPHIC      │
          │  1. Load brand guideline    │
          │  2. Choose layout/type      │
          │  3. Build structured prompt │
          │  4. POST to Kie AI API      │
          │  5. Poll for completion     │
          │  6. Download result image   │
          │  7. Review & refine (opt.)  │
          └─────────────────────────────┘
```

---

## Part 1: Brand Onboarding (New Brand Setup)

When a user wants infographics for a brand you haven't set up yet, run this flow **once**. The result is a reusable brand guideline `.md` file.

### Step 1 — Collect a Sample Image

Ask the user:

> **"Please share a sample image or existing infographic that represents the visual style you want. This can be:**
> - An infographic you've made before
> - A design from your brand kit
> - A screenshot of a style you admire
> - Any image that captures the look and feel you're going for
>
> **I'll analyze it to extract your brand's visual DNA."**

### Step 2 — Analyze the Sample Image

Use your vision capabilities to read the sample image. Extract and document:

| Element | What to Extract |
|---------|----------------|
| **Color Palette** | Dominant colors (with approximate hex), background color, accent colors, text colors |
| **Typography** | Font style, weight, sizes, special treatments (ALL CAPS, letter-spacing) |
| **Layout** | Grid structure, columns, vertical vs horizontal flow, spacing density |
| **Illustration Style** | Flat vector, line-art, 3D, photographic, hand-drawn, isometric |
| **Icon Style** | Outline, filled, duotone, rounded, sharp, consistent weight |
| **Shape Language** | Rounded corners vs sharp, circles vs rectangles |
| **White Space** | Generous vs compact, padding, margins |
| **Decorative Elements** | Patterns, gradients, borders, shadows, overlays |
| **Overall Mood** | Professional, playful, minimal, bold, elegant, techy, organic |

### Step 3 — Ask Refinement Questions

**Required Questions:**
1. **"What's the brand name and industry?"**
2. **"Is my color analysis accurate? Want to adjust any colors or provide exact hex codes?"**
3. **"What aspect ratio do you typically need?"** — 9:16, 16:9, 1:1, or custom
4. **"Any elements you specifically want to AVOID?"**
5. **"Anything I missed or got wrong about the style?"**

### Step 4 — Save the Brand Guideline

1. Copy `brands/_TEMPLATE.md` as the starting point.
2. Fill in every section with the extracted + refined information.
3. Write the `Prompt Prefix` block — the reusable text injected into every prompt.
4. Save as `brands/{{brand_name}}.md`

---

## Part 2: Generating Infographics (Every Time)

### Step 1 — Load the Brand Guideline

Read the brand's `.md` file from `brands/`. Extract the **Prompt Prefix** block.

### Step 2 — Choose Infographic Type & Layout

| Type | Best For |
|------|----------|
| Statistical/Data-Driven | Numbers, percentages, survey results, metrics |
| Timeline | History, milestones, evolution, project phases |
| Process/How-To | Steps, workflows, tutorials, recipes |
| Comparison | Product vs product, pros/cons, before/after |
| List/Informational | Tips, facts, key points, checklists |
| Geographic | Regional data, demographics, global trends |
| Hierarchical/Pyramid | Org structures, priority levels, ranked lists |
| Visual Metaphor | Complex systems explained via familiar images |
| Resume/Professional | Personal branding, CVs, portfolio highlights |
| Social Media | Platform-optimized posts, quotes, quick stats |

> See `references/infographic_types.md` for detailed templates and examples per type.

**Layout Templates:**

| Template | Structure | Best For |
|----------|-----------|----------|
| Arc / Radial | Semi-circular arc with central visual | Cyclical processes |
| Horizontal Step Cards | Row of 3-5 alternating-color cards | Process flows |
| Top Boxes + Connector | Boxes at top converging to bottom banner | Ideas converging |
| 2x3 Icon Grid | 2-column, 3-row card grid | 6 key points |
| Vertical Timeline (Zigzag) | Center line with alternating left-right | History, milestones |
| Single Column Flow | Stacked sections top-to-bottom | Mobile-friendly |
| Split Comparison | Left vs Right symmetrical layout | Comparisons |
| Modular Cards | Mixed-size card mosaic | Varied content |

### Step 3 — Build the Structured Prompt

```
[BRAND PREFIX]:  {{Paste the Prompt Prefix from the brand guideline}}

[LAYOUT]:        A [template name] infographic titled "[TITLE]".
[STRUCTURE]:     [Describe the exact grid, columns, or flow]
[CONTENT]:       [List every item with exact label, number, and description]
[ASPECT RATIO]:  [From brand guideline — e.g., "9:16 vertical"]
[RESOLUTION]:    High resolution, minimum 2K, sharp details.
[SOURCE]:        Small source line at bottom: "[Source text]"
[ANTI-PATTERNS]: [Brand-specific avoidances + general: no meta-content]
```

### Step 4 — Generate via Nano Banana 2

Call the generation script or use the API directly:

```bash
python scripts/generate_infographic.py "Your prompt here" \
  -o output.png \
  --type list \
  --style corporate \
  --resolution 2K
```

Or via the Python API:

```python
from generate_infographic_ai import InfographicGenerator

gen = InfographicGenerator(api_key="your_kie_api_key")
results = gen.generate_iterative(
    user_prompt="5 benefits of exercise",
    output_path="benefits.png",
    infographic_type="list",
    style="corporate",
    resolution="2K"
)
```

**Key generation rules:**
- Always specify the aspect ratio from the brand guideline
- Request high resolution (2K recommended, 4K for print)
- Never include layout labels, color hex codes, or prompt text visible in the image
- Keep text in the infographic to short phrases (5-10 words max per point)
- Every statistic must be provided explicitly — never let the model invent numbers

### Step 5 — Review & Refine (Max 3 Iterations)

If `OPENROUTER_API_KEY` is set, the script automatically reviews via AI vision. Score on 5 criteria (0-2 each, max 10):

| # | Criterion | What to Check |
|---|-----------|---------------|
| 1 | **Brand Consistency** | Colors, fonts, icon style, mood |
| 2 | **Visual Hierarchy & Layout** | Clear flow, balanced, white space |
| 3 | **Typography & Readability** | Bold headlines, no overlapping text |
| 4 | **Content Accuracy** | Correct numbers, proper labels |
| 5 | **Overall Impact** | Professional, no artifacts |

**Quality Thresholds:**

| Context | Threshold |
|---------|-----------|
| Client-facing / Marketing | 8.5/10 |
| Report / Presentation | 8.0/10 |
| Social Media | 7.5/10 |
| Internal / Draft | 7.0/10 |

If no OpenRouter key is set, the script does a single-pass generation without review.

---

## Part 3: Core Design Principles

Apply these to **every** prompt, regardless of brand:

### Layout & Spacing
- Grid-based structure with explicit column/row definitions
- Consistent spacing — uniform margins and gutters
- ~30% white space minimum
- Logical reading flow: top-to-bottom OR left-to-right

### Color Rules
- 2-3 colors maximum (from brand guideline)
- 60-30-10 distribution: 60% dominant, 30% secondary, 10% accent
- High contrast between text and background (4.5:1 minimum)

### Typography
- Maximum 2 fonts per infographic
- Clear size hierarchy: Title > Section Headers > Body > Captions
- No overlapping text
- Bold key numbers and statistics

### Content
- 60% visual elements, 40% text (the 60/40 rule)
- No text blocks — short bullet points + icons
- Every data point provided explicitly
- Include source citation at bottom

### Anti-Patterns (always avoid)
- Too much text
- Busy or photographic backgrounds
- Misaligned elements
- Generic clip-art icons
- Meta-content visible in the image
- More than 3 colors or more than 2 fonts

---

## Part 4: Nano Banana 2 Specific Features

### Reference Images (Style Transfer)
You can pass up to 14 reference images to guide the style:

```bash
python scripts/generate_infographic.py "Redesign this infographic" \
  -o redesigned.png \
  --image-input "https://example.com/reference1.png" \
  --image-input "https://example.com/reference2.png"
```

### Google Search Grounding
For infographics that need real-time data:

```bash
python scripts/generate_infographic.py "Latest AI trends 2026" \
  -o ai_trends.png \
  --type statistical \
  --google-search
```

### Resolution Options
- **1K** — Fast generation, good for drafts and social media
- **2K** — Recommended default, sharp for web and presentations
- **4K** — Ultra-high quality for print and large displays

---

## Quick Reference: Agent Checklist

When a user asks for an infographic, run through this checklist:

- [ ] **Brand exists?** → If no, run Brand Onboarding (Part 1)
- [ ] **Brand loaded?** → Read the brand's `.md` file, extract Prompt Prefix
- [ ] **Data accurate?** → Research/verify any statistics before generating
- [ ] **Type chosen?** → Pick the best infographic type for the content
- [ ] **Layout chosen?** → Pick the best layout template
- [ ] **Prompt built?** → Combine: Brand Prefix + Layout + Content + Anti-patterns
- [ ] **Aspect ratio set?** → From brand guideline
- [ ] **Resolution set?** → 2K default, 4K for print
- [ ] **Generated?** → POST to Kie AI, poll for result, download image
- [ ] **Reviewed?** → Score against 5 criteria (if OpenRouter key available)
- [ ] **Meets threshold?** → If no, refine and regenerate (max 3 iterations)
- [ ] **Delivered?** → Present to user with any notes

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KIE_API_KEY` | Yes | Kie AI API key for Nano Banana 2 generation |
| `OPENROUTER_API_KEY` | No | OpenRouter key for quality review and research |

Get your Kie AI key at: [kie.ai/api-key](https://kie.ai/api-key)
