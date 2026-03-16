# AIOS — AI Operating System

**Starter Kit** — Your personal AI business operating system, built on Claude Code.

AIOS turns Claude Code into a full business OS. It remembers your preferences, learns from feedback, maintains itself between sessions, and executes real tasks through a growing library of skills.

> **What's included now:** 1 skill — `infographics` (visual content generation via Kie AI).
> More skills are coming. This starter kit gives you the full framework to run them as they're released — or build your own.

---

## What You Get

- **Complete AIOS framework** — memory, feedback logging, session continuity, self-maintaining skill registry
- **1 ready-to-use skill**: `infographics` — generate professional, brand-consistent infographics via Kie AI Nano Banana 2
- **Extensible skill system** — drop a new skill folder into `skills/` and AIOS picks it up automatically
- **Brand-first workflow** — set your visual identity once, every infographic inherits it automatically
- **Memory and learning** — feedback is logged per skill and applied to every future run

---

## Quick Start

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- A terminal or IDE with Claude Code support (VS Code, Cursor, etc.)
- **For infographics**: `KIE_API_KEY` from [kie.ai](https://kie.ai/api-key) — required for image generation
- **Optional**: `OPENROUTER_API_KEY` — enables AI quality review and auto-refinement on infographics

### Setup (2 minutes)

1. **Clone or download this folder** to your local machine
2. **Set your API keys** in your terminal:
   ```bash
   export KIE_API_KEY=your_key_here
   export OPENROUTER_API_KEY=your_key_here  # optional
   ```
3. **Open the folder in your terminal or IDE**
4. **Start Claude Code** in the project directory
5. **Start working** — AIOS reads this setup automatically

---

## Current Skills

| Skill | What It Does | Requires |
|-------|-------------|---------|
| `infographics` | Generate brand-consistent infographics via Kie AI Nano Banana 2. Set up your brand once — every future infographic matches your visual identity automatically. | `KIE_API_KEY` |

> More skills are coming — content writing, LinkedIn posts, email sequences, SEO research, and more.
> When new skills drop, copy them into `skills/` and AIOS registers them automatically.

---

## How It Works

### Layer 1 — Skills (`skills/`)
The execution engine. Each skill is a self-contained folder with a `SKILL.md` that defines what it does, how it works, and what it needs. AIOS reads every skill at session start and routes your requests to the right one.

### Layer 2 — Memory (`context/`)
The agent's brain. AIOS tracks your preferences in `context/user.md`, logs feedback in `context/learnings.md`, and saves session notes in `context/memory/`. It picks up exactly where you left off every session.

### Layer 3 — Projects (`projects/`)
Where all deliverables land. Organized by date. Your output library grows automatically.

---

## Key Commands

| Say This | What Happens |
|----------|--------------|
| "create an infographic about X" | Runs the infographics skill (brand setup on first use) |
| "make an infographic for [Brand X] about Y" | Loads Brand X guideline and generates |
| "set up a new brand" | Runs brand onboarding for a new client or project |
| "wrap up" | Closes the session, logs feedback, saves memory |
| Any natural request | AIOS matches it to the right skill automatically |

---

## Adding New Skills

Drop a new folder with a `SKILL.md` into `skills/`. At the next session start, AIOS:

1. Reads the new skill
2. Checks for conflicts with existing skills
3. Registers it in the skill registry
4. Creates a feedback section in `context/learnings.md`
5. Confirms it's ready

Skills follow a standard format — see `CLAUDE.md` for the SKILL FORMAT STANDARD.

---

## Folder Structure

```
AIOS/
â”œâ”€â”€ CLAUDE.md                        â† Master system prompt (the brain)
â”œâ”€â”€ README.md                        â† This file
â”‚
â”œâ”€â”€ context/                         â† Agent memory and preferences
â”‚   â”œâ”€â”€ learnings.md                 â† Feedback log (applied to every skill run)
â”‚   â”œâ”€â”€ memory.md                    â† Long-term knowledge
â”‚   â””â”€â”€ memory/                      â† Session logs by date
â”‚
â”œâ”€â”€ skills/
â”‚   â””â”€â”€ infographics/                â† Current skill
â”‚       â”œâ”€â”€ SKILL.md                 â† Full skill definition and workflow
â”‚       â”œâ”€â”€ brands/                  â† Brand guideline files (one per brand)
â”‚       â”‚   â””â”€â”€ _TEMPLATE.md         â† Copy this to create a new brand
â”‚       â”œâ”€â”€ references/              â† Design principles, infographic types, color palettes
â”‚       â”œâ”€â”€ resources/               â† Nano Banana 2 API documentation
â”‚       â””â”€â”€ scripts/                 â† Python generation scripts
â”‚
â””â”€â”€ projects/                        â† All outputs land here
```

---

## Support

Built by Krishna Aggarwal. For questions, updates, or the Done-For-You setup service, reach out on [LinkedIn](https://www.linkedin.com/in/krishnaaggarwal16/).
