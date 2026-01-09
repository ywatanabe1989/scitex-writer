#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Second-pass aggressive enrichment for papers with missing metadata
Focuses on the 49 papers missing DOIs and 11 with DOI but no abstract
"""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / "proj/scitex-code/src"))

from scitex import logging
from scitex.scholar.storage.BibTeXHandler import BibTeXHandler
from scitex.scholar.pipelines.ScholarPipelineMetadataSingle import ScholarPipelineMetadataSingle
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def second_pass_enrichment():
    """Second pass: aggressive enrichment for gaps."""

    bib_file = Path.home() / "proj/scitex-writer/00_shared/bib_files/enriched_all.bib"
    output_file = Path.home() / "proj/scitex-writer/00_shared/bib_files/enriched_all_v2.bib"

    config = ScholarConfig()
    handler = BibTeXHandler(config=config)
    enricher = ScholarPipelineMetadataSingle(config=config)

    # Load current enriched papers
    papers = handler.papers_from_bibtex(bib_file)

    logger.info(f"Loaded {len(papers)} papers for second-pass enrichment")

    # Identify papers needing work
    needs_doi = []
    needs_abstract = []

    for paper in papers:
        has_doi = bool(paper.metadata.id.doi)
        has_abstract = bool(paper.metadata.basic.abstract)

        if not has_doi:
            needs_doi.append(paper)
        elif not has_abstract:
            needs_abstract.append(paper)

    logger.info(f"Papers needing DOI: {len(needs_doi)}")
    logger.info(f"Papers with DOI but no abstract: {len(needs_abstract)}")

    print("\n" + "="*80)
    print("SECOND-PASS ENRICHMENT")
    print("="*80)
    print(f"Target 1: {len(needs_doi)} papers missing DOI")
    print(f"Target 2: {len(needs_abstract)} papers with DOI but no abstract")
    print("="*80)

    enriched_papers = papers.copy()
    stats = {
        'doi_found': 0,
        'abstract_found': 0,
        'citations_added': 0,
        'total_improved': 0
    }

    # Phase 1: Focus on papers with DOI but no abstract (easier wins)
    print("\n" + "="*80)
    print("PHASE 1: Re-querying papers with DOI but missing abstract")
    print("="*80)

    for i, paper in enumerate(needs_abstract, 1):
        title = paper.metadata.basic.title[:60] if paper.metadata.basic.title else "No title"
        doi = paper.metadata.id.doi

        print(f"\n[{i}/{len(needs_abstract)}] {title}")
        print(f"  DOI: {doi}")

        try:
            # Force re-enrichment with the DOI
            enriched = await enricher.enrich_paper_async(paper, force=True)

            # Check what we gained
            got_abstract = enriched.metadata.basic.abstract and not paper.metadata.basic.abstract
            got_citations = enriched.metadata.citation_count.total and not paper.metadata.citation_count.total

            if got_abstract:
                stats['abstract_found'] += 1
                stats['total_improved'] += 1
                logger.success(f"  ✓ Found abstract! ({len(enriched.metadata.basic.abstract)} chars)")

            if got_citations:
                stats['citations_added'] += 1
                logger.success(f"  ✓ Found citations! ({enriched.metadata.citation_count.total})")

            if got_abstract or got_citations:
                # Update in our list
                idx = papers.index(paper)
                enriched_papers[idx] = enriched
            else:
                logger.info(f"  - No new metadata found")

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")

        await asyncio.sleep(0.5)

    # Phase 2: Try to find DOIs for papers without them
    print("\n" + "="*80)
    print("PHASE 2: Finding DOIs via title+author search")
    print("="*80)
    print(f"Attempting to find DOIs for {min(20, len(needs_doi))} papers...")
    print("(limiting to 20 to avoid rate limits)")
    print("="*80)

    for i, paper in enumerate(needs_doi[:20], 1):
        title = paper.metadata.basic.title[:60] if paper.metadata.basic.title else "No title"
        year = paper.metadata.basic.year
        authors = paper.metadata.basic.authors[:2] if paper.metadata.basic.authors else []

        print(f"\n[{i}/20] {title}")
        if year:
            print(f"  Year: {year}")
        if authors:
            print(f"  Authors: {', '.join(authors)}")

        try:
            # Try enrichment with title (will use title search)
            enriched = await enricher.enrich_paper_async(paper, force=True)

            # Check what we gained
            got_doi = enriched.metadata.id.doi and not paper.metadata.id.doi
            got_abstract = enriched.metadata.basic.abstract and not paper.metadata.basic.abstract
            got_citations = enriched.metadata.citation_count.total and not paper.metadata.citation_count.total

            if got_doi:
                stats['doi_found'] += 1
                stats['total_improved'] += 1
                logger.success(f"  ✓ Found DOI: {enriched.metadata.id.doi}")

            if got_abstract:
                stats['abstract_found'] += 1
                logger.success(f"  ✓ Found abstract! ({len(enriched.metadata.basic.abstract)} chars)")

            if got_citations:
                stats['citations_added'] += 1
                logger.success(f"  ✓ Found citations! ({enriched.metadata.citation_count.total})")

            if got_doi or got_abstract or got_citations:
                # Update in our list
                idx = papers.index(paper)
                enriched_papers[idx] = enriched
            else:
                logger.info(f"  - No new metadata found")

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")

        await asyncio.sleep(1.0)  # Longer delay for title searches

    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)

    from scitex.scholar.core.Papers import Papers
    enriched_collection = Papers(enriched_papers, project="scitex-writer")

    handler.papers_to_bibtex(enriched_collection, output_path=output_file)

    # Calculate final stats
    final_doi_count = sum(1 for p in enriched_papers if p.metadata.id.doi)
    final_abstract_count = sum(1 for p in enriched_papers if p.metadata.basic.abstract)
    final_citation_count = sum(1 for p in enriched_papers if p.metadata.citation_count.total)

    print("\n" + "="*80)
    print("SECOND-PASS ENRICHMENT RESULTS")
    print("="*80)
    print(f"\nNew metadata found:")
    print(f"  DOIs: +{stats['doi_found']} (now {final_doi_count}/102 = {100*final_doi_count/102:.1f}%)")
    print(f"  Abstracts: +{stats['abstract_found']} (now {final_abstract_count}/102 = {100*final_abstract_count/102:.1f}%)")
    print(f"  Citations: +{stats['citations_added']} (now {final_citation_count}/102 = {100*final_citation_count/102:.1f}%)")
    print(f"\nTotal papers improved: {stats['total_improved']}")
    print(f"\nSaved to: {output_file}")
    print("="*80)

    # Create improvement summary
    summary_file = Path.home() / "proj/scitex-writer/00_shared/bib_files/enrichment_v2_summary.txt"
    summary_lines = []
    summary_lines.append("="*80)
    summary_lines.append("SECOND-PASS ENRICHMENT SUMMARY")
    summary_lines.append("="*80)
    summary_lines.append("")
    summary_lines.append("IMPROVEMENTS:")
    summary_lines.append(f"  New DOIs found: {stats['doi_found']}")
    summary_lines.append(f"  New abstracts found: {stats['abstract_found']}")
    summary_lines.append(f"  New citations found: {stats['citations_added']}")
    summary_lines.append(f"  Total papers improved: {stats['total_improved']}")
    summary_lines.append("")
    summary_lines.append("FINAL COVERAGE:")
    summary_lines.append(f"  Papers with DOI: {final_doi_count}/102 ({100*final_doi_count/102:.1f}%)")
    summary_lines.append(f"  Papers with Abstract: {final_abstract_count}/102 ({100*final_abstract_count/102:.1f}%)")
    summary_lines.append(f"  Papers with Citations: {final_citation_count}/102 ({100*final_citation_count/102:.1f}%)")
    summary_lines.append("="*80)

    summary_file.write_text("\n".join(summary_lines))

    print(f"\nSummary saved to: {summary_file}")
    logger.success("\n✓ Second-pass enrichment complete!")


if __name__ == "__main__":
    asyncio.run(second_pass_enrichment())
