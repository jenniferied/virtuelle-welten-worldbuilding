# Layout Tools Research (January 2026)

## Requirements
- 16:9 fixed pages (not scrollable)
- Automatic/dynamic layout (content fits to margins)
- Beautiful visual output
- Code/CLI driven (no manual GUI)
- PDF export

---

## TOP RECOMMENDATIONS

### 1. Gamma API (Best for Quality + Automation)
- **URL:** https://gamma.app / https://developers.gamma.app
- **Type:** Commercial AI presentation platform with API
- **API Status:** v1.0 GA (November 2025)
- **Key Features:**
  - Full REST API for programmatic generation
  - Automatic beautiful layouts (their core strength)
  - Export to PDF, PPTX via API
  - Customizable themes, tone, audience, detail level
  - 60+ languages supported
  - 16:9 format supported (`"presentationStyle": "16x9"`)
  - Generate from prompts, notes, or structured content
- **Requirements:** Pro account ($8/month) or higher
- **Rate Limits:** Hundreds per hour (very generous)
- **Slide Limits:** Pro: 1-60 slides, Ultra: 1-75 slides
- **Docs:** https://developers.gamma.app/docs/getting-started

**Python Example:**
```python
import requests

response = requests.post(
    "https://public-api.gamma.app/v1.0/generations",
    headers={
        "X-API-Key": "sk-gamma-YOUR-KEY",
        "Content-Type": "application/json"
    },
    json={
        "inputText": "Soviet-inspired worldbuilding bible...",
        "textMode": "generate",
        "format": "presentation",
        "presentationStyle": "16x9",
        "themeId": "Noir",  # dark theme
        "numCards": 20,
        "exportAs": "pdf"
    }
)
```

- **VERDICT:** Best automatic layout quality, proper API, reasonable cost

### 2. Presenton (Best Open Source)
- **URL:** https://presenton.ai
- **GitHub:** https://github.com/presenton/presenton (3.6k stars)
- **Type:** Open-source AI presentation generator
- **Key Features:**
  - Self-hosted via Docker: `docker run -p 5000:80 ghcr.io/presenton/presenton:latest`
  - REST API at `/api/v1/ppt/presentation/generate`
  - Export to PPTX, PDF
  - Supports OpenAI, Gemini, Claude, or local Ollama models
  - Custom templates from existing PPTX
  - Tone options: casual, professional, funny, educational, sales_pitch
  - Verbosity: concise, standard, text-heavy
- **Requirements:** Self-host + bring your own LLM API key
- **Example:**
  ```python
  import requests
  response = requests.post(
      "http://localhost:5000/api/v1/ppt/presentation/generate",
      json={
          "prompt": "Soviet-inspired worldbuilding bible for eternal winter setting",
          "n_slides": 20,
          "theme": "dark",
          "export_as": "pdf"
      }
  )
  ```
- **VERDICT:** Full control, no subscription, requires setup

### 3. Slidev + Marp (Best Markdown-Native)
- **Slidev URL:** https://sli.dev
- **Marp URL:** https://marp.app
- **Type:** Markdown-based presentation tools
- **Key Features:**
  - Fixed 16:9 canvas
  - Auto-fit text components (Slidev)
  - CLI export: `slidev export` or `marp --pdf`
  - Custom CSS themes
  - Hot reload preview
- **Requirements:** Node.js / npm
- **VERDICT:** Best if you want to write Markdown directly, need custom layouts

---

## Comparison Matrix

| Tool | Auto Layout | API/CLI | PDF Export | Cost | Setup |
|------|-------------|---------|------------|------|-------|
| **Gamma** | Excellent | REST API | Yes | $8/mo | None |
| **Presenton** | Good | REST API | Yes | Free (self-host) | Docker |
| **Slidev** | Manual+CSS | CLI | Yes | Free | npm |
| **Marp** | Manual+CSS | CLI | Yes | Free | npm |

---

## Establishment & Traction

| Tool | GitHub Stars | Users | Funding | Team | Founded |
|------|-------------|-------|---------|------|---------|
| **Gamma** | N/A (closed) | **70 million** | $87M ($2.1B valuation) | 52 people | 2020 |
| **Presenton** | **3,637** | Unknown | Self-funded | Small OSS team | ~2024 |
| **Slidev** | **43,500** | Unknown | OSS (no funding) | 250 contributors | 2021 |
| **Marp** | **~8,000** | Unknown | OSS (no funding) | Small team | 2016 |
| **Beautiful.ai** | N/A (closed) | Unknown | $16M ($5.8M val) | 93 people | 2016 |

### Gamma (Most Established)
- **70 million users** generating 1M+ pieces of content/day
- **$100M ARR** (annual recurring revenue)
- **$2.1B valuation** (unicorn as of Nov 2025)
- Backed by Andreessen Horowitz, Accel
- Profitable for 2+ years
- Source: [TechCrunch](https://techcrunch.com/2025/11/10/ai-powerpoint-killer-gamma-hits-2-1b-valuation-100m-arr-founder-says/)

### Presenton (Emerging OSS)
- **3,637 GitHub stars**, 718 forks, 45 contributors
- Active development (last updated Jan 2026)
- Has Python SDK and JS SDK
- Apache 2.0 license
- Source: [GitHub](https://github.com/presenton/presenton)

### Slidev (Mature OSS)
- **43,500 GitHub stars** - very popular in dev community
- 250 open source contributors
- 7,276 weekly npm downloads
- Created by Anthony Fu (Vue/Vite core team)
- Source: [GitHub](https://github.com/slidevjs/slidev)

### Marp (Stable OSS)
- ~8,000 GitHub stars across repos
- 11,818 weekly npm downloads (marpit core)
- Mature ecosystem since 2016
- VS Code extension available
- Source: [GitHub](https://github.com/marp-team/marp)

---

## Ruled Out

| Tool | Reason |
|------|--------|
| LaTeX/Typst | Manual layout, slow iteration |
| Canva | GUI-only, no code automation |
| Figma | GUI-only, no code automation |
| InDesign | GUI-only, expensive |
| VitePress | Web-scroll, not fixed pages |
| Paged.js | Web-scroll heritage, page fit issues |
| Beautiful.ai | No public API found |
| Alai | Limited API documentation |

---

## Recommended Approach

**For best automatic layout:** Use Gamma API
- Sign up for Pro ($8/mo)
- Use their REST API to generate from your Markdown content
- Export directly to PDF

**For full control / free:** Use Presenton
- Self-host with Docker
- Use your existing OpenAI/Claude API key
- Full control over prompts and output

**For Markdown purists:** Use Slidev
- Write in Markdown
- Create custom Vue layouts for your Soviet aesthetic
- More manual but full control

---

## Updated: 2026-01-21
