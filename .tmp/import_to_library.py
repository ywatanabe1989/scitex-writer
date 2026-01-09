#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import enriched BibTeX into scitex.scholar library system
Creates proper directory structure with metadata.json files
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "proj/scitex-code/src"))

from scitex import logging
from scitex.scholar.storage.BibTeXHandler import BibTeXHandler
from scitex.scholar.storage.ScholarLibrary import ScholarLibrary
from scitex.scholar.config import ScholarConfig
from scitex.scholar.core.Papers import Papers

logger = logging.getLogger(__name__)


def import_bibliography_to_library():
    """Import enriched bibliography into scholar library."""

    # Paths
    bib_file = Path.home() / "proj/scitex-writer/00_shared/bib_files/enriched_all.bib"
    project_name = "scitex-writer-refs"

    logger.info(f"Importing bibliography: {bib_file}")
    logger.info(f"Project name: {project_name}")

    # Initialize
    config = ScholarConfig()
    library = ScholarLibrary(project=project_name, config=config)
    handler = BibTeXHandler(project=project_name, config=config)

    # Load papers from BibTeX
    logger.info("Loading papers from BibTeX...")
    papers_list = handler.papers_from_bibtex(bib_file)
    papers = Papers(papers_list, project=project_name, config=config)

    logger.info(f"Loaded {len(papers)} papers")

    # Get library paths
    master_dir = config.path_manager.get_library_master_dir()
    project_dir = config.path_manager.get_library_project_dir(project_name)

    logger.info(f"Master directory: {master_dir}")
    logger.info(f"Project directory: {project_dir}")

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create info directory for project metadata
    info_dir = project_dir / "info"
    info_dir.mkdir(exist_ok=True)

    # Save original BibTeX in info directory
    bib_backup = info_dir / "enriched_all.bib"
    import shutil
    shutil.copy(bib_file, bib_backup)
    logger.info(f"Saved BibTeX backup to: {bib_backup}")

    print("\n" + "="*80)
    print("IMPORTING PAPERS TO LIBRARY")
    print("="*80)

    stats = {
        'total': len(papers),
        'saved': 0,
        'symlinks': 0,
        'errors': 0
    }

    # Process each paper
    for i, paper in enumerate(papers, 1):
        title = paper.metadata.basic.title[:60] if paper.metadata.basic.title else "No title"
        print(f"\n[{i}/{len(papers)}] {title}...")

        try:
            # Save paper to MASTER directory (this creates metadata.json)
            paper_id = library.save_paper(paper)

            if paper_id:
                stats['saved'] += 1
                logger.success(f"  ✓ Saved to MASTER/{paper_id}")

                # Create human-readable symlink in project directory
                # Format: AUTHOR-YEAR-JOURNAL
                authors = paper.metadata.basic.authors
                year = paper.metadata.basic.year or "NoYear"
                journal = paper.metadata.publication.journal

                # Build symlink name
                if authors and len(authors) > 0:
                    first_author = authors[0].split()[-1]  # Last name
                else:
                    first_author = "Unknown"

                if journal:
                    # Clean journal name for filename
                    journal_clean = journal.replace(" ", "-")[:30]
                    symlink_name = f"{first_author}-{year}-{journal_clean}"
                else:
                    symlink_name = f"{first_author}-{year}"

                # Create symlink
                symlink_path = project_dir / symlink_name
                master_path = master_dir / paper_id

                # Remove existing symlink if it exists
                if symlink_path.exists() or symlink_path.is_symlink():
                    symlink_path.unlink()

                # Create relative symlink
                try:
                    symlink_path.symlink_to(f"../MASTER/{paper_id}")
                    stats['symlinks'] += 1
                    logger.info(f"  ✓ Symlink: {symlink_name} -> MASTER/{paper_id}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not create symlink: {e}")
            else:
                logger.warning(f"  ⚠️  No paper ID returned")

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            stats['errors'] += 1

    # Summary
    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print(f"\nStatistics:")
    print(f"  Total papers: {stats['total']}")
    print(f"  Saved to MASTER: {stats['saved']}")
    print(f"  Symlinks created: {stats['symlinks']}")
    print(f"  Errors: {stats['errors']}")

    print(f"\nLibrary structure:")
    print(f"  MASTER: {master_dir}")
    print(f"  Project: {project_dir}")
    print(f"  BibTeX backup: {bib_backup}")

    # Generate summary file
    summary_file = info_dir / "import_summary.txt"
    summary_lines = []
    summary_lines.append("="*80)
    summary_lines.append("SCITEX.SCHOLAR LIBRARY IMPORT SUMMARY")
    summary_lines.append("="*80)
    summary_lines.append("")
    from datetime import datetime
    summary_lines.append(f"Project: {project_name}")
    summary_lines.append(f"Source: {bib_file}")
    summary_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    summary_lines.append("STATISTICS:")
    summary_lines.append(f"  Total papers: {stats['total']}")
    summary_lines.append(f"  Saved to MASTER: {stats['saved']}")
    summary_lines.append(f"  Symlinks created: {stats['symlinks']}")
    summary_lines.append(f"  Errors: {stats['errors']}")
    summary_lines.append("")
    summary_lines.append("DIRECTORY STRUCTURE:")
    summary_lines.append(f"  {master_dir}/")
    summary_lines.append(f"    8DIGIT01/metadata.json")
    summary_lines.append(f"    8DIGIT02/metadata.json")
    summary_lines.append(f"    ...")
    summary_lines.append("")
    summary_lines.append(f"  {project_dir}/")
    summary_lines.append(f"    Author-Year-Journal -> ../MASTER/8DIGIT01")
    summary_lines.append(f"    ...")
    summary_lines.append("")
    summary_lines.append("="*80)

    summary_file.write_text("\n".join(summary_lines))
    print(f"\nSummary saved to: {summary_file}")

    logger.success("\n✓ Import complete!")

    return stats


if __name__ == "__main__":
    import_bibliography_to_library()
