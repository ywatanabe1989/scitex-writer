# Documentation Index

This directory contains comprehensive documentation for the SciTeX Writer template system. Files are organized with explicit descriptive prefixes for semantic clarity and easy navigation.

## Main Documentation (Root Level)

### Guides (01_GUIDE_*)
Procedural documentation for common tasks and workflows:
- **01_GUIDE_QUICK_START.md** - Quick reference for common tasks and basic workflows
- **01_GUIDE_CONTENT_CREATION.md** - Comprehensive guide for creating and managing figures and tables
- **01_GUIDE_AGENTS.md** - Guide for using AI agents and LLMs with the system

### Architecture (02_ARCHITECTURE_*)
Technical design and implementation details:
- **02_ARCHITECTURE.md** - System architecture, technical implementation, and troubleshooting guide

### Research (03_RESEARCH_*)
Lookup resources and standards for scientific writing:
- **03_RESEARCH_TERMINOLOGY.md** - Terminology guidelines and language conventions for scientific manuscripts

### External (04_EXTERNAL_*)
External resources and third-party references:
- **04_EXTERNAL_RESOURCES.md** - Comprehensive links to LaTeX, scientific writing, and research tools

## Subdirectories

### `to_claude/`
Configuration and guidelines for Claude Code integration:
- **agents/** - Individual agent specifications and responsibilities
- **bin/** - Utility scripts and tools
- **examples/** - Example projects and workflows
- **guidelines/** - Development guidelines organized by topic:
  - `command/` - Command reference guides
  - `elisp/` - Emacs Lisp development standards
  - `programming_common/` - General programming best practices
  - `project/` - Project-level standards
  - `python/` - Python-specific guidelines
  - `science/` - Scientific writing standards
  - `shell/` - Shell scripting guidelines

### `INSTRUCTIONS_TO_CLAUDE_CODE/`
Step-by-step instructions for Claude Code tasks:
- Custom Python management
- Project structure guidelines
- Testing strategies
- Shell scripting
- Git/GitHub workflows
- System information and troubleshooting

### `structure/`
- **structure.md** - Directory structure documentation
- **structure.mmd** - Mermaid diagram of repository structure

## Navigation Tips

1. **For quick answers**: Start with `01_GUIDE_QUICK_START.md`
2. **For figure/table creation**: See `01_GUIDE_CONTENT_CREATION.md`
3. **For AI agent and LLM setup**: Consult `01_GUIDE_AGENTS.md`
4. **For terminology guidance**: Check `03_RESEARCH_TERMINOLOGY.md`
5. **For technical architecture**: Review `02_ARCHITECTURE.md`
6. **For external resources**: See `04_EXTERNAL_RESOURCES.md`
7. **For Python development**: Check `to_claude/guidelines/python/` directory
8. **For project management**: Look in `to_claude/guidelines/project/`
9. **For scientific writing standards**: See `to_claude/guidelines/science/` directory

## File Naming Convention

Root-level documentation files use explicit descriptive prefixes for semantic meaning:

- **01_GUIDE_*** = Guide (procedural, how-to documentation)
  - `01_GUIDE_QUICK_START.md` - Quick reference for immediate needs
  - `01_GUIDE_CONTENT_CREATION.md` - Detailed creation processes
  - `01_GUIDE_AGENTS.md` - AI and LLM integration

- **02_ARCHITECTURE_*** = Architecture (technical design and implementation)
  - `02_ARCHITECTURE.md` - System design and technical details

- **03_RESEARCH_*** = Research (lookup materials, standards, terminology)
  - `03_RESEARCH_TERMINOLOGY.md` - Scientific writing conventions

- **04_EXTERNAL_*** = External (third-party resources and references)
  - `04_EXTERNAL_RESOURCES.md` - Links and external references

This prefix system provides immediate visual context about document purpose and category when viewing directory listings.

Subdirectory files within `to_claude/guidelines/` use numbered prefixes when they represent sequential steps or priority levels (e.g., `01_DEVELOPMENT_CYCLE.md`, `02_NAMING_CONVENSIONS.md`).
