#!/usr/bin/env python3
"""
Build Game Design Document PDF from multiple Markdown chapter files.

This script collects all chapter files (00-*.md, 01-*.md, etc.) in order
and passes them to Pandoc for PDF generation.

Usage:
    python scripts/build-gdd.py
    python scripts/build-gdd.py --merge-only  # Just create merged .md
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_chapter_files(manuscript_dir: Path) -> list[Path]:
    """Get all chapter files sorted by numeric prefix."""
    files = list(manuscript_dir.glob("[0-9][0-9]-*.md"))
    # Sort by the numeric prefix
    files.sort(key=lambda f: f.name)
    return files


def merge_chapters(files: list[Path], output_path: Path) -> None:
    """Merge all chapter files into a single markdown file."""
    with open(output_path, "w", encoding="utf-8") as out:
        for i, file in enumerate(files):
            content = file.read_text(encoding="utf-8")
            out.write(content)
            # Add newlines between chapters (but not after the last one)
            if i < len(files) - 1:
                out.write("\n\n")
    print(f"  Merged {len(files)} files -> {output_path}")


def build_pdf(
    manuscript_dir: Path,
    output_path: Path,
    template: Path,
    fontsize: Optional[str] = None,
) -> int:
    """Build PDF from chapter files using Pandoc."""
    files = get_chapter_files(manuscript_dir)

    if not files:
        print(f"Error: No chapter files found in {manuscript_dir}")
        print("  Expected files like: 00-frontmatter.md, 01-uebersicht.md, etc.")
        return 1

    print(f"Found {len(files)} chapter files:")
    for f in files:
        print(f"  - {f.name}")

    # Build pandoc command with paths relative to manuscript_dir
    relative_files = [f.name for f in files]
    relative_output = (
        output_path.relative_to(manuscript_dir)
        if output_path.is_relative_to(manuscript_dir)
        else f"../export/{output_path.name}"
    )
    relative_template = f"../{template.name}"

    cmd = [
        "pandoc",
        *relative_files,
        "-o",
        str(relative_output),
        f"--template={relative_template}",
        "--pdf-engine=lualatex",
    ]

    # Add fontsize variable if specified (article class supports: 10pt, 11pt, 12pt)
    if fontsize:
        cmd.extend(["-V", f"fontsize={fontsize}"])
        print(f"  Using font size: {fontsize}")

    print(f"\nBuilding PDF: {output_path}")
    print(f"  Running from: {manuscript_dir}")
    print(f"  Command: {' '.join(cmd)}")
    # Run from the language-specific manuscript directory so relative paths work
    result = subprocess.run(cmd, cwd=manuscript_dir)

    if result.returncode == 0:
        print(f"  PDF generated: {output_path}")
    else:
        print(f"  Error: Pandoc failed with code {result.returncode}")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Game Design Document PDF from chapter files")
    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Only merge chapters into single .md file (no PDF)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output filename (without extension)",
    )
    parser.add_argument(
        "--fontsize",
        type=str,
        help="Font size (e.g., 10pt, 11pt, 12pt). Default: 11pt",
    )
    args = parser.parse_args()

    # Determine paths
    project_root = Path(__file__).parent.parent
    manuscript_dir = project_root / "game-design-document" / "de"
    template = project_root / "game-design-document" / "template-gdd.tex"
    export_dir = project_root / "game-design-document" / "export"
    base_name = args.output or "gdd-de"

    # Ensure export directory exists
    export_dir.mkdir(parents=True, exist_ok=True)

    if args.merge_only:
        # Just merge to a single markdown file
        merged_path = export_dir / f"{base_name}.md"
        files = get_chapter_files(manuscript_dir)
        if not files:
            print(f"Error: No chapter files found in {manuscript_dir}")
            return 1
        merge_chapters(files, merged_path)
        return 0

    # Build PDF
    pdf_path = export_dir / f"{base_name}.pdf"
    return build_pdf(manuscript_dir, pdf_path, template, fontsize=args.fontsize)


if __name__ == "__main__":
    sys.exit(main())
