# Makefile for Dystopian District Project

.PHONY: help worldbuilding gdd all clean

help:
	@echo "Dystopian District - Document Generation"
	@echo ""
	@echo "Build Commands:"
	@echo "  worldbuilding     Build Worldbuilding Bible PDF (A3 Landscape)"
	@echo "  worldbuilding-tex Build Worldbuilding TeX only (for debugging)"
	@echo "  gdd               Build Game Design Document PDF (A4 Portrait)"
	@echo "  all               Build all documents"
	@echo "  clean             Remove generated files"
	@echo ""
	@echo "Requirements:"
	@echo "  - LuaLaTeX (via MacTeX or TeX Live)"
	@echo "  - Pandoc"
	@echo "  - Python 3"

# Worldbuilding Bible (A3 Landscape PDF)
worldbuilding:
	@echo "Building Worldbuilding Bible..."
	@python3 scripts/build-worldbuilding.py
	@echo "✓ Worldbuilding Bible: worldbuilding-bible/export/worldbuilding-bible-de.pdf"

# Worldbuilding TeX only (for debugging)
worldbuilding-tex:
	@echo "Building Worldbuilding Bible (TeX only)..."
	@python3 scripts/build-worldbuilding.py --tex-only
	@echo "✓ Worldbuilding TeX: worldbuilding-bible/export/worldbuilding-bible-de.tex"

# Game Design Document (A4 Portrait PDF)
gdd:
	@echo "Building Game Design Document..."
	@python3 scripts/build-gdd.py
	@echo "✓ GDD: game-design-document/export/gdd-de.pdf"

# Build all documents
all: worldbuilding gdd
	@echo ""
	@echo "========================================="
	@echo "✓ All documents generated successfully!"
	@echo "========================================="
	@echo ""
	@echo "Generated PDFs:"
	@echo "  Worldbuilding: worldbuilding-bible/export/worldbuilding-bible-de.pdf"
	@echo "  GDD:           game-design-document/export/gdd-de.pdf"

# Clean generated files
clean:
	@echo "Cleaning generated documents..."
	@rm -f worldbuilding-bible/export/*.pdf worldbuilding-bible/export/*.tex worldbuilding-bible/export/*.lof
	@rm -f game-design-document/export/*.pdf game-design-document/export/*.md
	@rm -f worldbuilding-bible/de/*.aux worldbuilding-bible/de/*.log worldbuilding-bible/de/*.out
	@rm -f game-design-document/de/*.aux game-design-document/de/*.log game-design-document/de/*.out
	@echo "✓ Cleaned all generated documents"
