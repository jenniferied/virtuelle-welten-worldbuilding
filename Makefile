# Makefile for ПАНЕЛЬКИ Worldbuilding Project

.PHONY: help worldbuilding gdd clean check-deps

help:
	@echo "ПАНЕЛЬКИ Worldbuilding Bible"
	@echo ""
	@echo "Commands:"
	@echo "  worldbuilding   Build worldbuilding bible PDF (LaTeX)"
	@echo "  gdd             Build game design document PDF"
	@echo "  all             Build both documents"
	@echo "  clean           Remove generated files"
	@echo "  check-deps      Check LaTeX dependencies"
	@echo ""
	@echo "Requirements:"
	@echo "  - Python 3.8+"
	@echo "  - Pandoc"
	@echo "  - LuaLaTeX (via MacTeX)"

# Build worldbuilding bible PDF
worldbuilding:
	@echo "Building Worldbuilding Bible..."
	@python3 scripts/build-worldbuilding.py --lang de

# Build GDD PDF
gdd:
	@echo "Building Game Design Document..."
	@python3 scripts/build-gdd.py

# Build all documents
all: worldbuilding gdd

# Check dependencies
check-deps:
	@python3 scripts/build-worldbuilding.py --check-deps

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf worldbuilding-bible/export/*.pdf
	@rm -rf worldbuilding-bible/export/*.tex
	@rm -rf worldbuilding-bible/export/*.aux
	@rm -rf worldbuilding-bible/export/*.log
	@rm -rf worldbuilding-bible/export/*.out
	@rm -rf worldbuilding-bible/export/*.toc
	@rm -rf worldbuilding-bible/export/*.lof
	@echo "Done."
