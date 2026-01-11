# Layout Discoveries

Document what works and what doesn't for future reference.

---

## Session Log

*(Add entries as solutions are discovered)*

### Template: Entry Format
```
### YYYY-MM-DD: [Issue Type]
**Problem**: Describe what was wrong
**Solution**: What fixed it
**Files changed**: List files
**Result**: Did it work? Any trade-offs?
```

---

## Known Working Patterns

### Image Galleries
- Use `page-4` with raw LaTeX `\includegraphics` blocks
- Consistent spacing: `\vspace{3mm}` between images
- Captions with `{\footnotesize ... \hfill\textit{Credit}}`

### Text-Heavy Sections
- Use `columns-2` or `columns-3` (balanced)
- Mix in pull quotes or sidebars to fill space
- Lead paragraphs at 11pt for visual hierarchy

### Mixed Content
- Start with text intro in fewer columns (page-2)
- Transition to more columns for image grids
- Use `new-page` divs for clean section breaks

---

## Known Problems / Dead Ends

### multicols* vs multicols
- `multicols*` fills to bottom but can't break pages
- `multicols` balances but leaves space at bottom
- **Trade-off**: Use multicols for text, multicols* for fixed galleries

### flowfram package
- Tested in test-flowfram.tex
- Too complex for this use case
- Stick with multicol

### paracol package
- Tested in test-paracol.tex
- Useful for parallel columns but overkill here
