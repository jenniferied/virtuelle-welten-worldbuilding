# Makefile for ПАНЕЛЬКИ Worldbuilding Project

.PHONY: help dev build export clean

help:
	@echo "ПАНЕЛЬКИ Worldbuilding Bible"
	@echo ""
	@echo "Commands:"
	@echo "  dev       Start Slidev dev server with hot reload"
	@echo "  build     Build static site"
	@echo "  export    Export to PDF (16:9)"
	@echo "  clean     Remove generated files"
	@echo ""
	@echo "Requirements:"
	@echo "  - Node.js 18+"
	@echo "  - npm install (run once)"

# Start development server
dev:
	@echo "Starting Slidev dev server..."
	@cd worldbuilding-bible && npm run dev

# Build static site
build:
	@echo "Building static site..."
	@cd worldbuilding-bible && npm run build
	@echo "✓ Built to worldbuilding-bible/dist/"

# Export to PDF
export:
	@echo "Exporting to PDF..."
	@mkdir -p worldbuilding-bible/export
	@cd worldbuilding-bible && npm run export
	@echo "✓ PDF: worldbuilding-bible/export/worldbuilding-bible.pdf"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf worldbuilding-bible/dist
	@rm -rf worldbuilding-bible/export/*.pdf
	@rm -rf worldbuilding-bible/node_modules/.cache
	@echo "✓ Cleaned"

# Install dependencies (run once)
install:
	@echo "Installing dependencies..."
	@cd worldbuilding-bible && npm install
	@echo "✓ Dependencies installed"
