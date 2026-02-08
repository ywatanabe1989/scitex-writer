# Makefile for SciTeX Writer
# Usage: make [target] [DOC=manuscript|supplementary|revision]
# Author: ywatanabe
# Dependencies: Python 3.8+, compile scripts, Apptainer containers

GREEN := \033[0;32m
CYAN := \033[0;36m
NC := \033[0m

# Document type argument (default: all)
DOC ?=

.PHONY: \
	all \
	compile \
	manuscript \
	supplementary \
	revision \
	all-watch \
	manuscript-watch \
	supplementary-watch \
	revision-watch \
	draft \
	python-install \
	python-develop \
	python-test \
	python-build \
	python-upload \
	python-upload-test \
	python-update \
	python-version \
	clean \
	clean-logs \
	clean-archive \
	clean-compiled \
	clean-python \
	clean-all \
	init \
	initialize-contents \
	restore \
	help \
	usage-all \
	usage-manuscript \
	usage-supplementary \
	usage-revision \
	usage-shared

# Default target - show help instead of compiling
.DEFAULT_GOAL := help

# ============================================================================
# Document compilation
# ============================================================================
all: manuscript supplementary revision

# Generic compile target with DOC= support
compile:
ifdef DOC
	@echo "Compiling $(DOC)..."
	./compile.sh $(DOC) --quiet
else
	@$(MAKE) --no-print-directory all
endif

manuscript:
	@echo "Compiling manuscript..."
	./compile.sh manuscript --quiet

supplementary:
	@echo "Compiling supplementary materials..."
	./compile.sh supplementary --quiet

revision:
	@echo "Compiling revision responses..."
	./compile.sh revision --quiet

# Draft mode - fast compilation (skips bibliography)
draft:
ifdef DOC
	@echo "Compiling $(DOC) (draft mode)..."
	./compile.sh $(DOC) --draft --quiet
else
	@echo "Compiling manuscript (draft mode)..."
	./compile.sh manuscript --draft --quiet
endif

# ============================================================================
# Watch mode - auto-recompile on file changes
# ============================================================================
all-watch:
	@echo "Starting all-documents watch mode (Ctrl+C to stop)..."
	./compile.sh all --watch

manuscript-watch:
	@echo "Starting manuscript watch mode (Ctrl+C to stop)..."
	./compile.sh manuscript --watch

supplementary-watch:
	@echo "Starting supplementary watch mode (Ctrl+C to stop)..."
	./compile.sh supplementary --watch

revision-watch:
	@echo "Starting revision watch mode (Ctrl+C to stop)..."
	./compile.sh revision --watch

# ============================================================================
# Initialize and restore contents
# ============================================================================
init: initialize-contents
initialize-contents:
ifdef DOC
	@bash scripts/shell/initialize_contents.sh $(DOC)
else
	@bash scripts/shell/initialize_contents.sh
endif

restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)"
else
	@bash scripts/shell/restore_contents.sh
endif

# ============================================================================
# Python package targets
# ============================================================================
python-install:
	@echo "Installing scitex-writer..."
	pip install .

python-develop:
	@echo "Installing scitex-writer in development mode..."
	pip install -e .

python-test:
	@echo "Running tests..."
	pytest tests/ -v

python-build:
	@echo "Building distribution packages..."
	python -m build

python-upload:
	@echo "Uploading to PyPI..."
	python -m twine upload dist/*

python-upload-test:
	@echo "Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

python-update:
	@echo "Updating scitex-writer..."
	./scripts/maintenance/update.sh

python-version:
	@echo "SciTeX Writer $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '\"')"

demo-previews:
	@echo "Generating demo preview images for README..."
	./scripts/maintenance/generate_demo_previews.sh

# ============================================================================
# Cleaning targets
# ============================================================================
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

# ============================================================================
# Status and information
# ============================================================================
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
	@echo ""
	@printf "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)\n"
	@printf "$(GREEN)║     SciTeX Writer v%-5s - LaTeX Manuscript System    ║$(NC)\n" "$(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '\"')"
	@printf "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)\n"
	@echo ""
	@printf "$(CYAN)🚀 Getting Started:$(NC)\n"
	@echo "  make init                 Reset all contents to clean template"
	@echo "  make init DOC=manuscript  Reset only manuscript contents"
	@echo "  make restore              List available snapshots"
	@echo "  make restore ID=xxx       Restore contents from a snapshot"
	@echo ""
	@printf "$(CYAN)📄 Document Compilation:$(NC)\n"
	@echo "  make all                  Compile all documents"
	@echo "  make manuscript           Compile manuscript"
	@echo "  make supplementary        Compile supplementary materials"
	@echo "  make revision             Compile revision responses"
	@echo "  make compile DOC=xxx      Compile specific document"
	@echo "  make draft                Fast draft (manuscript, skips bib)"
	@echo "  make draft DOC=xxx        Fast draft for specific document"
	@echo ""
	@printf "$(CYAN)🔄 Watch Mode (auto-recompile):$(NC)\n"
	@echo "  make all-watch            Watch all documents"
	@echo "  make manuscript-watch     Watch manuscript"
	@echo "  make supplementary-watch  Watch supplementary"
	@echo "  make revision-watch       Watch revision"
	@echo ""
	@printf "$(CYAN)📦 Python Package:$(NC)\n"
	@echo "  make python-install       Install scitex-writer package"
	@echo "  make python-develop       Install in development mode"
	@echo "  make python-test          Run tests"
	@echo "  make python-build         Build distribution packages"
	@echo "  make python-upload        Upload to PyPI"
	@echo "  make python-upload-test   Upload to Test PyPI"
	@echo "  make python-update        Update to latest version"
	@echo "  make python-version       Show version"
	@echo ""
	@printf "$(CYAN)🧹 Cleaning:$(NC)\n"
	@echo "  make clean                Remove temporary LaTeX files"
	@echo "  make clean-logs           Remove log files"
	@echo "  make clean-archive        Remove archived versions"
	@echo "  make clean-compiled       Remove compiled tex/pdf files"
	@echo "  make clean-python         Remove Python build artifacts"
	@echo "  make clean-all            Remove all generated files"
	@echo ""
	@printf "$(CYAN)📋 Information:$(NC)\n"
	@echo "  make status               Show compilation status"
	@echo "  make help                 Show this help message"
	@echo "  make usage-all            Show full project usage guide"

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
