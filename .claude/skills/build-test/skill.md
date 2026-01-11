# Build & Test Skill

PDF generation, visual regression testing, and optimization.

## Trigger
Run `/build` when:
- Need to rebuild PDF
- Testing template changes
- Checking build errors
- Comparing before/after

## Commands

### Quick Build
```bash
make worldbuilding
```

### Build with Debug Output
```bash
make worldbuilding-tex  # Just generate .tex, don't compile PDF
```

### Check Page Count
```bash
pdfinfo worldbuilding-bible/export/worldbuilding-bible-de.pdf | grep Pages
```

### Render Page to PNG
```bash
python3 scripts/layout-check.py --page 5 --no-build --dpi 150
```

### Render All Pages
```bash
python3 scripts/layout-check.py --all-pages --no-build
```

### Compare Two PDFs
```bash
diff-pdf-visually old.pdf new.pdf
```

## Build Pipeline

```
worldbuilding-bible/de/*.md
         ↓ (Pandoc + Lua filter)
worldbuilding-bible/export/worldbuilding-bible-de.tex
         ↓ (LuaLaTeX, 2 passes)
worldbuilding-bible/export/worldbuilding-bible-de.pdf
```

## Common Build Errors

### "Undefined control sequence"
- Missing package or typo in macro name
- Check template-latex.tex for typos

### "Too many unprocessed floats"
- Too many figures queued
- Add `\clearpage` or reduce figure density

### "Overfull hbox"
- Content wider than column
- Usually images - check `width=\columnwidth`

### "Font not found"
- Check `fc-list | grep FontName`
- May need to install font system-wide

## Optimization

### Image Optimization (already set up)
```bash
python3 scripts/optimize-images.py
```

### PDF Size Check
```bash
du -h worldbuilding-bible/export/worldbuilding-bible-de.pdf
```
Target: < 30MB for reasonable performance

### Compress PDF (if needed)
```bash
qpdf --linearize input.pdf output.pdf
```

## Visual Regression Workflow

1. Save current PDF as baseline
2. Make changes
3. Rebuild
4. Compare with `diff-pdf-visually`
5. Review differences manually
