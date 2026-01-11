# Layout Skill

Fixes image placement, column balancing, and white space issues in multi-column LaTeX documents.

## Trigger
Run `/layout` when:
- Images overflow columns or look too small
- Pages have awkward white space
- Text doesn't balance across columns
- Adding new images to multi-column sections
- User reports layout issues

## Diagnosis Steps

1. **Build and check page count**
   ```bash
   make worldbuilding
   pdfinfo worldbuilding-bible/export/worldbuilding-bible-de.pdf | grep Pages
   ```

2. **Render specific page for inspection**
   ```bash
   python3 scripts/layout-check.py --page N --no-build
   ```

3. **Identify issue type**
   - White space: Too little content for layout, or wrong column count
   - Overflow: Image too large for column
   - Cramped: Too much content, needs page break
   - Orphaned: Heading separated from content

## Common Fixes

### White Space Issues
- **Too few columns**: Change `page-3` to `page-2` or `page-1`
- **Not enough content**: Add descriptive text, don't leave images alone
- **Wrong break**: Remove `new-page` or add one earlier

### Image Issues
- **Overflow**: Use `width=\columnwidth` (not fixed sizes)
- **Too small**: Check max height constraint in template
- **Cropped badly**: Adjust `Clip*` parameters or use different image

### Column Balance
- Use `columns-N` (balanced) for text-heavy sections
- Use `page-N` (unbalanced) for image galleries
- Mix text and images to fill columns naturally

## Template Reference

### Figure Macros (template-latex.tex lines 418-490)
- `\colfig{path}{caption}{list-caption}` - single column
- `\colpairfig{img1}{img2}{caption}{list-caption}` - side-by-side
- `\coldualfig{img1}{img2}{caption}{list-caption}` - stacked
- `\colgridfig{i1}{i2}{i3}{i4}{caption}{list-caption}` - 2x2
- `\coltriplefig{i1}{i2}{i3}{caption}{list-caption}` - 3 stacked

### Layout Environments
- `columns-1` through `columns-4` - balanced (multicols)
- `page-1` through `page-4` - unbalanced (multicols*)

## Files to Modify
- `worldbuilding-bible/de/*.md` - Content and layout divs
- `worldbuilding-bible/template-latex.tex` - Macros and environments
- `scripts/build-worldbuilding.py` - Lua filter for div conversion

## After Fixing
1. Rebuild: `make worldbuilding`
2. Check affected pages visually
3. Note fix in discoveries.md
