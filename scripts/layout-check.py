#!/usr/bin/env python3
"""
Visual Layout Assessment Tool

This script helps assess and iterate on PDF layouts by:
1. Building the PDF
2. Rendering pages to images for inspection
3. Comparing against previous versions
4. Recording what works

Usage:
    python scripts/layout-check.py                    # Build and preview
    python scripts/layout-check.py --page 3           # Preview specific page
    python scripts/layout-check.py --compare old.pdf  # Compare with previous
    python scripts/layout-check.py --all-pages        # Render all pages

Requirements:
    - poppler (pdftocairo): brew install poppler
    - Pillow: pip3 install Pillow
    - diff-pdf-visually (optional): pip3 install diff-pdf-visually
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def check_dependencies() -> bool:
    """Check if required tools are available."""
    missing = []

    # Check pdftocairo
    try:
        subprocess.run(["pdftocairo", "-v"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        missing.append("poppler (install: brew install poppler)")

    # Check diff-pdf-visually (optional)
    try:
        subprocess.run(["diff-pdf-visually", "--help"], capture_output=True, check=True)
    except FileNotFoundError:
        print("  Note: diff-pdf-visually not found (optional, install: pip3 install diff-pdf-visually)")

    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        return False

    return True


def get_page_count(pdf_path: Path) -> int:
    """Get number of pages in PDF using pdfinfo."""
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return 0


def render_page(pdf_path: Path, page: int, output_dir: Path, dpi: int = 150) -> Path:
    """Render a single PDF page to PNG."""
    output_prefix = output_dir / f"{pdf_path.stem}-page"

    subprocess.run([
        "pdftocairo", "-png", "-r", str(dpi),
        "-f", str(page), "-l", str(page),
        str(pdf_path), str(output_prefix)
    ], check=True)

    # pdftocairo adds page numbers with padding
    output_file = output_dir / f"{pdf_path.stem}-page-{page:02d}.png"
    if not output_file.exists():
        output_file = output_dir / f"{pdf_path.stem}-page-{page}.png"

    return output_file


def render_all_pages(pdf_path: Path, output_dir: Path, dpi: int = 150) -> list[Path]:
    """Render all PDF pages to PNG files."""
    page_count = get_page_count(pdf_path)

    if page_count == 0:
        print(f"Could not determine page count for {pdf_path}")
        return []

    output_prefix = output_dir / pdf_path.stem

    print(f"Rendering {page_count} pages at {dpi} DPI...")
    subprocess.run([
        "pdftocairo", "-png", "-r", str(dpi),
        str(pdf_path), str(output_prefix)
    ], check=True)

    # Collect output files
    outputs = sorted(output_dir.glob(f"{pdf_path.stem}-*.png"))
    return outputs


def compare_pdfs(old_pdf: Path, new_pdf: Path) -> bool:
    """Compare two PDFs visually using diff-pdf-visually."""
    try:
        result = subprocess.run(
            ["diff-pdf-visually", str(old_pdf), str(new_pdf)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("PDFs are visually identical")
            return True
        else:
            print("PDFs differ:")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("diff-pdf-visually not installed, skipping comparison")
        return False


def open_image(image_path: Path):
    """Open image in default viewer."""
    if sys.platform == "darwin":
        subprocess.run(["open", str(image_path)])
    elif sys.platform == "linux":
        subprocess.run(["xdg-open", str(image_path)])
    else:
        print(f"Preview: {image_path}")


def build_pdf() -> tuple[int, Path]:
    """Build the worldbuilding bible PDF."""
    project_root = Path(__file__).parent.parent
    build_script = project_root / "scripts" / "build-worldbuilding.py"

    print("Building PDF...")
    result = subprocess.run(
        [sys.executable, str(build_script)],
        cwd=project_root,
        capture_output=True, text=True
    )

    pdf_path = project_root / "worldbuilding-bible" / "export" / "worldbuilding-bible-de.pdf"

    return result.returncode, pdf_path


def main():
    parser = argparse.ArgumentParser(
        description="Visual layout assessment tool for worldbuilding bible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/layout-check.py                    # Build and preview page 1
    python scripts/layout-check.py --page 5           # Preview page 5
    python scripts/layout-check.py --all-pages        # Render all pages
    python scripts/layout-check.py --compare old.pdf  # Compare with old version
    python scripts/layout-check.py --no-build         # Skip build, use existing PDF
        """
    )

    parser.add_argument("--page", type=int, default=1, help="Page number to preview (default: 1)")
    parser.add_argument("--all-pages", action="store_true", help="Render all pages")
    parser.add_argument("--compare", type=str, help="Compare with another PDF")
    parser.add_argument("--no-build", action="store_true", help="Skip building, use existing PDF")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for rendering (default: 150)")
    parser.add_argument("--output-dir", type=str, help="Directory for preview images")

    args = parser.parse_args()

    print("=" * 60)
    print("  LAYOUT ASSESSMENT TOOL")
    print("=" * 60)

    if not check_dependencies():
        return 1

    project_root = Path(__file__).parent.parent

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "worldbuilding-bible" / "export" / "previews"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build PDF if needed
    if args.no_build:
        pdf_path = project_root / "worldbuilding-bible" / "export" / "worldbuilding-bible-de.pdf"
        if not pdf_path.exists():
            print(f"PDF not found: {pdf_path}")
            return 1
    else:
        returncode, pdf_path = build_pdf()
        if returncode != 0 or not pdf_path.exists():
            print("Build failed")
            return 1

    print(f"\nPDF: {pdf_path}")
    print(f"Pages: {get_page_count(pdf_path)}")

    # Compare if requested
    if args.compare:
        compare_pdf = Path(args.compare)
        if compare_pdf.exists():
            print(f"\nComparing with: {compare_pdf}")
            compare_pdfs(compare_pdf, pdf_path)
        else:
            print(f"Comparison PDF not found: {compare_pdf}")

    # Render previews
    if args.all_pages:
        print(f"\nRendering all pages to {output_dir}...")
        outputs = render_all_pages(pdf_path, output_dir, args.dpi)
        print(f"Created {len(outputs)} preview images")
        if outputs:
            print(f"First: {outputs[0]}")
            print(f"Last: {outputs[-1]}")
    else:
        print(f"\nRendering page {args.page}...")
        preview = render_page(pdf_path, args.page, output_dir, args.dpi)
        if preview.exists():
            print(f"Preview: {preview}")
            open_image(preview)
        else:
            print(f"Failed to create preview")

    print("\n" + "=" * 60)
    print("  ASSESSMENT COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
