#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge and enrich BibTeX files from scitex-writer project
Using scitex.scholar tools for intelligent merging and metadata enrichment
"""

import asyncio
from pathlib import Path
import sys

# Add scitex.scholar to path
sys.path.insert(0, str(Path.home() / "proj/scitex-code/src"))

from scitex import logging
from scitex.scholar.storage.BibTeXHandler import BibTeXHandler
from scitex.scholar.pipelines.ScholarPipelineMetadataSingle import ScholarPipelineMetadataSingle
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def merge_and_enrich():
    """Merge and enrich all BibTeX files."""

    # Input directory
    bib_dir = Path.home() / "proj/scitex-writer/00_shared/bib_files"

    # Output files
    output_merged = bib_dir / "merged_all.bib"
    output_enriched = bib_dir / "enriched_all.bib"
    summary_file = bib_dir / "enrichment_summary.txt"

    # Find all BibTeX files (excluding output files and empty files)
    bib_files = []
    for file in bib_dir.glob("*.bib"):
        if file.name in ["merged_all.bib", "enriched_all.bib"]:
            continue
        if file.stat().st_size == 0:
            logger.info(f"Skipping empty file: {file.name}")
            continue
        bib_files.append(file)

    logger.info(f"Found {len(bib_files)} BibTeX files to merge:")
    for f in bib_files:
        logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")

    # Initialize handlers
    config = ScholarConfig()
    handler = BibTeXHandler(project="scitex-writer", config=config)
    enricher = ScholarPipelineMetadataSingle(config=config)

    # Step 1: Merge all BibTeX files
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Merging BibTeX files with smart deduplication")
    logger.info("="*80)

    result = handler.merge_bibtex_files(
        file_paths=bib_files,
        output_path=output_merged,
        dedup_strategy="smart",
        return_details=True
    )

    merged_papers = result["papers"]
    stats = result["stats"]

    logger.success(f"\nMerge complete:")
    logger.info(f"  Total entries loaded: {stats['total_input']}")
    logger.info(f"  Unique entries: {stats['unique_papers']}")
    logger.info(f"  Duplicates found: {stats['duplicates_found']}")
    logger.info(f"  Duplicates merged: {stats['duplicates_merged']}")
    logger.info(f"  Saved to: {output_merged}")

    # Step 2: Enrich metadata
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Enriching metadata (DOIs, abstracts, citations)")
    logger.info("="*80)

    enrichment_stats = {
        'total_papers': len(merged_papers.papers),
        'enriched_count': 0,
        'failed_count': 0,
        'with_doi': 0,
        'with_abstract': 0,
        'with_citations': 0,
    }

    enriched_papers = []

    for i, paper in enumerate(merged_papers.papers, 1):
        title = paper.metadata.basic.title[:60] if paper.metadata.basic.title else "No title"
        logger.info(f"\n[{i}/{len(merged_papers.papers)}] Enriching: {title}...")

        try:
            # Track what we had before
            had_doi = bool(paper.metadata.id.doi)
            had_abstract = bool(paper.metadata.basic.abstract)
            had_citations = bool(paper.metadata.citation_count.total)

            # Enrich
            enriched_paper = await enricher.enrich_paper_async(paper, force=False)

            # Track what we have now
            has_doi = bool(enriched_paper.metadata.id.doi)
            has_abstract = bool(enriched_paper.metadata.basic.abstract)
            has_citations = bool(enriched_paper.metadata.citation_count.total)

            # Update stats
            if has_doi:
                enrichment_stats['with_doi'] += 1
            if has_abstract:
                enrichment_stats['with_abstract'] += 1
            if has_citations:
                enrichment_stats['with_citations'] += 1

            # Check if we actually enriched anything
            if (not had_doi and has_doi) or \
               (not had_abstract and has_abstract) or \
               (not had_citations and has_citations):
                enrichment_stats['enriched_count'] += 1
                logger.success(f"  ✓ Enriched (DOI: {has_doi}, Abstract: {has_abstract}, Citations: {has_citations})")
            else:
                logger.info(f"  - Already complete (DOI: {has_doi}, Abstract: {has_abstract}, Citations: {has_citations})")

            enriched_papers.append(enriched_paper)

        except Exception as e:
            logger.error(f"  ✗ Failed to enrich: {e}")
            enrichment_stats['failed_count'] += 1
            enriched_papers.append(paper)  # Keep original

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

    # Step 3: Save enriched bibliography
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Saving enriched bibliography")
    logger.info("="*80)

    from scitex.scholar.core.Papers import Papers
    enriched_collection = Papers(enriched_papers, project="scitex-writer")

    handler.papers_to_bibtex(
        enriched_collection,
        output_path=output_enriched
    )

    logger.success(f"Saved enriched bibliography to: {output_enriched}")

    # Step 4: Generate summary
    logger.info("\n" + "="*80)
    logger.info("STEP 4: Generating summary")
    logger.info("="*80)

    summary_lines = []
    summary_lines.append("="*80)
    summary_lines.append("BibTeX Merge and Enrichment Summary")
    summary_lines.append("="*80)
    summary_lines.append("")
    summary_lines.append("INPUT FILES:")
    for f in bib_files:
        summary_lines.append(f"  - {f.name}")
    summary_lines.append("")
    summary_lines.append("MERGE STATISTICS:")
    summary_lines.append(f"  Total entries loaded: {stats['total_input']}")
    summary_lines.append(f"  Unique entries: {stats['unique_papers']}")
    summary_lines.append(f"  Duplicates found: {stats['duplicates_found']}")
    summary_lines.append(f"  Duplicates merged: {stats['duplicates_merged']}")
    summary_lines.append("")
    summary_lines.append("ENRICHMENT STATISTICS:")
    summary_lines.append(f"  Total papers: {enrichment_stats['total_papers']}")
    summary_lines.append(f"  Papers enriched: {enrichment_stats['enriched_count']}")
    summary_lines.append(f"  Failed to enrich: {enrichment_stats['failed_count']}")
    summary_lines.append(f"  Papers with DOI: {enrichment_stats['with_doi']} ({100*enrichment_stats['with_doi']/enrichment_stats['total_papers']:.1f}%)")
    summary_lines.append(f"  Papers with abstract: {enrichment_stats['with_abstract']} ({100*enrichment_stats['with_abstract']/enrichment_stats['total_papers']:.1f}%)")
    summary_lines.append(f"  Papers with citations: {enrichment_stats['with_citations']} ({100*enrichment_stats['with_citations']/enrichment_stats['total_papers']:.1f}%)")
    summary_lines.append("")
    summary_lines.append("OUTPUT FILES:")
    summary_lines.append(f"  - {output_merged.name} (merged)")
    summary_lines.append(f"  - {output_enriched.name} (enriched)")
    summary_lines.append("="*80)

    summary_text = "\n".join(summary_lines)

    # Save summary
    summary_file.write_text(summary_text)
    logger.success(f"Saved summary to: {summary_file}")

    # Print summary
    print("\n" + summary_text)

    logger.success("\n✓ All done!")


if __name__ == "__main__":
    asyncio.run(merge_and_enrich())
