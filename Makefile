# Makefile for NeuroVista Paper Compilation System
# Usage: make [target]
# Author: ywatanabe
# Dependencies: compile script, Apptainer containers

.PHONY: \
	all \
	manuscript \
	supplementary \
	revision \
	clean \
	clean-logs \
	clean-cache \
	clean-compiled \
	clean-all \
	help

# Default target
all: manuscript supplementary revision

# Document compilation targets
manuscript:
	@echo "Compiling manuscript..."
	./compile manuscript --quiet

supplementary:
	@echo "Compiling supplementary materials..."
	./compile supplementary --quiet

revision:
	@echo "Compiling revision responses..."
	./compile revision --quiet

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

clean-all: clean clean-logs clean-archive clean-compiled
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
	@echo "NeuroVista Paper Compilation System"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Compile manuscript (default)"
	@echo "  manuscript       - Compile manuscript"
	@echo "  supplementary    - Compile supplementary materials"
	@echo "  revision         - Compile revision responses"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean            - Remove temporary LaTeX files"
	@echo "  clean-logs       - Remove log files"
	@echo "  clean-archive    - Remove archived versions"
	@echo "  clean-cache      - Remove container cache"
	@echo "  clean-compiled      - Remove compiled tex/pdf files"
	@echo "  clean-all        - Remove all generated files"
	@echo ""
	@echo "Information:"
	@echo "  status           - Show compilation status"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make manuscript"
	@echo "  make supplementary-quiet"
	@echo "  make revision-force"
	@echo "  make clean-all"
