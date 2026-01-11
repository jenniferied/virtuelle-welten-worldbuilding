# Visual Review Workflow

Claude can directly view rendered PDF pages as images. Here's how:

## Quick Visual Check

1. **Render a specific page**
   ```bash
   python3 scripts/layout-check.py --page N --no-build --output-dir /tmp/preview
   ```

2. **Claude reads the image**
   Use the Read tool on the generated PNG file to see the layout directly.

3. **Analyze and suggest fixes**
   Based on what I see, suggest specific changes.

## Automated Analysis

1. **Run JSON analysis**
   ```bash
   python3 scripts/layout-check.py --analyze 1-10 --no-build --json
   ```

2. **Review structured report**
   Get metrics on white space percentage, issues per page, etc.

## Example Session

User: "Check page 3 of the PDF"

Claude:
1. Runs: `python3 scripts/layout-check.py --page 3 --no-build --output-dir /tmp/preview`
2. Reads: `/tmp/preview/worldbuilding-bible-de-page-03.png`
3. Describes what I see and suggests improvements

## What I Can Assess

- **White space**: Empty areas that should have content
- **Image placement**: Whether images fit columns properly
- **Text flow**: If columns are balanced
- **Overall composition**: Visual weight distribution
- **Heading orphans**: Headings separated from their content

## What I Cannot Assess

- **Typography details**: Fine kerning, specific font rendering
- **Color accuracy**: Exact color matching
- **Print-readiness**: Bleed, color profiles

## Workflow Integration

When user reports layout issue:
1. Render the affected page(s)
2. View the image
3. Identify specific problems
4. Suggest markdown/template changes
5. Rebuild and verify fix
