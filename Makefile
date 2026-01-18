# Makefile for SciTeX Writer
# Usage: make [target]
# Author: ywatanabe
# Dependencies: Python 3.8+, compile scripts, Apptainer containers

.PHONY: \
	all \
	manuscript \
	supplementary \
	revision \
	install \
	develop \
	test \
	build \
	upload \
	update \
	clean \
	clean-logs \
	clean-cache \
	clean-compiled \
	clean-python \
	clean-all \
	help \
	usage-all \
	usage-manuscript \
	usage-supplementary \
	usage-revision \
	usage-shared

# Default target - show help instead of compiling
.DEFAULT_GOAL := help

all: manuscript supplementary revision

# Document compilation targets
manuscript:
	@echo "Compiling manuscript..."
	./compile.sh manuscript --quiet

supplementary:
	@echo "Compiling supplementary materials..."
	./compile.sh supplementary --quiet

revision:
	@echo "Compiling revision responses..."
	./compile.sh revision --quiet

# Python package targets
install:
	@echo "Installing scitex-writer..."
	pip install .

develop:
	@echo "Installing scitex-writer in development mode..."
	pip install -e .

test:
	@echo "Running tests..."
	pytest tests/ -v

build:
	@echo "Building distribution packages..."
	python -m build

upload:
	@echo "Uploading to PyPI..."
	python -m twine upload dist/*

upload-test:
	@echo "Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

update:
	@echo "Updating scitex-writer..."
	./scripts/maintenance/update.sh

version:
	@echo "SciTeX Writer $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '\"')"

demo-previews:
	@echo "Generating demo preview images for README..."
	./scripts/maintenance/generate_demo_previews.sh

# Cleaning targets
clean:
	@echo "Cleaning temporary files..."
	rm -f ./01_manuscript/*.{aux,log,bbl,blg,out,toc,fls,fdb_latexmk,synctex.gz}
	rm -f ./02_supplementary/*.{aux,log,bbl,blg,out,toc,fls,fdb_latexmk,synctex.gz}
	rm -f ./03_revision/*.{aux,log,bbl,blg,out,toc,fls,fdb_latexmk,synctex.gz}

clean-logs:
	@echo "Cleaning log directories..."
	rm -rf ./01_manuscript/logs/*
	rm -rf ./02_supplementary/logs/*
	rm -rf ./03_revision/logs/*
	rm -rf ./logs/*

clean-archive:
	@echo "Cleaning archive directories..."
	rm -rf ./01_manuscript/archive/*
	rm -rf ./02_supplementary/archive/*
	rm -rf ./03_revision/archive/*

clean-compiled:
	@echo "Cleaning compiled tex/pdf files..."
	rm -f ./01_manuscript/{manuscript.pdf,manuscript.tex,manuscript_diff.pdf,manuscript_diff.tex}
	rm -f ./02_supplementary/{supplementary.pdf,supplementary.tex,supplementary_diff.pdf,supplementary_diff.tex}
	rm -f ./03_revision/{revision.pdf,revision.tex,revision_diff.pdf,revision_diff.tex}

clean-python:
	@echo "Cleaning Python build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean clean-logs clean-archive clean-compiled clean-python
	@echo "Deep cleaning all generated files..."

# Status and information
status:
	@echo "=== Paper Compilation Status ==="
	@echo "Manuscript PDF:     $(shell [ -f ./01_manuscript/manuscript.pdf ] && echo "✓ Available" || echo "✗ Missing")"
	@echo "Supplementary PDF:  $(shell [ -f ./02_supplementary/supplementary.pdf ] && echo "✓ Available" || echo "✗ Missing")"
	@echo "Revision PDF:       $(shell [ -f ./03_revision/revision.pdf ] && echo "✓ Available" || echo "✗ Missing")"
	@echo ""
	@echo "Container Cache:"
	@ls -lh ./.cache/containers/*.sif 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  No containers cached"

# Help target
help:
	@echo "SciTeX Writer - LaTeX Compilation System for Scientific Documents"
	@echo "Version: $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '\"')"
	@echo ""
	@echo "Document Compilation:"
	@echo "  all              - Compile all documents (default)"
	@echo "  manuscript       - Compile manuscript"
	@echo "  supplementary    - Compile supplementary materials"
	@echo "  revision         - Compile revision responses"
	@echo ""
	@echo "Python Package:"
	@echo "  install          - Install scitex-writer package"
	@echo "  develop          - Install in development mode"
	@echo "  test             - Run tests"
	@echo "  build            - Build distribution packages"
	@echo "  upload           - Upload to PyPI"
	@echo "  upload-test      - Upload to Test PyPI"
	@echo "  update           - Update to latest version"
	@echo "  version          - Show version"
	@echo "  demo-previews    - Generate demo preview images for README"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean            - Remove temporary LaTeX files"
	@echo "  clean-logs       - Remove log files"
	@echo "  clean-archive    - Remove archived versions"
	@echo "  clean-compiled   - Remove compiled tex/pdf files"
	@echo "  clean-python     - Remove Python build artifacts"
	@echo "  clean-all        - Remove all generated files"
	@echo ""
	@echo "Information:"
	@echo "  status           - Show compilation status"
	@echo "  help             - Show this help message"
	@echo "  usage-all        - Show full project usage guide"
	@echo "  usage-manuscript - Show manuscript usage"
	@echo "  usage-supplementary - Show supplementary usage"
	@echo "  usage-revision   - Show revision usage"
	@echo "  usage-shared     - Show shared files info"
	@echo ""
	@echo "Examples:"
	@echo "  make manuscript         # Compile manuscript"
	@echo "  make develop            # Install for development"
	@echo "  make test               # Run tests"
	@echo "  make update             # Update to latest version"
	@echo "  make clean-all          # Clean everything"

# Project usage guides
usage-all:
	@./scripts/maintenance/show_usage.sh

usage-manuscript:
	@./scripts/shell/compile_manuscript.sh --help

usage-supplementary:
	@./scripts/shell/compile_supplementary.sh --help

usage-revision:
	@./scripts/shell/compile_revision.sh --help

usage-shared:
	@echo "━━━ 00_shared/ - Shared Metadata ━━━"
	@echo ""
	@echo "Files shared across all document types:"
	@echo "  title.tex        - Manuscript title"
	@echo "  authors.tex      - Author list and affiliations"
	@echo "  keywords.tex     - Keywords for the manuscript"
	@echo "  journal_name.tex - Target journal name"
	@echo "  bib_files/*.bib  - Bibliography files (auto-merged and deduplicated)"
	@echo ""
	@echo "Location: $(CURDIR)/00_shared/"
	@echo ""
	@echo "These files are automatically included in all document types"
	@echo "(manuscript, supplementary, revision)."
