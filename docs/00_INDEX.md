# Documentation Index

This directory contains comprehensive documentation for the SciTeX Writer template system. Files are organized with class-based prefixes for semantic clarity and easy navigation.

## Main Documentation (Root Level)

### Guides (G_)
Procedural documentation for common tasks and workflows:
- **G_QUICK_START.md** - Quick reference for common tasks and basic workflows
- **G_CONTENT_CREATION.md** - Comprehensive guide for creating and managing figures and tables
- **G_AGENTS.md** - Guide for using AI agents and LLMs with the system

### Reference (R_)
Lookup resources and standards for scientific writing:
- **R_TERMINOLOGY.md** - Terminology guidelines and language conventions for scientific manuscripts

### Architecture (A_)
Technical design and implementation details:
- **A_IMPLEMENTATION.md** - System architecture, technical implementation, and troubleshooting guide

### External (X_)
External resources and third-party references:
- **X_EXTERNAL_RESOURCES.md** - Comprehensive links to LaTeX, scientific writing, and research tools

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

1. **For quick answers**: Start with `G_QUICK_START.md`
2. **For figure/table creation**: See `G_CONTENT_CREATION.md`
3. **For AI agent and LLM setup**: Consult `G_AGENTS.md`
4. **For terminology guidance**: Check `R_TERMINOLOGY.md`
5. **For technical architecture**: Review `A_IMPLEMENTATION.md`
6. **For external resources**: See `X_EXTERNAL_RESOURCES.md`
7. **For Python development**: Check `to_claude/guidelines/python/` directory
8. **For project management**: Look in `to_claude/guidelines/project/`
9. **For scientific writing standards**: See `to_claude/guidelines/science/` directory

## File Naming Convention

Root-level documentation files use class-based prefixes for semantic meaning:

- **G_** = Guide (procedural, how-to documentation)
- **R_** = Reference (lookup materials, standards, terminology)
- **A_** = Architecture (technical design and implementation)
- **I_** = Important (critical core information)
- **T_** = Tutorial (learning materials with detailed steps)
- **E_** = Example (demonstrations and sample workflows)
- **X_** = External (third-party resources and references)

This prefix system provides immediate visual context about document purpose when viewing directory listings.

Subdirectory files within `to_claude/guidelines/` use numbered prefixes when they represent sequential steps or priority levels (e.g., `01_DEVELOPMENT_CYCLE.md`, `02_NAMING_CONVENSIONS.md`).

Files prefixed with `IMPORTANT-` indicate critical information that should be reviewed before starting work.
