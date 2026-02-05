#!/usr/bin/env python3
"""
Image Optimization for PDF Export

Resizes images to the exact pixel dimensions needed for screen-quality PDFs.
Creates optimized copies in a 'resized' subdirectory, preserving originals.

Target dimensions based on A3 landscape (420×297mm) with 19.05mm margins:
- Text width: ~382mm (~15 inches)
- 4-column width: ~91.7mm (~3.6 inches) → 540px at 150 DPI
- 3-column width: ~124mm (~4.9 inches) → 730px at 150 DPI
- 2-column width: ~188mm (~7.4 inches) → 1110px at 150 DPI
- Full width: ~382mm (~15 inches) → 2250px at 150 DPI

We use 2x resolution for crisp display on retina screens:
- Column images: max 1200px on longest side
- Full-width images: max 2400px on longest side

Usage:
    python scripts/optimize-images.py                    # Optimize all images
    python scripts/optimize-images.py --dpi 150          # Set target DPI
    python scripts/optimize-images.py --max-width 1200   # Set max dimension
    python scripts/optimize-images.py --quality 85       # Set JPEG quality
    python scripts/optimize-images.py --dry-run          # Show what would be done

Requirements:
    pip3 install Pillow
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: pip3 install Pillow")
    sys.exit(1)


class ImageStats(NamedTuple):
    path: Path
    width: int
    height: int
    size_kb: float
    format: str


def get_image_stats(path: Path) -> ImageStats | None:
    """Get image dimensions and file size."""
    try:
        with Image.open(path) as img:
            return ImageStats(
                path=path,
                width=img.width,
                height=img.height,
                size_kb=path.stat().st_size / 1024,
                format=img.format or "UNKNOWN"
            )
    except Exception as e:
        print(f"  Warning: Could not read {path}: {e}")
        return None


def calculate_target_size(
    width: int,
    height: int,
    max_dimension: int
) -> tuple[int, int]:
    """Calculate target dimensions maintaining aspect ratio."""
    if width <= max_dimension and height <= max_dimension:
        return width, height

    if width > height:
        new_width = max_dimension
        new_height = int(height * max_dimension / width)
    else:
        new_height = max_dimension
        new_width = int(width * max_dimension / height)

    return new_width, new_height


def optimize_image(
    source: Path,
    dest: Path,
    max_dimension: int,
    quality: int,
    dry_run: bool = False
) -> tuple[float, float] | None:
    """
    Resize and optimize a single image.

    Returns: (original_kb, new_kb) or None if skipped
    """
    stats = get_image_stats(source)
    if not stats:
        return None

    target_w, target_h = calculate_target_size(
        stats.width, stats.height, max_dimension
    )

    # Skip if already small enough - but copy to dest for consistency
    if target_w == stats.width and target_h == stats.height:
        if not dry_run:
            import shutil
            shutil.copy2(source, dest)
        print(f"  Copy (already optimal): {source.name}")
        return stats.size_kb, stats.size_kb

    reduction = 100 * (1 - (target_w * target_h) / (stats.width * stats.height))

    if dry_run:
        print(f"  Would resize: {source.name}")
        print(f"    {stats.width}×{stats.height} → {target_w}×{target_h} ({reduction:.0f}% fewer pixels)")
        return stats.size_kb, stats.size_kb * (1 - reduction/100)

    try:
        with Image.open(source) as img:
            # Convert to RGB if necessary (for JPEG output)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize with high-quality resampling
            resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Save as JPEG but keep original filename (including extension)
            # This ensures LaTeX finds the file with the original reference
            dest_path = dest  # Keep original name including extension
            resized.save(
                dest_path,
                'JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )

            new_size_kb = dest_path.stat().st_size / 1024

            print(f"  Optimized: {source.name}")
            print(f"    {stats.width}×{stats.height} → {target_w}×{target_h}")
            print(f"    {stats.size_kb:.0f} KB → {new_size_kb:.0f} KB ({100*(1-new_size_kb/stats.size_kb):.0f}% smaller)")

            return stats.size_kb, new_size_kb

    except Exception as e:
        print(f"  Error processing {source.name}: {e}")
        return None


def optimize_directory(
    source_dir: Path,
    max_dimension: int = 1200,
    quality: int = 85,
    dry_run: bool = False
) -> tuple[float, float]:
    """
    Optimize all images in a directory.

    Returns: (total_original_mb, total_new_mb)
    """
    # Create resized subdirectory
    resized_dir = source_dir / "resized"
    if not dry_run:
        resized_dir.mkdir(exist_ok=True)

    # Find all images
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif'}
    images = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    ]

    if not images:
        print(f"No images found in {source_dir}")
        return 0, 0

    print(f"\nProcessing {len(images)} images in {source_dir.name}/")
    print(f"  Max dimension: {max_dimension}px")
    print(f"  Quality: {quality}%")
    print(f"  Output: {resized_dir}/")
    print()

    total_original = 0.0
    total_new = 0.0
    processed = 0

    for img_path in sorted(images):
        dest_path = resized_dir / img_path.name
        result = optimize_image(img_path, dest_path, max_dimension, quality, dry_run)

        if result:
            total_original += result[0]
            total_new += result[1]
            processed += 1

    return total_original / 1024, total_new / 1024  # Return in MB


def main():
    parser = argparse.ArgumentParser(
        description="Optimize images for PDF export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Target sizes for A3 landscape at 150 DPI (2x for retina):
  - Column images (4-col): 1200px max
  - Full-width images: 2400px max

Examples:
    python scripts/optimize-images.py                     # Optimize all
    python scripts/optimize-images.py --max-width 800     # Smaller for web
    python scripts/optimize-images.py --dry-run           # Preview changes
    python scripts/optimize-images.py --dir figures/foo   # Specific folder
        """
    )

    parser.add_argument(
        "--dir",
        type=str,
        help="Specific directory to optimize (default: all figure directories)"
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=1200,
        help="Maximum dimension in pixels (default: 1200)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality 1-100 (default: 85)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Target DPI for calculation reference (default: 150)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  IMAGE OPTIMIZATION FOR PDF EXPORT")
    print("=" * 60)

    if args.dry_run:
        print("\n  DRY RUN - no files will be modified\n")

    project_root = Path(__file__).parent.parent
    figures_root = project_root / "worldbuilding-bible" / "figures"

    if args.dir:
        directories = [Path(args.dir)]
    else:
        # Find all figure subdirectories
        directories = [
            d for d in figures_root.iterdir()
            if d.is_dir() and d.name != "resized"
        ]

    total_original = 0.0
    total_new = 0.0

    for directory in sorted(directories):
        if not directory.exists():
            print(f"\nDirectory not found: {directory}")
            continue

        orig, new = optimize_directory(
            directory,
            max_dimension=args.max_width,
            quality=args.quality,
            dry_run=args.dry_run
        )
        total_original += orig
        total_new += new

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"  WOULD SAVE: {total_original:.1f} MB → {total_new:.1f} MB")
        print(f"  REDUCTION: {total_original - total_new:.1f} MB ({100*(1-total_new/total_original):.0f}%)")
    else:
        print(f"  TOTAL: {total_original:.1f} MB → {total_new:.1f} MB")
        if total_original > 0:
            print(f"  SAVED: {total_original - total_new:.1f} MB ({100*(1-total_new/total_original):.0f}%)")
    print("=" * 60)

    if not args.dry_run:
        print("\nTo use optimized images, update your LaTeX graphics path:")
        print("  \\graphicspath{{../figures/russia-photographs/resized/}}")
        print("\nOr create a symlink to swap directories.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
