# Layout Assistant Skill

This skill helps with image layout in multi-column LaTeX documents for the worldbuilding bible.

## Core Problem

Images in multi-column layouts need to:
1. Scale automatically while respecting aspect ratios
2. Fit within column width and reasonable height constraints
3. Optionally crop to fill available space
4. Flow naturally with text in newspaper-style columns

## Current State

The project uses:
- **Markdown** sources in `worldbuilding-bible/de/`
- **Pandoc** with Lua filters for conversion
- **LuaLaTeX** for rendering with `multicol` package
- **Template**: `worldbuilding-bible/template-latex.tex`

Existing macros (lines 418-490):
- `\colfig{path}{caption}{list-caption}` - single column image
- `\colpairfig{img1}{img2}{caption}{list-caption}` - two side-by-side
- `\coldualfig{img1}{img2}{caption}{list-caption}` - two stacked
- `\colgridfig{i1}{i2}{i3}{i4}{caption}{list-caption}` - 2x2 grid
- `\coltriplefig{i1}{i2}{i3}{caption}{list-caption}` - three stacked

**Problem**: These use fixed `max height` percentages (0.24\textheight, 0.17\textheight, etc.) that don't adapt to image aspect ratios.

## Solution Options

### Option A: Enhanced LaTeX Macros (Recommended)

Use the `adjustbox` package with `Clip*` for intelligent cropping:

```latex
% Smart column figure that crops to fit column
\newcommand{\smartfig}[4][center]{%
  % #1 = crop position (center, north, south, etc.)
  % #2 = image path
  % #3 = text caption
  % #4 = list of figures caption
  \par\vspace{2mm}\noindent
  \centering
  \adjincludegraphics[
    width=\columnwidth,
    max height=0.35\textheight,
    Clip*={.5\width-.5\columnwidth} {0} {.5\width-.5\columnwidth} {0},
    keepaspectratio
  ]{#2}%
  \par\nopagebreak[4]
  \captionof{figure}[#4]{#3}%
  \par\vspace{2mm}
  \raggedright
}
```

### Option B: Typst Migration

Typst offers superior auto-layout with these packages:
- **tessera**: Masonry/matrix layouts for image galleries
- **oasis-align**: Equal-height side-by-side content

Example Typst:
```typst
#import "@preview/tessera:0.1.0": masonry
#import "@preview/oasis-align:0.3.2": *

#masonry(
  (image("cat1.jpg"), image("cat2.jpg")),
  image("cat3.jpg"),
  gutter: 1em,
)
```

### Option C: Python Pre-processor

Add image analysis to `scripts/build-worldbuilding.py`:

```python
from PIL import Image

def get_optimal_height(img_path: Path, col_width_mm: float = 93) -> str:
    """Calculate optimal max height based on aspect ratio."""
    with Image.open(img_path) as img:
        aspect = img.width / img.height
        # If landscape (wider than column), constrain by width
        if aspect > 1:
            return "0.25\\textheight"
        # If portrait, allow taller
        elif aspect < 0.7:
            return "0.40\\textheight"
        else:
            return "0.30\\textheight"
```

## When to Use This Skill

Run `/layout` when:
1. Images overflow their columns or look too small
2. Adding new images to multi-column sections
3. Page layout looks unbalanced
4. Testing new figure macros

## Workflow

1. **Analyze current layout**: Build PDF, check visually
2. **Identify issues**: Which images are problematic?
3. **Apply fix**: Adjust macro parameters or use smarter cropping
4. **Rebuild and compare**: Use `diff-pdf-visually` for regression testing
5. **Iterate**: Repeat until layout looks good

## Visual Assessment Tools

For automated PDF comparison:
```bash
# Install
pip3 install diff-pdf-visually

# Compare before/after
diff-pdf-visually old.pdf new.pdf
```

For rendering PDF to images:
```bash
# Using pdftocairo (from poppler)
pdftocairo -png -r 150 document.pdf preview
```

## Recommended Approach

1. Start with **Option A** (enhanced macros) for immediate improvement
2. Consider **Option B** (Typst) for major layout redesign
3. Use **Option C** (Python) for batch image processing

## Files to Modify

- `worldbuilding-bible/template-latex.tex` - Add smart figure macros
- `scripts/build-worldbuilding.py` - Add image analysis
- `worldbuilding-bible/de/*.md` - Update figure calls

## Self-Improvement Notes

After each use of this skill, document:
1. What layout problem was encountered
2. What solution was applied
3. Whether it worked
4. Any refinements needed

Add findings to this file for future reference.

---

## Iteration Log

*(Add entries below as solutions are tried)*

