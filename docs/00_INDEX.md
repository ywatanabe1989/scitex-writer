# Documentation Index

This directory contains comprehensive documentation for the SciTeX Writer template system. Files are organized with numerical prefixes for easy navigation.

## Main Documentation (Root Level)

### Getting Started
- **01_AI_AGENT_GUIDE.md** - Guide for using AI agents with the template system
- **02_QUICK_REFERENCE.md** - Quick lookup reference for common tasks
- **08_USAGE_FOR_LLM.md** - Best practices for using with LLMs

### Content Creation
- **03_FIGURE_TABLE_GUIDE.md** - Comprehensive guide for figures and tables
- **04_MULTIPANEL_FIGURE_GUIDE.md** - Specialized guide for multipanel figures
- **05_CROSS_REFERENCING.md** - How to properly cross-reference figures and tables
- **06_TABLE_FORMAT_OPTIONS.md** - Available table formatting options

### Reference
- **07_IMPLEMENTATION_SUMMARY.md** - Technical implementation overview
- **09_NON_SCIENTIFIC_TERMS.md** - Guidance on terminology usage
- **10_FROM_OPENAI.md** - Information from OpenAI resources

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

1. **For quick answers**: Start with `02_QUICK_REFERENCE.md`
2. **For figure/table work**: See `03_FIGURE_TABLE_GUIDE.md` or `04_MULTIPANEL_FIGURE_GUIDE.md`
3. **For AI agent setup**: Consult `01_AI_AGENT_GUIDE.md`
4. **For Python development**: Check `to_claude/guidelines/python/` directory
5. **For project management**: Look in `to_claude/guidelines/project/`
6. **For scientific writing**: See `to_claude/guidelines/science/` directory

## File Naming Convention

Root-level documentation files use two-digit numerical prefixes (`01_`, `02_`, etc.) to maintain alphabetical ordering and clarity when viewing directory listings.

Subdirectory files within `to_claude/guidelines/` use numbered prefixes when they represent sequential steps or priority levels (e.g., `01_DEVELOPMENT_CYCLE.md`, `02_NAMING_CONVENSIONS.md`).

Files prefixed with `IMPORTANT-` indicate critical information that should be reviewed before starting work.
