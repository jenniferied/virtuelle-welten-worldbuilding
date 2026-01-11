#!/usr/bin/env python3
"""
Visual Layout Assessment Tool

This script helps assess and iterate on PDF layouts by:
1. Building the PDF
2. Rendering pages to images for inspection
3. Comparing against previous versions
4. Outputting structured JSON reports for Claude analysis
5. Recording what works

Usage:
    python scripts/layout-check.py                    # Build and preview
    python scripts/layout-check.py --page 3           # Preview specific page
    python scripts/layout-check.py --compare old.pdf  # Compare with previous
    python scripts/layout-check.py --all-pages        # Render all pages
    python scripts/layout-check.py --json             # Output JSON report
    python scripts/layout-check.py --analyze 5        # Analyze page 5 for issues

Requirements:
    - poppler (pdftocairo): brew install poppler
    - Pillow: pip3 install Pillow
    - diff-pdf-visually (optional): pip3 install diff-pdf-visually
"""

import argparse
import subprocess
import sys
import json
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

    print("Building PDF...", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, str(build_script)],
        cwd=project_root,
        capture_output=True, text=True
    )

    pdf_path = project_root / "worldbuilding-bible" / "export" / "worldbuilding-bible-de.pdf"

    return result.returncode, pdf_path


def get_pdf_metadata(pdf_path: Path) -> dict:
    """Get PDF metadata using pdfinfo."""
    metadata = {}
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower().replace(" ", "_")] = value.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return metadata


def analyze_page_image(image_path: Path) -> dict:
    """Analyze a rendered page image for layout issues."""
    analysis = {
        "path": str(image_path),
        "exists": image_path.exists(),
        "issues": [],
        "metrics": {}
    }

    if not image_path.exists():
        return analysis

    try:
        from PIL import Image
        import statistics

        with Image.open(image_path) as img:
            analysis["metrics"]["width"] = img.width
            analysis["metrics"]["height"] = img.height

            # Convert to grayscale for analysis
            gray = img.convert("L")
            pixels = list(gray.getdata())

            # Calculate brightness statistics
            avg_brightness = statistics.mean(pixels)
            analysis["metrics"]["avg_brightness"] = round(avg_brightness, 1)

            # Check for large white areas (potential empty space)
            white_threshold = 250
            white_pixels = sum(1 for p in pixels if p > white_threshold)
            white_percentage = (white_pixels / len(pixels)) * 100
            analysis["metrics"]["white_percentage"] = round(white_percentage, 1)

            # Flag high white percentage as potential issue
            if white_percentage > 40:
                analysis["issues"].append({
                    "type": "excessive_whitespace",
                    "severity": "warning" if white_percentage < 60 else "error",
                    "detail": f"{white_percentage:.1f}% of page is white"
                })

            # Check edges for margins (sample left/right strips)
            width, height = img.size
            left_strip = gray.crop((0, 0, width // 20, height))
            right_strip = gray.crop((width - width // 20, 0, width, height))

            left_avg = statistics.mean(list(left_strip.getdata()))
            right_avg = statistics.mean(list(right_strip.getdata()))
            analysis["metrics"]["left_margin_brightness"] = round(left_avg, 1)
            analysis["metrics"]["right_margin_brightness"] = round(right_avg, 1)

    except ImportError:
        analysis["issues"].append({
            "type": "missing_dependency",
            "severity": "info",
            "detail": "Pillow not installed, skipping image analysis"
        })
    except Exception as e:
        analysis["issues"].append({
            "type": "analysis_error",
            "severity": "error",
            "detail": str(e)
        })

    return analysis


def generate_json_report(pdf_path: Path, pages_to_analyze: list[int] = None, output_dir: Path = None, dpi: int = 72) -> dict:
    """Generate a structured JSON report of the PDF layout."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "pdf_path": str(pdf_path),
        "metadata": get_pdf_metadata(pdf_path),
        "pages": [],
        "summary": {
            "total_issues": 0,
            "pages_with_issues": []
        }
    }

    page_count = get_page_count(pdf_path)
    report["metadata"]["page_count"] = page_count

    if pages_to_analyze is None:
        pages_to_analyze = list(range(1, min(page_count + 1, 6)))  # First 5 pages by default

    if output_dir is None:
        output_dir = pdf_path.parent / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    for page_num in pages_to_analyze:
        if page_num > page_count:
            continue

        # Render page at low DPI for analysis
        preview = render_page(pdf_path, page_num, output_dir, dpi)
        analysis = analyze_page_image(preview)
        analysis["page_number"] = page_num

        report["pages"].append(analysis)

        if analysis["issues"]:
            report["summary"]["total_issues"] += len(analysis["issues"])
            report["summary"]["pages_with_issues"].append(page_num)

    return report


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
    parser.add_argument("--json", action="store_true", help="Output JSON report (for Claude analysis)")
    parser.add_argument("--analyze", type=str, help="Analyze specific pages (e.g., '1,3,5' or '1-5' or 'all')")

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

    # JSON/Analyze mode - quieter output, structured data
    if args.json or args.analyze:
        pages_to_analyze = None
        if args.analyze:
            if args.analyze.lower() == "all":
                pages_to_analyze = list(range(1, get_page_count(pdf_path) + 1))
            elif "-" in args.analyze:
                start, end = map(int, args.analyze.split("-"))
                pages_to_analyze = list(range(start, end + 1))
            else:
                pages_to_analyze = [int(p.strip()) for p in args.analyze.split(",")]

        report = generate_json_report(
            pdf_path,
            pages_to_analyze=pages_to_analyze,
            output_dir=output_dir if args.output_dir else None,
            dpi=72  # Lower DPI for analysis
        )

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            # Human-readable summary
            print(f"\nPDF: {pdf_path}")
            print(f"Pages: {report['metadata'].get('page_count', 'unknown')}")
            print(f"File size: {report['metadata'].get('file_size', 'unknown')}")
            print(f"\nAnalyzed {len(report['pages'])} pages")
            print(f"Total issues found: {report['summary']['total_issues']}")
            if report['summary']['pages_with_issues']:
                print(f"Pages with issues: {report['summary']['pages_with_issues']}")
            for page in report['pages']:
                if page['issues']:
                    print(f"\n  Page {page['page_number']}:")
                    for issue in page['issues']:
                        print(f"    - [{issue['severity']}] {issue['type']}: {issue['detail']}")

        return 0

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
