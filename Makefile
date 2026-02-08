# Makefile for SciTeX Writer
# Usage: make [target]
# Author: ywatanabe
# Dependencies: Python 3.8+, compile scripts, Apptainer containers

GREEN := \033[0;32m
CYAN := \033[0;36m
NC := \033[0m

.PHONY: \
	manuscript-compile \
	supplementary-compile \
	revision-compile \
	manuscript-draft \
	supplementary-draft \
	revision-draft \
	manuscript-watch \
	supplementary-watch \
	revision-watch \
	init \
	manuscript-init \
	supplementary-init \
	revision-init \
	shared-init \
	restore \
	manuscript-restore \
	supplementary-restore \
	revision-restore \
	shared-restore \
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
	help \
	usage \
	usage-manuscript \
	usage-supplementary \
	usage-revision \
	usage-shared

# Default target - show help instead of compiling
.DEFAULT_GOAL := help

# ============================================================================
# Document compilation
# ============================================================================
manuscript-compile:
	@echo "Compiling manuscript..."
	./compile.sh manuscript --quiet

supplementary-compile:
	@echo "Compiling supplementary materials..."
	./compile.sh supplementary --quiet

revision-compile:
	@echo "Compiling revision responses..."
	./compile.sh revision --quiet

# ============================================================================
# Draft mode - fast compilation (skips bibliography)
# ============================================================================
manuscript-draft:
	@echo "Compiling manuscript (draft mode)..."
	./compile.sh manuscript --draft --quiet

supplementary-draft:
	@echo "Compiling supplementary (draft mode)..."
	./compile.sh supplementary --draft --quiet

revision-draft:
	@echo "Compiling revision (draft mode)..."
	./compile.sh revision --draft --quiet

# ============================================================================
# Watch mode - auto-recompile on file changes
# ============================================================================
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
# Initialize contents to clean template
# ============================================================================
init:
	@bash scripts/shell/initialize_contents.sh

shared-init:
	@bash scripts/shell/initialize_contents.sh shared

manuscript-init:
	@bash scripts/shell/initialize_contents.sh manuscript

supplementary-init:
	@bash scripts/shell/initialize_contents.sh supplementary

revision-init:
	@bash scripts/shell/initialize_contents.sh revision

# ============================================================================
# Restore contents from snapshot
# ============================================================================
restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)"
else
	@bash scripts/shell/restore_contents.sh
endif

shared-restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)" shared
else
	@bash scripts/shell/restore_contents.sh
endif

manuscript-restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)" manuscript
else
	@bash scripts/shell/restore_contents.sh
endif

supplementary-restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)" supplementary
else
	@bash scripts/shell/restore_contents.sh
endif

revision-restore:
ifdef ID
	@bash scripts/shell/restore_contents.sh "$(ID)" revision
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
	@printf "$(CYAN)🚀 Initialization:$(NC)\n"
	@echo "  make init                       Reset all contents to template"
	@echo "  make shared-init                Reset shared metadata only"
	@echo "  make manuscript-init            Reset manuscript only"
	@echo "  make supplementary-init         Reset supplementary only"
	@echo "  make revision-init              Reset revision only"
	@echo ""
	@printf "$(CYAN)🔧 Compilation:$(NC)\n"
	@echo ""
	@printf "  $(CYAN)📝 Full:$(NC)\n"
	@echo "    make manuscript-compile       Compile manuscript"
	@echo "    make supplementary-compile    Compile supplementary"
	@echo "    make revision-compile         Compile revision"
	@echo ""
	@printf "  $(CYAN)⚡ Draft (skips bibliography):$(NC)\n"
	@echo "    make manuscript-draft         Draft manuscript"
	@echo "    make supplementary-draft      Draft supplementary"
	@echo "    make revision-draft           Draft revision"
	@echo ""
	@printf "  $(CYAN)🔄 Watch (auto-recompile):$(NC)\n"
	@echo "    make manuscript-watch         Watch manuscript"
	@echo "    make supplementary-watch      Watch supplementary"
	@echo "    make revision-watch           Watch revision"
	@echo ""
	@printf "$(CYAN)🔙 Restoration:$(NC)\n"
	@echo "  make restore                    List available snapshots"
	@echo "  make restore ID=xxx             Restore all from snapshot"
	@echo "  make manuscript-restore ID=xxx  Restore manuscript only"
	@echo "  make supplementary-restore ID=xxx  Restore supplementary only"
	@echo "  make revision-restore ID=xxx    Restore revision only"
	@echo "  make shared-restore ID=xxx      Restore shared metadata only"
	@echo ""
	@printf "$(CYAN)📦 Python Package:$(NC)\n"
	@echo "  make python-install             Install package"
	@echo "  make python-develop             Install in dev mode"
	@echo "  make python-test                Run tests"
	@echo "  make python-build               Build distributions"
	@echo "  make python-upload              Upload to PyPI"
	@echo "  make python-upload-test         Upload to Test PyPI"
	@echo "  make python-update              Update to latest version"
	@echo "  make python-version             Show version"
	@echo ""
	@printf "$(CYAN)🧹 Cleaning:$(NC)\n"
	@echo "  make clean                      Remove temporary LaTeX files"
	@echo "  make clean-logs                 Remove log files"
	@echo "  make clean-archive              Remove archived versions"
	@echo "  make clean-compiled             Remove compiled tex/pdf files"
	@echo "  make clean-python               Remove Python build artifacts"
	@echo "  make clean-all                  Remove all generated files"
	@echo ""
	@printf "$(CYAN)📋 Information:$(NC)\n"
	@echo "  make status                     Show compilation status"
	@echo "  make help                       Show this help message"
	@echo "  make usage                  Show full project usage guide"

# Project usage guides
usage:
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
