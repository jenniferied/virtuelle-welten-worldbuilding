# Multi-Column Image Layout Research

**Date**: January 2026
**Status**: Research Complete

## Problem Statement

Images in multi-column LaTeX layouts do not scale properly. Current implementation uses fixed `max height` percentages that don't adapt to:
- Image aspect ratios
- Available column space
- Content flow requirements

## What Has Been Tried

### LaTeX Packages Tested

| Package | File | Approach | Result |
|---------|------|----------|--------|
| `multicol` | test-multicol-v1 to v4 | Standard multi-column with fixed heights | Partial - works but heights don't adapt |
| `paracol` | test-paracol.tex | Parallel columns with minipage | Similar issues with fixed heights |
| `flowfram` | test-flowfram-v1, v2 | Flow frames with explicit positioning | Complex, not flexible enough |
| `vwcol` | test-vwcol.tex | Variable-width columns | Sequential fill, not optimal |

### Current Template Approach (template-latex.tex)

Lines 418-490 define figure macros using:
```latex
\includegraphics[width=0.92\columnwidth, keepaspectratio, max height=0.24\textheight]{...}
```

**Problems**:
1. Fixed height constraints (0.24, 0.17, 0.09 of textheight)
2. No automatic cropping for mismatched aspect ratios
3. Landscape images appear too small
4. Portrait images may overflow

## Research Findings

### 1. LaTeX Solutions

#### adjustbox Package
The `adjustbox` package provides `Clip*` for intelligent cropping:

```latex
\adjincludegraphics[
  width=\columnwidth,
  max height=0.35\textheight,
  Clip*={.5\width-.5\columnwidth} {.3\height} {.5\width-.5\columnwidth} {0},
  keepaspectratio
]{image.png}
```

**Reference**: [adjustbox documentation](https://mirrors.ibiblio.org/CTAN/macros/latex/contrib/adjustbox/adjustbox.pdf)

#### trimclip Package
Part of adjustbox bundle, allows proportional trimming:

```latex
\adjincludegraphics[trim={0 {.2\height} 0 {.2\height}}, clip]{image.png}
```

**Reference**: [trimclip documentation](https://ctan.math.illinois.edu/macros/latex/contrib/adjustbox/trimclip.pdf)

### 2. Typst Ecosystem (Alternative)

Typst offers superior auto-layout packages:

#### tessera Package
Automatic masonry/matrix layouts:
- Calculates exact dimensions based on aspect ratios
- Handles mixed landscape/portrait automatically
- Supports gutter/gap configuration

```typst
#import "@preview/tessera:0.1.0": masonry

#masonry(
  (image("cat1.jpg"), image("cat2.jpg")),
  image("cat3.jpg"),
  gutter: 1em,
)
```

**Reference**: [tessera on Typst Universe](https://typst.app/universe/package/tessera)

#### oasis-align Package
Equal-height side-by-side content:
- Uses mathematical optimization for fixed aspect ratios
- Perfect for pairing images of different proportions

```typst
#import "@preview/oasis-align:0.3.2": *

#oasis-align-images(image1, image2)
```

**Reference**: [oasis-align on Typst Universe](https://typst.app/universe/package/oasis-align)

### 3. PDF Visual Assessment Tools

#### diff-pdf (C++)
Binary comparison with visual diff output:
```bash
diff-pdf --output-diff=diff.pdf before.pdf after.pdf
```
**GitHub**: https://github.com/vslavik/diff-pdf

#### diff-pdf-visually (Python)
Uses ImageMagick + pdftocairo for pixel comparison:
```bash
pip3 install diff-pdf-visually
diff-pdf-visually before.pdf after.pdf
```
**PyPI**: https://pypi.org/project/diff-pdf-visually/

#### pdf-visual-diff (JavaScript)
Snapshot-based regression testing:
```bash
npx pdf-visual-diff compare snapshot.png current.pdf
```
**npm**: https://www.npmjs.com/package/pdf-visual-diff

## Recommended Solution

### Phase 1: Improve Existing LaTeX (Immediate)

1. Add smart figure macros using adjustbox:

```latex
% Smart column figure with optional cropping
\newcommand{\smartcolimg}[3]{%
  % #1 = image path
  % #2 = text caption
  % #3 = list caption
  \par\vspace{2mm}\noindent\centering
  \adjincludegraphics[
    width=0.95\columnwidth,
    max height=0.38\textheight,
    min height=3cm,
    keepaspectratio
  ]{#1}%
  \par\nopagebreak[4]
  \captionof{figure}[#3]{#2}%
  \par\vspace{2mm}\raggedright
}

% Fill-crop variant (crops to fit exactly)
\newcommand{\smartcolfill}[4][center]{%
  % #1 = crop gravity (north, center, south)
  % #2 = image path
  % #3 = text caption
  % #4 = list caption
  \par\vspace{2mm}\noindent\centering
  \adjincludegraphics[
    width=0.95\columnwidth,
    height=0.28\textheight,
    trim=0 {(\height-0.28\textheight)/2} 0 {(\height-0.28\textheight)/2},
    clip
  ]{#2}%
  \par\nopagebreak[4]
  \captionof{figure}[#4]{#3}%
  \par\vspace{2mm}\raggedright
}
```

2. Add visual assessment to build pipeline:

```python
# In scripts/build-worldbuilding.py
def render_preview(pdf_path: Path, page: int = 1) -> Path:
    """Render PDF page to PNG for visual inspection."""
    preview = pdf_path.with_suffix(f".page{page}.png")
    subprocess.run([
        "pdftocairo", "-png", "-r", "150",
        "-f", str(page), "-l", str(page),
        str(pdf_path), str(preview.with_suffix(""))
    ])
    return preview
```

### Phase 2: Consider Typst Migration (Long-term)

If LaTeX solutions remain problematic, consider migrating to Typst:

**Pros**:
- Much simpler syntax
- Superior auto-layout (tessera, oasis-align)
- Faster compilation
- Modern ecosystem

**Cons**:
- Different syntax (learning curve)
- Less mature than LaTeX
- Fewer fonts/packages

### Phase 3: Self-Improving Skill

The `/layout` Claude skill should:
1. Build the PDF
2. Render preview images
3. Ask user about visual quality
4. Record what works and what doesn't
5. Update its own documentation

## Implementation Checklist

- [ ] Add adjustbox smart macros to template
- [ ] Update chapter files to use new macros
- [ ] Add PDF preview rendering to build script
- [ ] Install diff-pdf-visually for regression testing
- [ ] Document successful patterns in skill file
- [ ] Consider Typst prototype for comparison

## References

1. [Multiple Columns Layout - LaTeX Cloud Studio](https://resources.latex-cloud-studio.com/learn/latex/formatting/multiple-columns)
2. [adjustbox Package Documentation](https://mirrors.ibiblio.org/CTAN/macros/latex/contrib/adjustbox/adjustbox.pdf)
3. [tessera - Typst Universe](https://typst.app/universe/package/tessera)
4. [oasis-align - Typst Universe](https://typst.app/universe/package/oasis-align)
5. [diff-pdf - GitHub](https://github.com/vslavik/diff-pdf)
6. [diff-pdf-visually - PyPI](https://pypi.org/project/diff-pdf-visually/)
7. [LearnLaTeX - Including Graphics](https://www.learnlatex.org/en/lesson-07)
8. [PhysicsRead - Resize Figures in LaTeX](https://www.physicsread.com/latex-figure-size/)
