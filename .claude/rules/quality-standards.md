# Quality Standards

## PDF Layout Quality

### Good Layout Indicators
- Text fills columns reasonably (not too sparse, not cramped)
- Images fit within columns without awkward cropping
- Consistent spacing between elements
- Headings stay with their content (no orphaned headings)
- White space is intentional, not accidental

### Bad Layout Indicators
- Large gaps of white space with no content
- Images that overflow or look too small
- Text that doesn't balance across columns
- Captions separated from their images
- Page breaks in awkward places

## Content Quality

### Text Standards
- Concise, evocative writing (not academic verbosity)
- First-person narrative for travel/personal sections
- Technical accuracy for game design sections
- Consistent terminology throughout

### Image Standards
- Optimized for PDF (use scripts/optimize-images.py)
- Meaningful captions, not just filenames
- Credit attribution where required
- Consistent visual style per section

## Build Quality

### Before Committing
- PDF builds without errors
- Page count is reasonable (not bloated)
- File size is manageable (< 50MB preferred)
- Visual spot-check on key pages

### Testing Workflow
1. Make changes
2. Run `make worldbuilding`
3. Open PDF and check affected pages
4. If layout issues, iterate before committing
