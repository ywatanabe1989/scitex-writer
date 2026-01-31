.. SciTeX Writer documentation master file

SciTeX Writer - LaTeX Manuscript Compilation
=============================================

**SciTeX Writer** is a LaTeX manuscript compilation system designed for scientific documents. It provides three interfaces: Python API, CLI, and MCP server for AI agents.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/scitex_writer

Key Features
------------

- **Three Interfaces**: Python API, CLI commands, and MCP server (28 tools)
- **Container-based Compilation**: Consistent LaTeX compilation across environments
- **Document Types**: Manuscript, Supplementary, and Revision documents
- **Bibliography Management**: BibTeX handling with list, add, remove, merge operations
- **Figure/Table Management**: Automatic format conversion and organization
- **AI Integration**: MCP server for AI agent workflows

Quick Example
-------------

Python API:

.. code-block:: python

    import scitex_writer as sw

    # Clone a template project
    sw.project.clone("template", "/path/to/new/project")

    # Compile manuscript
    result = sw.compile.manuscript("/path/to/project")

    # List bibliography entries
    entries = sw.bib.list("/path/to/project")

CLI:

.. code-block:: bash

    # Clone template
    scitex-writer clone template /path/to/new/project

    # Compile manuscript
    scitex-writer compile manuscript /path/to/project

    # List bibliography entries
    scitex-writer bib list /path/to/project

MCP Server:

.. code-block:: bash

    # Start MCP server
    scitex-writer mcp start

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
