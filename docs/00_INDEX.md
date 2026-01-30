# Documentation Index

This directory contains comprehensive documentation for the SciTeX Writer template system. Files are organized with explicit descriptive prefixes for semantic clarity and easy navigation.

## Main Documentation (Root Level)

### Guides (01_GUIDE_*)
Procedural documentation for common tasks and workflows:
- **01_GUIDE_QUICK_START.md** - Quick reference for common tasks and basic workflows
- **01_GUIDE_INSTALLATION.md** - Setup for all environments
- **01_GUIDE_BIBLIOGRAPHY.md** - Complete guide to bibliography management with multi-file support and caching
- **01_GUIDE_CONTENT_CREATION.md** - Comprehensive guide for creating and managing figures and tables
- **01_GUIDE_AGENTS.md** - Guide for using AI agents and LLMs with the system

### Architecture (02_ARCHITECTURE_*)
Technical design and implementation details:
- **02_ARCHITECTURE_IMPLEMENTATION.md** - System architecture, technical implementation, and troubleshooting guide

### MCP Tools
- **MCP_TOOLS.md** - Reference for all 29 MCP tools for AI agent integration

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
2. **For installation**: See `01_GUIDE_INSTALLATION.md`
3. **For bibliography management**: See `01_GUIDE_BIBLIOGRAPHY.md`
4. **For figure/table creation**: See `01_GUIDE_CONTENT_CREATION.md`
5. **For AI agent and LLM setup**: Consult `01_GUIDE_AGENTS.md`
6. **For technical architecture**: Review `02_ARCHITECTURE_IMPLEMENTATION.md`
7. **For MCP tools reference**: See `MCP_TOOLS.md`
8. **For Python development**: Check `to_claude/guidelines/python/` directory
9. **For project management**: Look in `to_claude/guidelines/project/`
10. **For scientific writing standards**: See `to_claude/guidelines/science/` directory

## File Naming Convention

Root-level documentation files use explicit descriptive prefixes for semantic meaning:

- **01_GUIDE_*** = Guide (procedural, how-to documentation)
  - `01_GUIDE_QUICK_START.md` - Quick reference for immediate needs
  - `01_GUIDE_INSTALLATION.md` - Setup for all environments
  - `01_GUIDE_BIBLIOGRAPHY.md` - Bibliography management and organization
  - `01_GUIDE_CONTENT_CREATION.md` - Detailed creation processes
  - `01_GUIDE_AGENTS.md` - AI and LLM integration

- **02_ARCHITECTURE_*** = Architecture (technical design and implementation)
  - `02_ARCHITECTURE_IMPLEMENTATION.md` - System design and technical details

This prefix system provides immediate visual context about document purpose and category when viewing directory listings.

Subdirectory files within `to_claude/guidelines/` use numbered prefixes when they represent sequential steps or priority levels (e.g., `01_DEVELOPMENT_CYCLE.md`, `02_NAMING_CONVENSIONS.md`).
