#!/usr/bin/env python3
"""
AI-powered infographic generation using Kie AI Nano Banana 2.

This script uses a smart iterative refinement approach:
1. (Optional) Research phase - gather facts and data using Perplexity Sonar
2. Generate initial infographic with Nano Banana 2 via Kie AI API
3. AI quality review using OpenRouter (optional, if OPENROUTER_API_KEY set)
4. Only regenerate if quality is below threshold for document type
5. Repeat until quality meets standards (max iterations)

Requirements:
    - KIE_API_KEY environment variable (required)
    - OPENROUTER_API_KEY environment variable (optional, for quality review)
    - requests library

Usage:
    python generate_infographic_ai.py "5 benefits of exercise" -o benefits.png --type list
    python generate_infographic_ai.py "Global AI market size" -o ai_market.png --type statistical --research
    python generate_infographic_ai.py "Company history 2010-2025" -o timeline.png --type timeline --style corporate
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def _load_env_file():
    """Load .env file from current directory, parent directories, or package directory."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False

    # Try current working directory first
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
        return True

    # Try parent directories (up to 5 levels)
    cwd = Path.cwd()
    for _ in range(5):
        env_path = cwd / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            return True
        cwd = cwd.parent
        if cwd == cwd.parent:
            break

    # Try the package's parent directory
    script_dir = Path(__file__).resolve().parent
    for _ in range(5):
        env_path = script_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            return True
        script_dir = script_dir.parent
        if script_dir == script_dir.parent:
            break

    return False


# Infographic type configurations with detailed prompting
INFOGRAPHIC_TYPES = {
    "statistical": {
        "name": "Statistical/Data-Driven",
        "guidelines": """
STATISTICAL INFOGRAPHIC REQUIREMENTS:
- Large, bold numbers that are immediately readable (biggest text on canvas)
- Clear data visualization: bar charts for comparisons, pie/donut for parts-of-whole, line for trends
- Data callouts with context (e.g., '35% increase YoY')
- Trend indicators (arrows, growth/decline symbols)
- Legend if multiple data series
- Source attribution area at bottom right in small text
- Clean grid alignment for all data elements
- Use max 3 colors for data series to avoid confusion
- Colorblind-safe palette preferred
"""
    },
    "timeline": {
        "name": "Timeline/Chronological",
        "guidelines": """
TIMELINE INFOGRAPHIC REQUIREMENTS (Zigzag/Alternating Style):
- Vertical center line with circular node markers (hollow circles)
- Items ALTERNATE left-right (zigzag) for visual interest
- Each item: bold year/date banner in accent color, title, 2-3 sentence description
- Use a different accent color per era or milestone (navy, coral, teal, gold)
- Subtle dot-grid or line-grid background for a professional, editorial look
- Consistent spacing between events
- Clear start (oldest) at top, end (newest) at bottom
- Each date banner is a contrasting colored pill/rectangle shape
"""
    },
    "process": {
        "name": "Process/How-To",
        "guidelines": """
PROCESS INFOGRAPHIC REQUIREMENTS (Horizontal Step Cards):
- A horizontal row of 3-5 cards, each with a unique accent color border
- Each card has: a circular icon badge (at top or bottom, overlapping card edge), a step label ('Step A', 'Step B'), a bold title, and a 2-line description
- Cards have white backgrounds, colored top/left accent border, and subtle drop shadows
- Circular icon badges use the same accent color as the card
- Light gray or white canvas background
- Directional arrows or visual flow between cards
- Consistent card sizes and padding
"""
    },
    "comparison": {
        "name": "Comparison",
        "guidelines": """
COMPARISON INFOGRAPHIC REQUIREMENTS:
- Symmetrical side-by-side layout with a clear center divider
- Bold distinct headers for each option (different colors)
- Matching rows/categories for fair comparison
- Visual indicators: green checkmarks for pros, red X marks for cons, star ratings
- Equal visual weight on both sides
- Summary or verdict section at the bottom
- Use only 2 primary colors (one per side) plus neutral for shared rows
"""
    },
    "list": {
        "name": "List/Informational",
        "guidelines": """
LIST INFOGRAPHIC REQUIREMENTS (Icon Grid Style):
- Use a 2xN or 3xN grid of white rounded-rectangle cards on a light gray background
- Each card: rounded-corner colored border, centered icon, bold ALL-CAPS label, 2-3 line description
- Card border colors cycle through 3-4 accent colors (e.g., coral, teal, gold, purple)
- Icons use consistent style: flat outline icons
- Card padding: 16-24px, subtle drop shadows
- Title banner at the top in a bold contrasting color
- No more than 6 items in a list (use hierarchy if more needed)
"""
    },
    "geographic": {
        "name": "Geographic/Map-Based",
        "guidelines": """
GEOGRAPHIC INFOGRAPHIC REQUIREMENTS:
- Clean, simplified map as background or main element
- Color-coded regions based on data value (light = low, dark = high)
- Bold color legend in a corner
- Data callout bubbles for top 3-5 key regions
- Region labels where space allows
- Subtle outline-only map lines (not filled by default)
- Simple, clean cartographic style — no 3D or complex projection
"""
    },
    "hierarchical": {
        "name": "Hierarchical/Pyramid",
        "guidelines": """
HIERARCHICAL INFOGRAPHIC REQUIREMENTS:
- Clear pyramid (wide at base) or inverted pyramid or tree structure
- Distinct levels with visual separation and color per level
- Size progression: larger sections at base, smaller at top
- Bold labels for each tier
- Gradient or distinct accent color per level (darkest at top or base depending on context)
- Centered composition with horizontal guides
- Can include brief description next to each tier level
"""
    },
    "anatomical": {
        "name": "Anatomical/Visual Metaphor",
        "guidelines": """
ANATOMICAL INFOGRAPHIC REQUIREMENTS:
- A central metaphor illustration (brain, tree, machine, rocket, etc.)
- Labeled components with clean callout lines extending outward
- Circular or rectangular label badges at the end of each callout line
- Each label: icon + bold term + 1-line explanation
- Consistent callout line style (dashed or solid, same weight)
- Educational, technical illustration aesthetic
- Light background to make the central illustration stand out
"""
    },
    "resume": {
        "name": "Resume/Professional",
        "guidelines": """
RESUME INFOGRAPHIC REQUIREMENTS:
- Top section: name, title, tagline, professional avatar/photo placeholder
- Skills section: progress bars or spider chart with % labels
- Experience: mini timeline or vertical list with company, role, years
- Contact icons row: email, phone, LinkedIn, location
- Achievement/certification badge icons
- Two-column layout: left sidebar (darker accent color) for contact/skills, right main area for experience
- Personal accent color branding throughout
"""
    },
    "social": {
        "name": "Social Media",
        "guidelines": """
SOCIAL MEDIA INFOGRAPHIC REQUIREMENTS:
- Square (1:1) or portrait (4:5) format
- One bold, large headline (max 8 words) at the top
- Single large central statistic or powerful visual
- Minimal text — max 30 words total on the canvas
- Vibrant, saturated colors (use the style preset fully)
- Strong CTA element at the bottom
- Brand/logo watermark area in the corner
- High contrast between all text and background
"""
    },
}

# Industry style configurations
STYLE_PRESETS = {
    "corporate": {
        "name": "Corporate/Business",
        "colors": "navy blue (#1E3A5F), steel blue (#4A90A4), gold (#F5A623) accents",
        "description": "Clean, professional, minimal design with structured layout",
    },
    "healthcare": {
        "name": "Healthcare/Medical",
        "colors": "medical blue (#0077B6), cyan (#00B4D8), light cyan (#90E0EF)",
        "description": "Trust-inducing, clinical, clean design",
    },
    "technology": {
        "name": "Technology/Data",
        "colors": "tech blue (#2563EB), slate gray (#475569), violet (#7C3AED) accents",
        "description": "Modern, innovative, futuristic design",
    },
    "nature": {
        "name": "Nature/Environmental",
        "colors": "forest green (#2D6A4F), mint (#95D5B2), earth brown (#8B4513)",
        "description": "Organic, natural, earth-toned design",
    },
    "education": {
        "name": "Education/Academic",
        "colors": "academic blue (#3D5A80), light blue (#98C1D9), coral (#EE6C4D) accents",
        "description": "Friendly, approachable, educational design",
    },
    "marketing": {
        "name": "Marketing/Creative",
        "colors": "coral (#FF6B6B), teal (#4ECDC4), yellow (#FFE66D)",
        "description": "Bold, vibrant, eye-catching design",
    },
    "finance": {
        "name": "Finance/Investment",
        "colors": "navy (#14213D), gold (#FCA311), green (#2ECC71) for positive",
        "description": "Conservative, trustworthy, professional design",
    },
    "nonprofit": {
        "name": "Nonprofit/Cause",
        "colors": "warm orange (#E07A5F), sage green (#81B29A), sand (#F2CC8F)",
        "description": "Warm, human-centered, impactful design",
    },
}

# Colorblind-safe palette options
PALETTE_PRESETS = {
    "wong": {
        "name": "Wong's Palette",
        "colors": "orange (#E69F00), sky blue (#56B4E9), bluish green (#009E73), blue (#0072B2), vermillion (#D55E00)",
    },
    "ibm": {
        "name": "IBM Colorblind-Safe",
        "colors": "ultramarine (#648FFF), indigo (#785EF0), magenta (#DC267F), orange (#FE6100), gold (#FFB000)",
    },
    "tol": {
        "name": "Tol's Qualitative",
        "colors": "indigo (#332288), cyan (#88CCEE), teal (#44AA99), green (#117733), sand (#DDCC77), rose (#CC6677)",
    },
}

# Aspect ratio mapping for Nano Banana 2
ASPECT_RATIOS = {
    "square": "1:1",
    "portrait": "9:16",
    "landscape": "16:9",
    "tall": "2:3",
    "wide": "3:2",
    "photo": "4:3",
    "photo_portrait": "3:4",
    "instagram": "4:5",
    "instagram_landscape": "5:4",
    "cinematic": "21:9",
    "auto": "auto",
}


class InfographicGenerator:
    """Generate infographics using Kie AI Nano Banana 2 with smart iterative refinement.

    Uses Nano Banana 2 for image generation via the Kie AI async task API.
    Optionally uses OpenRouter for quality review if OPENROUTER_API_KEY is set.
    """

    # Quality thresholds by document type (score out of 10)
    QUALITY_THRESHOLDS = {
        "marketing": 8.5,
        "report": 8.0,
        "presentation": 7.5,
        "social": 7.0,
        "internal": 7.0,
        "draft": 6.5,
        "default": 7.5,
    }

    # Base infographic design guidelines
    INFOGRAPHIC_GUIDELINES = """
Create a high-quality, publication-ready infographic following these MANDATORY design rules:

=== DESIGN & LAYOUT ===
- Use a GRID-BASED structure: all elements must be aligned to an invisible grid
- Consistent spacing: equal margins and gutters between ALL sections, icons, and text blocks
- White space: keep ~30% of the canvas empty — it is not wasted space, it guides the eye
- Visual hierarchy: Title > Section Headers > Body Text. Signal importance with size, weight, and color
- 60/40 rule: ~60% visual elements (icons, charts, illustrations), ~40% text
- Logical reading flow: strictly top-to-bottom OR left-to-right — never both simultaneously
- Balanced composition: mirror visual weight on left and right

=== COLOR RULES ===
- MAXIMUM 3 COLORS: one primary, one secondary, one accent — more than 3 creates chaos
- High contrast: text must contrast sharply against its background (aim for 4.5:1+ contrast ratio)
- Consistent icon style: ALL icons must share the same visual style (all outline OR all filled, never mixed)
- Subtle background: light solid color or very subtle pattern — NO busy textures, NO photo backgrounds
- Reserve gradients for UI card accents only, never for the main background

=== TYPOGRAPHY ===
- Maximum 2 font families: one bold display font for headlines, one clean sans-serif for body
- Font size hierarchy: Title >= 32pt | Section headers >= 18pt | Body text >= 12pt | Captions >= 10pt
- NO overlapping text: every text element must have clear breathing room from adjacent elements
- Bold key numbers: statistics and key figures should be the LARGEST, BOLDEST text element
- No text blocks: replace paragraphs with 5-10 word bullet points paired with icons

=== DATA VISUALIZATION ===
- Large, bold numbers for key statistics — make them impossible to miss
- Use the RIGHT chart type: bar for comparisons, pie/donut for parts-of-whole, line for trends
- Labeled axes and data points — never make the viewer guess
- Legend where multiple data series exist
- Icons that clearly and literally represent the concept

=== CONTENT & STORYTELLING ===
- Compelling headline: specific, action-oriented, answers 'what will I learn?'
- Always include a small source/citation line at the bottom for credibility
- Each visual element should serve the story — remove anything decorative that adds no information

=== AVOID THESE MISTAKES ===
- Too much text (never use paragraphs, only short punchy phrases)
- Too many fonts (max 2 families)
- Busy or distracting backgrounds that compete with the content
- Misaligned elements (use the grid!)
- Too many colors (max 3)
- Generic icons that don't match the specific concept

=== CRITICAL - NO META CONTENT ===
- Do NOT include the prompt, instructions, or metadata in the image
- Do NOT include layout descriptions like 'left panel', 'right panel'
- Do NOT include font names or color hex codes as visible text
- Only include the actual infographic content — nothing else
"""

    # Kie AI API endpoints
    KIE_CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
    KIE_STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

    def __init__(self, api_key: Optional[str] = None,
                 openrouter_key: Optional[str] = None,
                 verbose: bool = False):
        """Initialize the generator.

        Args:
            api_key: Kie AI API key (or KIE_API_KEY env var)
            openrouter_key: OpenRouter API key for quality review (optional)
            verbose: Enable verbose logging
        """
        self.api_key = api_key or os.getenv("KIE_API_KEY")

        if not self.api_key:
            _load_env_file()
            self.api_key = os.getenv("KIE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "KIE_API_KEY not found. Please either:\n"
                "  1. Set the KIE_API_KEY environment variable\n"
                "  2. Add KIE_API_KEY to your .env file\n"
                "  3. Pass api_key parameter to the constructor\n"
                "Get your API key from: https://kie.ai/api-key"
            )

        self.openrouter_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        self.verbose = verbose
        self._last_error = None

    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    # ========== RESEARCH METHODS ==========

    def research_topic(self, topic: str, infographic_type: Optional[str] = None) -> Dict[str, Any]:
        """Research a topic using Perplexity Sonar Pro (requires OPENROUTER_API_KEY)."""
        if not self.openrouter_key:
            self._log("Skipping research - OPENROUTER_API_KEY not set")
            return {"success": False, "error": "OPENROUTER_API_KEY not set for research"}

        self._log(f"Researching topic: {topic}")

        type_context = ""
        if infographic_type:
            type_contexts = {
                "statistical": "Focus on statistics, numbers, percentages, and quantitative data.",
                "timeline": "Focus on key dates, milestones, and chronological events.",
                "process": "Focus on steps, procedures, and sequential information.",
                "comparison": "Focus on comparing different options, pros/cons, and differences.",
                "list": "Focus on key points, tips, facts, and organized information.",
                "geographic": "Focus on regional data, location-based statistics, and geographic distribution.",
                "hierarchical": "Focus on levels, rankings, and hierarchical relationships.",
            }
            type_context = type_contexts.get(infographic_type, "")

        research_prompt = f"""You are a research assistant gathering information for an infographic.

TOPIC: {topic}

{type_context}

Please provide:
1. KEY FACTS: 5-8 key facts or statistics about this topic (with specific numbers where possible)
2. CONTEXT: Brief background context (2-3 sentences)
3. SOURCES: Mention any major sources or studies
4. DATA POINTS: Any specific data points that would make good visualizations

Format your response as structured data that can be easily incorporated into an infographic.
Be specific with numbers, percentages, and dates.
Prioritize recent information (2023-2026).
Include citation hints where possible."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert research assistant. Provide accurate, well-sourced information formatted for infographic creation."
            },
            {"role": "user", "content": research_prompt}
        ]

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/infographic-generator",
                "X-Title": "Infographic Research"
            }

            payload = {
                "model": "perplexity/sonar-pro",
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.1,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                self._log(f"Research request failed: {response.status_code}")
                return {"success": False, "error": f"API error: {response.status_code}"}

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                self._log(f"Research complete: {len(content)} chars")
                return {
                    "success": True,
                    "content": content,
                    "sources": result.get("search_results", []),
                    "model": "perplexity/sonar-pro"
                }
            else:
                return {"success": False, "error": "No response from research model"}

        except Exception as e:
            self._log(f"Research failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _enhance_prompt_with_research(self, user_prompt: str, research_data: Dict[str, Any]) -> str:
        """Enhance the user prompt with researched information."""
        if not research_data.get("success") or not research_data.get("content"):
            return user_prompt

        return f"""{user_prompt}

RESEARCHED DATA AND FACTS (use these in the infographic):
{research_data['content']}

Use the above researched facts, statistics, and data points to create an accurate, informative infographic.
Incorporate specific numbers, percentages, and dates from the research."""

    # ========== KIE AI API METHODS ==========

    def _create_task(self, prompt: str,
                     image_inputs: Optional[List[str]] = None,
                     aspect_ratio: str = "auto",
                     resolution: str = "2K",
                     output_format: str = "png",
                     google_search: bool = False) -> Dict[str, Any]:
        """Create a generation task on Kie AI.

        Args:
            prompt: Text description of the image to generate
            image_inputs: Optional list of reference image URLs
            aspect_ratio: Aspect ratio (1:1, 9:16, 16:9, auto, etc.)
            resolution: Resolution (1K, 2K, 4K)
            output_format: Output format (jpg, png)
            google_search: Use Google Web Search grounding

        Returns:
            Dict with taskId or error info
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        input_params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "google_search": google_search,
            "resolution": resolution,
            "output_format": output_format,
        }

        if image_inputs:
            input_params["image_input"] = image_inputs

        payload = {
            "model": "nano-banana-2",
            "input": input_params
        }

        self._log(f"Creating Nano Banana 2 task (resolution: {resolution}, ratio: {aspect_ratio})...")
        self._log(f"Prompt length: {len(prompt)} chars")

        try:
            response = requests.post(
                self.KIE_CREATE_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            result = response.json()

            if response.status_code != 200:
                error_msg = result.get("msg", f"HTTP {response.status_code}")
                self._log(f"Task creation failed: {error_msg}")
                return {"success": False, "error": error_msg, "code": response.status_code}

            if result.get("code") == 200 and result.get("data", {}).get("taskId"):
                task_id = result["data"]["taskId"]
                self._log(f"Task created: {task_id}")
                return {"success": True, "taskId": task_id}
            else:
                error_msg = result.get("msg", "Unknown error")
                return {"success": False, "error": error_msg}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _poll_task(self, task_id: str,
                   max_wait: int = 300,
                   poll_interval: int = 5) -> Dict[str, Any]:
        """Poll for task completion.

        Args:
            task_id: The task ID to poll
            max_wait: Maximum wait time in seconds
            poll_interval: Seconds between polls

        Returns:
            Dict with result URLs or error info
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        self._log(f"Polling task {task_id[:16]}... (max {max_wait}s)")

        start_time = time.time()

        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(
                    self.KIE_STATUS_URL,
                    params={"taskId": task_id},
                    headers=headers,
                    timeout=30
                )

                result = response.json()

                if result.get("code") != 200:
                    error_msg = result.get("msg", f"HTTP {response.status_code}")
                    return {"success": False, "error": error_msg}

                data = result.get("data", {})
                state = data.get("state", "unknown")

                if state == "success":
                    result_json_str = data.get("resultJson", "{}")
                    try:
                        result_json = json.loads(result_json_str)
                    except (json.JSONDecodeError, TypeError):
                        result_json = {}

                    result_urls = result_json.get("resultUrls", [])
                    cost_time = data.get("costTime", 0)

                    self._log(f"Task complete! ({cost_time}ms, {len(result_urls)} image(s))")

                    return {
                        "success": True,
                        "urls": result_urls,
                        "costTime": cost_time,
                        "state": state
                    }

                elif state == "fail":
                    fail_msg = data.get("failMsg", "Unknown failure")
                    fail_code = data.get("failCode", "")
                    self._log(f"Task failed: {fail_code} - {fail_msg}")
                    return {
                        "success": False,
                        "error": f"{fail_code}: {fail_msg}",
                        "state": state
                    }

                else:
                    elapsed = int(time.time() - start_time)
                    self._log(f"  Status: {state} ({elapsed}s elapsed)")
                    time.sleep(poll_interval)

            except Exception as e:
                self._log(f"Poll error: {str(e)}")
                time.sleep(poll_interval)

        return {"success": False, "error": f"Timed out after {max_wait}s"}

    def _download_image(self, url: str, output_path: str) -> bool:
        """Download image from URL to local file."""
        try:
            self._log(f"Downloading image from {url[:60]}...")
            response = requests.get(url, timeout=60, stream=True)

            if response.status_code != 200:
                self._log(f"Download failed: HTTP {response.status_code}")
                return False

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output_path)
            self._log(f"Downloaded: {output_path} ({file_size:,} bytes)")
            return True

        except Exception as e:
            self._log(f"Download error: {str(e)}")
            return False

    # ========== PROMPT BUILDING ==========

    def _calculate_aspect_ratio(self, prompt: str, infographic_type: Optional[str] = None) -> str:
        """Determine the best aspect ratio for the infographic."""
        if infographic_type == "social":
            return "1:1"
        elif infographic_type in ("resume", "list", "timeline", "hierarchical"):
            return "9:16"
        elif infographic_type in ("comparison", "process"):
            return "16:9"

        # Default: auto-detect based on content density
        word_count = len(prompt.split())
        if word_count < 30:
            return "3:4"
        elif word_count < 80:
            return "9:16"
        else:
            return "9:16"

    def _build_generation_prompt(self, user_prompt: str,
                                  infographic_type: Optional[str] = None,
                                  style: Optional[str] = None,
                                  palette: Optional[str] = None,
                                  background: str = "white") -> str:
        """Build the full generation prompt."""

        parts = []
        parts.append(self.INFOGRAPHIC_GUIDELINES)

        # Add type-specific guidelines
        if infographic_type and infographic_type in INFOGRAPHIC_TYPES:
            type_config = INFOGRAPHIC_TYPES[infographic_type]
            parts.append(f"\nINFOGRAPHIC TYPE: {type_config['name']}")
            parts.append(type_config['guidelines'])

        # Add style preset
        if style and style in STYLE_PRESETS:
            style_config = STYLE_PRESETS[style]
            parts.append(f"\nSTYLE: {style_config['name']}")
            parts.append(f"Colors: {style_config['colors']}")
            parts.append(f"Design: {style_config['description']}")

        # Add palette
        if palette and palette in PALETTE_PRESETS:
            palette_config = PALETTE_PRESETS[palette]
            parts.append(f"\nCOLORBLIND-SAFE PALETTE: {palette_config['name']}")
            parts.append(f"Use these colors: {palette_config['colors']}")

        # Aesthetics
        parts.append(f"\nBACKGROUND: Premium {background} background. Flat and clean.")
        parts.append("AESTHETICS: Ultra-minimalist. Massive empty whitespace. No clutter.")
        parts.append("TYPOGRAPHY: Giant bold stark sans-serif headlines. Very tiny, sparse supplementary text.")
        parts.append("VIBE: High-end business magazine (like Monocle or Fast Company).")

        # The actual content
        parts.append(f"\nTOPIC & CONTENT:\n{user_prompt}")

        parts.append("\nFinal instruction: Generate a flat, clean, jaw-dropping minimalist infographic. No watermarks. No overlapping text. No meta-content visible.")

        return "\n".join(parts)

    # ========== GENERATION ==========

    def generate_image(self, prompt: str,
                       aspect_ratio: str = "auto",
                       resolution: str = "2K",
                       output_format: str = "png",
                       image_inputs: Optional[List[str]] = None,
                       google_search: bool = False,
                       max_wait: int = 300) -> Optional[List[str]]:
        """Generate an image using Nano Banana 2.

        Returns list of result image URLs on success, None on failure.
        """
        self._last_error = None

        # Step 1: Create the task
        task_result = self._create_task(
            prompt=prompt,
            image_inputs=image_inputs,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
            google_search=google_search
        )

        if not task_result.get("success"):
            self._last_error = task_result.get("error", "Task creation failed")
            print(f"  Task creation failed: {self._last_error}")
            return None

        task_id = task_result["taskId"]

        # Step 2: Poll for results
        poll_result = self._poll_task(task_id, max_wait=max_wait)

        if not poll_result.get("success"):
            self._last_error = poll_result.get("error", "Task polling failed")
            print(f"  Task failed: {self._last_error}")
            return None

        urls = poll_result.get("urls", [])
        if not urls:
            self._last_error = "No image URLs in result"
            return None

        self._log(f"Generated {len(urls)} image(s)")
        return urls

    # ========== QUALITY REVIEW (Optional) ==========

    def review_image_url(self, image_url: str, original_prompt: str,
                         infographic_type: Optional[str],
                         iteration: int, doc_type: str = "default",
                         max_iterations: int = 3) -> Tuple[str, float, bool]:
        """Review generated infographic using OpenRouter (optional).

        If OPENROUTER_API_KEY is not set, returns a default passing score.
        """
        if not self.openrouter_key:
            self._log("Skipping review - OPENROUTER_API_KEY not set")
            return "Image generated (review skipped - no OpenRouter key)", 8.0, False

        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(),
                                                 self.QUALITY_THRESHOLDS["default"])

        type_name = "general"
        if infographic_type and infographic_type in INFOGRAPHIC_TYPES:
            type_name = INFOGRAPHIC_TYPES[infographic_type]["name"]

        review_prompt = f"""You are an expert infographic designer reviewing a generated infographic for quality.

ORIGINAL REQUEST: {original_prompt}
INFOGRAPHIC TYPE: {type_name}
QUALITY THRESHOLD: {threshold}/10
ITERATION: {iteration}/{max_iterations}

Evaluate this infographic on these criteria:

1. **Visual Hierarchy & Layout** (0-2 points)
2. **Typography & Readability** (0-2 points)
3. **Data Visualization** (0-2 points)
4. **Color & Accessibility** (0-2 points)
5. **Overall Impact & Anti-Pattern Check** (0-2 points)

RESPOND IN THIS EXACT FORMAT:
SCORE: [total score 0-10]

STRENGTHS:
- [strength 1]
- [strength 2]

ISSUES:
- [issue 1 if any]

SPECIFIC_IMPROVEMENTS:
- [specific improvement 1]

VERDICT: [ACCEPTABLE or NEEDS_IMPROVEMENT]

If score >= {threshold}, the infographic is ACCEPTABLE."""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": review_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/infographic-generator",
                "X-Title": "Infographic Review"
            }

            payload = {
                "model": "google/gemini-2.5-flash",
                "messages": messages
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                return "Review failed (API error)", 7.5, False

            result = response.json()
            choices = result.get("choices", [])
            if not choices:
                return "Image generated successfully", 7.5, False

            content = choices[0].get("message", {}).get("content", "")

            if isinstance(content, list):
                text_parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
                content = "\n".join(text_parts)

            # Extract score
            score = 7.5
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))

            needs_improvement = "NEEDS_IMPROVEMENT" in content.upper() or score < threshold

            self._log(f"Review: Score {score}/10 (threshold: {threshold})")

            return (content if content else "Image generated successfully",
                    score, needs_improvement)

        except Exception as e:
            self._log(f"Review skipped: {str(e)}")
            return "Image generated (review skipped)", 7.5, False

    def improve_prompt(self, original_prompt: str, critique: str,
                      infographic_type: Optional[str],
                      style: Optional[str],
                      palette: Optional[str],
                      background: str,
                      iteration: int) -> str:
        """Improve the generation prompt based on critique."""
        parts = [self.INFOGRAPHIC_GUIDELINES]

        if infographic_type and infographic_type in INFOGRAPHIC_TYPES:
            type_config = INFOGRAPHIC_TYPES[infographic_type]
            parts.append(f"\nINFOGRAPHIC TYPE: {type_config['name']}")
            parts.append(type_config['guidelines'])

        if style and style in STYLE_PRESETS:
            style_config = STYLE_PRESETS[style]
            parts.append(f"\nSTYLE: {style_config['name']}")
            parts.append(f"Colors: {style_config['colors']}")
            parts.append(f"Design: {style_config['description']}")

        if palette and palette in PALETTE_PRESETS:
            palette_config = PALETTE_PRESETS[palette]
            parts.append(f"\nCOLORBLIND-SAFE PALETTE: {palette_config['name']}")
            parts.append(f"Use these colors: {palette_config['colors']}")

        parts.append(f"\nUSER REQUEST: {original_prompt}")
        parts.append(f"\nBackground: {background} background")

        parts.append(f"""
ITERATION {iteration}: Based on previous review, address these specific improvements:
{critique}

Generate an improved version that:
1. Fixes ALL the issues mentioned in the review
2. Maintains the requested infographic type and style
3. Ensures professional, publication-ready quality
4. Has no visual bugs, overlapping elements, or readability issues
""")

        return "\n".join(parts)

    # ========== MAIN WORKFLOW ==========

    def generate_iterative(self, user_prompt: str, output_path: str,
                          infographic_type: Optional[str] = None,
                          style: Optional[str] = None,
                          palette: Optional[str] = None,
                          background: str = "white",
                          iterations: int = 3,
                          doc_type: str = "default",
                          research: bool = False,
                          resolution: str = "2K",
                          output_format: str = "png",
                          google_search: bool = False,
                          image_inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate infographic with smart iterative refinement via Nano Banana 2.

        Only regenerates if the quality score is below the threshold
        (requires OPENROUTER_API_KEY for review; otherwise single-pass).
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = output_path.stem
        extension = output_path.suffix or f".{output_format}"

        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(),
                                                 self.QUALITY_THRESHOLDS["default"])

        # Determine aspect ratio
        aspect_ratio = self._calculate_aspect_ratio(user_prompt, infographic_type)

        type_name = infographic_type if infographic_type else "general"
        style_name = style if style else "default"

        results = {
            "user_prompt": user_prompt,
            "infographic_type": infographic_type,
            "style": style,
            "palette": palette,
            "doc_type": doc_type,
            "quality_threshold": threshold,
            "model": "nano-banana-2",
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "research_enabled": research,
            "research_data": None,
            "iterations": [],
            "final_image": None,
            "final_score": 0.0,
            "success": False,
            "early_stop": False,
            "early_stop_reason": None
        }

        print(f"\n{'='*60}")
        print(f"Generating Infographic with Nano Banana 2 (Kie AI)")
        print(f"{'='*60}")
        print(f"Content: {user_prompt}")
        print(f"Type: {type_name}")
        print(f"Style: {style_name}")
        print(f"Resolution: {resolution}")
        print(f"Aspect Ratio: {aspect_ratio}")
        print(f"Research: {'Enabled' if research else 'Disabled'}")
        print(f"Review: {'Enabled (OpenRouter)' if self.openrouter_key else 'Disabled (no OpenRouter key)'}")
        print(f"Quality Threshold: {threshold}/10")
        print(f"Max Iterations: {iterations}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")

        # ===== RESEARCH PHASE =====
        enhanced_prompt = user_prompt
        if research:
            print(f"\n[Research Phase]")
            print("-" * 40)
            print(f"Researching topic for accurate data...")

            research_result = self.research_topic(user_prompt, infographic_type)

            if research_result.get("success"):
                print(f"  Research complete - gathered facts and statistics")
                results["research_data"] = research_result
                enhanced_prompt = self._enhance_prompt_with_research(user_prompt, research_result)

                research_path = output_dir / f"{base_name}_research.json"
                with open(research_path, "w") as f:
                    json.dump(research_result, f, indent=2)
                print(f"  Research saved: {research_path}")
            else:
                print(f"  Research failed: {research_result.get('error', 'Unknown error')}")
                print(f"  Proceeding with original prompt...")

        # Build initial prompt
        current_prompt = self._build_generation_prompt(
            enhanced_prompt, infographic_type, style, palette, background
        )

        for i in range(1, iterations + 1):
            print(f"\n[Iteration {i}/{iterations}]")
            print("-" * 40)

            # Generate image via Nano Banana 2
            print(f"  Generating with Nano Banana 2...")
            result_urls = self.generate_image(
                prompt=current_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format,
                image_inputs=image_inputs,
                google_search=google_search
            )

            if not result_urls:
                error_msg = self._last_error or "Generation failed"
                print(f"  Generation failed: {error_msg}")
                results["iterations"].append({
                    "iteration": i,
                    "success": False,
                    "error": error_msg
                })
                continue

            # Download the first result image
            image_url = result_urls[0]
            iter_path = output_dir / f"{base_name}_v{i}{extension}"

            if not self._download_image(image_url, str(iter_path)):
                print(f"  Failed to download image")
                results["iterations"].append({
                    "iteration": i,
                    "success": False,
                    "error": "Download failed"
                })
                continue

            print(f"  Saved: {iter_path}")

            # Review image (uses OpenRouter if available)
            print(f"  Reviewing quality...")
            critique, score, needs_improvement = self.review_image_url(
                image_url, user_prompt, infographic_type, i, doc_type, iterations
            )
            print(f"  Score: {score}/10 (threshold: {threshold}/10)")

            iteration_result = {
                "iteration": i,
                "image_path": str(iter_path),
                "image_url": image_url,
                "prompt_length": len(current_prompt),
                "critique": critique,
                "score": score,
                "needs_improvement": needs_improvement,
                "success": True
            }
            results["iterations"].append(iteration_result)

            # Check if quality is acceptable
            if not needs_improvement:
                print(f"\n  Quality meets threshold ({score} >= {threshold})")
                print(f"  No further iterations needed!")
                results["final_image"] = str(iter_path)
                results["final_score"] = score
                results["success"] = True
                results["early_stop"] = True
                results["early_stop_reason"] = f"Quality score {score} meets threshold {threshold}"
                break

            if i == iterations:
                print(f"\n  Maximum iterations reached")
                results["final_image"] = str(iter_path)
                results["final_score"] = score
                results["success"] = True
                break

            # Quality below threshold - improve prompt
            print(f"\n  Quality below threshold ({score} < {threshold})")
            print(f"  Improving prompt based on feedback...")
            current_prompt = self.improve_prompt(
                user_prompt, critique, infographic_type, style, palette, background, i + 1
            )

        # Copy final version to output path
        if results["success"] and results["final_image"]:
            final_iter_path = Path(results["final_image"])
            if final_iter_path != output_path:
                import shutil
                shutil.copy(final_iter_path, output_path)
                print(f"\n  Final image: {output_path}")

        # Save review log
        log_path = output_dir / f"{base_name}_review_log.json"
        with open(log_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Review log: {log_path}")

        print(f"\n{'='*60}")
        print(f"Generation Complete!")
        print(f"Final Score: {results['final_score']}/10")
        if results.get("early_stop"):
            iterations_used = len([r for r in results['iterations'] if r.get('success')])
            print(f"Iterations Used: {iterations_used}/{iterations} (early stop)")
        print(f"{'='*60}\n")

        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate infographics using Kie AI Nano Banana 2 with smart iterative refinement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a list infographic
  python generate_infographic_ai.py "5 benefits of meditation" -o benefits.png --type list

  # Generate a timeline with corporate style
  python generate_infographic_ai.py "Company history 2010-2025" -o timeline.png --type timeline --style corporate

  # Generate with colorblind-safe palette
  python generate_infographic_ai.py "Heart disease stats" -o stats.png --type statistical --palette wong

  # Generate with RESEARCH for accurate data
  python generate_infographic_ai.py "Global AI market 2025" -o ai_market.png --type statistical --research

  # High resolution 4K output
  python generate_infographic_ai.py "Process diagram" -o process.png --type process --resolution 4K

Infographic Types:
  statistical, timeline, process, comparison, list,
  geographic, hierarchical, anatomical, resume, social

Style Presets:
  corporate, healthcare, technology, nature, education, marketing, finance, nonprofit

Colorblind-Safe Palettes:
  wong, ibm, tol

Environment:
  KIE_API_KEY           Kie AI API key (required) - https://kie.ai/api-key
  OPENROUTER_API_KEY    OpenRouter key (optional, for quality review)
        """
    )

    parser.add_argument("prompt", help="Description of the infographic content")
    parser.add_argument("-o", "--output", required=True,
                       help="Output image path (e.g., infographic.png)")
    parser.add_argument("--type", "-t", choices=list(INFOGRAPHIC_TYPES.keys()),
                       help="Infographic type preset")
    parser.add_argument("--style", "-s", choices=list(STYLE_PRESETS.keys()),
                       help="Industry style preset")
    parser.add_argument("--palette", "-p", choices=list(PALETTE_PRESETS.keys()),
                       help="Colorblind-safe palette")
    parser.add_argument("--background", "-b", default="white",
                       help="Background color (default: white)")
    parser.add_argument("--iterations", type=int, default=3,
                       help="Maximum refinement iterations (default: 3)")
    parser.add_argument("--doc-type", default="default",
                       choices=["marketing", "report", "presentation", "social",
                               "internal", "draft", "default"],
                       help="Document type for quality threshold")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"],
                       help="Output resolution (default: 2K)")
    parser.add_argument("--format", default="png", choices=["png", "jpg"],
                       help="Output format (default: png)")
    parser.add_argument("--google-search", action="store_true",
                       help="Use Google Web Search grounding for real-time info")
    parser.add_argument("--image-input", action="append",
                       help="Reference image URL(s) to transform or use as reference (can specify multiple)")
    parser.add_argument("--api-key", help="Kie AI API key (or set KIE_API_KEY)")
    parser.add_argument("--openrouter-key", help="OpenRouter API key for quality review (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--research", "-r", action="store_true",
                       help="Research topic first using Perplexity Sonar (requires OPENROUTER_API_KEY)")

    args = parser.parse_args()

    # Check for API key
    api_key = args.api_key or os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not set")
        print("\nGet your API key from: https://kie.ai/api-key")
        print("\nSet it with:")
        print("  export KIE_API_KEY='your_api_key'")
        print("\nOr use --api-key flag")
        sys.exit(1)

    openrouter_key = args.openrouter_key or os.getenv("OPENROUTER_API_KEY")

    try:
        generator = InfographicGenerator(
            api_key=api_key,
            openrouter_key=openrouter_key,
            verbose=args.verbose
        )
        results = generator.generate_iterative(
            user_prompt=args.prompt,
            output_path=args.output,
            infographic_type=args.type,
            style=args.style,
            palette=args.palette,
            background=args.background,
            iterations=args.iterations,
            doc_type=args.doc_type,
            research=args.research,
            resolution=args.resolution,
            output_format=args.format,
            google_search=args.google_search,
            image_inputs=args.image_input,
        )

        if not results["success"]:
            print("Generation failed!")
            sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)


if __name__ == "__main__":
    main()
