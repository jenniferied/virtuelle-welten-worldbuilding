#!/usr/bin/env python3
"""
Build Worldbuilding Bible PDF from Markdown using LaTeX.

This script implements a Markdown → LaTeX → PDF pipeline using Pandoc and LuaLaTeX
to create a magazine-style A3 landscape document.

This is an alternative to the WeasyPrint-based pipeline, producing similar output
but using LaTeX for typesetting.

Features:
    - Collects Markdown files with numeric prefixes (00-*, 01-*, etc.)
    - Converts to LaTeX via Pandoc using a custom template
    - Renders final PDF via LuaLaTeX
    - Handles fenced divs: .lead, .sidebar, .infobox, .warning, .columns-N

Usage:
    python scripts/build-worldbuilding-latex.py --lang en
    python scripts/build-worldbuilding-latex.py --lang de
    python scripts/build-worldbuilding-latex.py --lang en --tex-only
    python scripts/build-worldbuilding-latex.py --check-deps

Requirements:
    - pandoc (system install)
    - LuaLaTeX with fontspec (via MacTeX or TeX Live)
    - Fonts: Open Sans, EB Garamond, Courier New
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

# Pandoc Lua filter to convert fenced divs to LaTeX environments
LUA_FILTER = r"""
-- Lua filter for converting Pandoc fenced divs to LaTeX environments
-- Handles all worldbuilding bible special elements

function Div(el)
  local classes = el.classes

  -- Lead paragraph
  if classes:includes("lead") then
    return {
      pandoc.RawBlock("latex", "\\begin{lead}"),
      el,
      pandoc.RawBlock("latex", "\\end{lead}")
    }
  end

  -- Sidebar
  if classes:includes("sidebar") then
    return {
      pandoc.RawBlock("latex", "\\begin{sidebar}"),
      el,
      pandoc.RawBlock("latex", "\\end{sidebar}")
    }
  end

  -- Infobox / Callout
  if classes:includes("infobox") or classes:includes("callout") then
    return {
      pandoc.RawBlock("latex", "\\begin{infobox}"),
      el,
      pandoc.RawBlock("latex", "\\end{infobox}")
    }
  end

  -- Warning
  if classes:includes("warning") then
    return {
      pandoc.RawBlock("latex", "\\begin{warning}"),
      el,
      pandoc.RawBlock("latex", "\\end{warning}")
    }
  end

  -- Note
  if classes:includes("note") then
    return {
      pandoc.RawBlock("latex", "\\begin{note}"),
      el,
      pandoc.RawBlock("latex", "\\end{note}")
    }
  end

  -- Success
  if classes:includes("success") then
    return {
      pandoc.RawBlock("latex", "\\begin{success}"),
      el,
      pandoc.RawBlock("latex", "\\end{success}")
    }
  end

  -- Metadata
  if classes:includes("metadata") then
    return {
      pandoc.RawBlock("latex", "\\begin{metadata}"),
      el,
      pandoc.RawBlock("latex", "\\end{metadata}")
    }
  end

  -- Hierarchy (for tree diagrams)
  if classes:includes("hierarchy") then
    return {
      pandoc.RawBlock("latex", "\\begin{hierarchy}"),
      el,
      pandoc.RawBlock("latex", "\\end{hierarchy}")
    }
  end

  -- Stats box (D&D style stat blocks)
  if classes:includes("statsbox") or classes:includes("stats") then
    return {
      pandoc.RawBlock("latex", "\\begin{statsbox}"),
      el,
      pandoc.RawBlock("latex", "\\end{statsbox}")
    }
  end

  -- Multi-column layouts (with \nopagebreak to keep with preceding heading)
  if classes:includes("columns-1") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{columns-1}"),
      el,
      pandoc.RawBlock("latex", "\\end{columns-1}")
    }
  end

  if classes:includes("columns-2") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{columns-2}"),
      el,
      pandoc.RawBlock("latex", "\\end{columns-2}")
    }
  end

  if classes:includes("columns-3") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{columns-3}"),
      el,
      pandoc.RawBlock("latex", "\\end{columns-3}")
    }
  end

  if classes:includes("columns-4") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{columns-4}"),
      el,
      pandoc.RawBlock("latex", "\\end{columns-4}")
    }
  end

  -- Full-page unbalanced column layouts (with \nopagebreak to keep with preceding heading)
  if classes:includes("page-1") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{page-1}"),
      el,
      pandoc.RawBlock("latex", "\\end{page-1}")
    }
  end

  if classes:includes("page-2") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{page-2}"),
      el,
      pandoc.RawBlock("latex", "\\end{page-2}")
    }
  end

  if classes:includes("page-3") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{page-3}"),
      el,
      pandoc.RawBlock("latex", "\\end{page-3}")
    }
  end

  if classes:includes("page-4") then
    return {
      pandoc.RawBlock("latex", "\\nopagebreak\\begin{page-4}"),
      el,
      pandoc.RawBlock("latex", "\\end{page-4}")
    }
  end

  -- Boxed content (unified box style)
  if classes:includes("boxed") then
    return {
      pandoc.RawBlock("latex", "\\begin{boxed}"),
      el,
      pandoc.RawBlock("latex", "\\end{boxed}")
    }
  end

  -- Cover / title page
  if classes:includes("cover") or classes:includes("title-page") then
    -- Skip - handled by maketitle
    return el
  end

  -- Page break (used at start of chapter files)
  if classes:includes("page-break") or classes:includes("pagebreak") or classes:includes("new-page") or classes:includes("newpage") then
    return {
      pandoc.RawBlock("latex", "\\clearpage"),
      el
    }
  end

  -- No break (keep together)
  if classes:includes("no-break") or classes:includes("nobreak") then
    return {
      pandoc.RawBlock("latex", "\\begin{minipage}{\\linewidth}"),
      el,
      pandoc.RawBlock("latex", "\\end{minipage}")
    }
  end

  return el
end

-- Convert horizontal rules to decorative dividers
function HorizontalRule(el)
  return pandoc.RawBlock("latex", "\\sectiondivider")
end
"""


def get_chapter_files(source_dir: Path) -> list[Path]:
    """
    Get all Markdown files sorted by numeric prefix.

    Looks for files matching patterns like:
        00-cover.md
        01-introduction.md
        02-species.md

    Args:
        source_dir: Directory containing the Markdown files

    Returns:
        List of Path objects sorted by filename
    """
    files = list(source_dir.glob("[0-9][0-9]-*.md"))

    # Also include single-digit prefixes
    files.extend(source_dir.glob("[0-9]-*.md"))

    # Sort by numeric prefix
    files.sort(key=lambda f: f.name)

    return files


def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    errors = []

    # Check pandoc
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True)
        print(f"  ✓ Pandoc: {result.stdout.splitlines()[0]}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("Pandoc not found. Install from: https://pandoc.org/installing.html")

    # Check LuaLaTeX
    try:
        result = subprocess.run(
            ["lualatex", "--version"], capture_output=True, text=True, check=True
        )
        version_line = result.stdout.splitlines()[0] if result.stdout else "Unknown"
        print(f"  ✓ LuaLaTeX: {version_line}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("LuaLaTeX not found. Install MacTeX (macOS) or TeX Live (Linux/Windows)")

    # Check fonts (basic check via fc-list)
    try:
        result = subprocess.run(["fc-list", ":family"], capture_output=True, text=True, check=True)
        fonts = result.stdout.lower()
        font_status = []
        for font in ["open sans", "eb garamond", "courier"]:
            if font in fonts:
                font_status.append(f"✓ {font.title()}")
            else:
                font_status.append(f"? {font.title()} (may still work)")
        print(f"  Fonts: {', '.join(font_status)}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ? Could not check fonts (fc-list not available)")

    if errors:
        print("\n❌ Missing dependencies:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def create_lua_filter(temp_dir: Path) -> Path:
    """Create the Lua filter file for Pandoc."""
    filter_path = temp_dir / "worldbuilding-filter.lua"
    filter_path.write_text(LUA_FILTER)
    return filter_path


def build_latex(
    source_dir: Path,
    output_path: Path,
    template: Path,
    lua_filter: Path,
    toc: bool = True,
) -> int:
    """
    Build LaTeX from Markdown files using Pandoc.

    Args:
        source_dir: Directory containing source Markdown files
        output_path: Path for the output .tex file
        template: Path to the LaTeX template
        lua_filter: Path to the Lua filter for fenced divs
        toc: Whether to include table of contents

    Returns:
        Exit code (0 for success)
    """
    files = get_chapter_files(source_dir)

    if not files:
        print(f"❌ No chapter files found in {source_dir}")
        print("   Expected files like: 00-cover.md, 01-introduction.md, etc.")
        return 1

    print(f"\n📚 Found {len(files)} chapter files:")
    for f in files:
        print(f"   - {f.name}")

    # Build pandoc command
    cmd = [
        "pandoc",
        *[str(f) for f in files],
        "-o",
        str(output_path),
        f"--template={template}",
        f"--lua-filter={lua_filter}",
        "--standalone",
        f"--resource-path={source_dir}:{source_dir}/figures",
        "--pdf-engine=lualatex",
        "-V",
        "documentclass=article",
    ]

    if toc:
        cmd.extend(["--toc", "--toc-depth=3", "-V", "toc=true"])

    # Always include list of figures at end
    cmd.extend(["-V", "lof=true"])

    print(f"\n🔨 Building LaTeX: {output_path.name}")
    print(f"   Template: {template.name}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=source_dir)

        if result.returncode != 0:
            print(f"\n❌ Pandoc error:\n{result.stderr}")
            return result.returncode

        print(f"   ✓ LaTeX generated: {output_path}")
        return 0

    except FileNotFoundError:
        print("❌ Pandoc not found. Please install Pandoc first.")
        return 1


def build_pdf(
    tex_path: Path,
    output_dir: Path,
) -> int:
    """
    Build PDF from LaTeX using LuaLaTeX.

    Args:
        tex_path: Path to the source .tex file
        output_dir: Directory for output files

    Returns:
        Exit code (0 for success)
    """
    pdf_name = tex_path.stem + ".pdf"
    pdf_path = output_dir / pdf_name

    print(f"\n📄 Rendering PDF: {pdf_name}")
    print(f"   Source: {tex_path.name}")

    # Run LuaLaTeX twice for TOC and references
    cmd = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir}",
        str(tex_path),
    ]

    try:
        # First pass
        print("   Pass 1/2...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_path.parent)
        # First pass may have warnings, continue to second pass

        # Second pass (for TOC)
        print("   Pass 2/2...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_path.parent)

        # Check if PDF was produced (the only real test of success)
        if not pdf_path.exists():
            print("\n❌ LuaLaTeX error: No PDF produced")
            lines = result.stdout.splitlines()[-50:]
            for line in lines:
                if "error" in line.lower() or "!" in line:
                    print(f"   {line}")
            return 1

        print(f"   ✓ PDF generated: {pdf_path}")

        # Report file size
        if pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"   📊 Size: {size_mb:.2f} MB")

        # Clean up auxiliary files
        for ext in [".aux", ".log", ".out", ".toc"]:
            aux_file = output_dir / (tex_path.stem + ext)
            if aux_file.exists():
                aux_file.unlink()

        return 0

    except FileNotFoundError:
        print("❌ LuaLaTeX not found. Please install MacTeX or TeX Live.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Worldbuilding Bible PDF using LaTeX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/build-worldbuilding-latex.py
    python scripts/build-worldbuilding-latex.py --tex-only
    python scripts/build-worldbuilding-latex.py --check-deps
        """,
    )

    parser.add_argument(
        "--lang",
        choices=["de"],
        default="de",
        help="Language version to build (default: de)",
    )

    parser.add_argument(
        "--tex-only",
        action="store_true",
        help="Only generate LaTeX (skip PDF generation)",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Custom output filename (without extension)",
    )

    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Disable table of contents",
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies and exit",
    )

    args = parser.parse_args()

    # Header
    print("=" * 60)
    print("  🌍 WORLDBUILDING BIBLE BUILDER (LaTeX)")
    print("     Markdown → LaTeX → PDF Pipeline")
    print("=" * 60)

    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        return 1

    if args.check_deps:
        print("\n✅ All dependencies available!")
        return 0

    # Determine paths
    project_root = Path(__file__).parent.parent
    worldbuilding_dir = project_root / "worldbuilding-bible"
    source_dir = worldbuilding_dir / args.lang
    export_dir = worldbuilding_dir / "export"

    # Template path
    template = worldbuilding_dir / "template-latex.tex"

    # Validate paths
    if not source_dir.exists():
        print(f"\n❌ Source directory not found: {source_dir}")
        print("   Create Markdown files in this directory first.")
        return 1

    if not template.exists():
        print(f"\n❌ Template not found: {template}")
        return 1

    # Ensure export directory exists
    export_dir.mkdir(parents=True, exist_ok=True)

    # Determine output filenames
    base_name = args.output or f"worldbuilding-bible-{args.lang}"
    tex_path = export_dir / f"{base_name}.tex"
    pdf_path = export_dir / f"{base_name}.pdf"

    print("\n📁 Paths:")
    print(f"   Source: {source_dir}")
    print(f"   Export: {export_dir}")

    # Create temporary Lua filter
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        lua_filter = create_lua_filter(temp_path)

        # Step 1: Build LaTeX
        result = build_latex(
            source_dir=source_dir,
            output_path=tex_path,
            template=template,
            lua_filter=lua_filter,
            toc=not args.no_toc,
        )

        if result != 0:
            return result

    if args.tex_only:
        print("\n✅ LaTeX-only build complete!")
        print(f"   TeX: {tex_path}")
        return 0

    # Step 2: Build PDF
    result = build_pdf(
        tex_path=tex_path,
        output_dir=export_dir,
    )

    if result != 0:
        return result

    print("\n" + "=" * 60)
    print("  ✅ BUILD COMPLETE!")
    print(f"     PDF: {pdf_path}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
