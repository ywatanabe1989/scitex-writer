#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze enrichment gaps and identify papers needing more work
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "proj/scitex-code/src"))

from scitex.scholar.storage.BibTeXHandler import BibTeXHandler
from scitex.scholar.config import ScholarConfig

def analyze_gaps():
    """Analyze which papers are missing which metadata."""

    bib_file = Path.home() / "proj/scitex-writer/00_shared/bib_files/enriched_all.bib"

    config = ScholarConfig()
    handler = BibTeXHandler(config=config)

    papers = handler.papers_from_bibtex(bib_file)

    print("\n" + "="*80)
    print("METADATA GAP ANALYSIS")
    print("="*80)

    missing_doi = []
    missing_abstract = []
    missing_citations = []
    missing_all = []

    for paper in papers:
        title = paper.metadata.basic.title[:60] if paper.metadata.basic.title else "No title"
        has_doi = bool(paper.metadata.id.doi)
        has_abstract = bool(paper.metadata.basic.abstract)
        has_citations = bool(paper.metadata.citation_count.total)

        if not has_doi:
            missing_doi.append((title, paper))
        if not has_abstract:
            missing_abstract.append((title, paper))
        if not has_citations:
            missing_citations.append((title, paper))

        if not has_doi and not has_abstract and not has_citations:
            missing_all.append((title, paper))

    print(f"\nPapers missing DOI: {len(missing_doi)}/102")
    print("\nTop 10 papers missing DOI:")
    for i, (title, paper) in enumerate(missing_doi[:10], 1):
        year = paper.metadata.basic.year or "?"
        journal = paper.metadata.publication.journal or "?"
        print(f"  {i}. [{year}] {title}")
        print(f"      Journal: {journal}")
        # Check what identifiers we have
        identifiers = []
        if paper.metadata.id.arxiv_id:
            identifiers.append(f"arXiv:{paper.metadata.id.arxiv_id}")
        if paper.metadata.id.corpus_id:
            identifiers.append(f"CorpusID:{paper.metadata.id.corpus_id}")
        if paper.metadata.id.pmid:
            identifiers.append(f"PMID:{paper.metadata.id.pmid}")
        if identifiers:
            print(f"      Has: {', '.join(identifiers)}")
        print()

    print(f"\nPapers missing Abstract: {len(missing_abstract)}/102")
    print("\nTop 5 papers missing Abstract (but have DOI):")
    count = 0
    for title, paper in missing_abstract:
        if paper.metadata.id.doi:
            count += 1
            if count <= 5:
                year = paper.metadata.basic.year or "?"
                print(f"  {count}. [{year}] {title}")
                print(f"      DOI: {paper.metadata.id.doi}")
                print()

    print(f"\nPapers missing ALL metadata (DOI + Abstract + Citations): {len(missing_all)}/102")
    print("\nThese papers need the most help:")
    for i, (title, paper) in enumerate(missing_all[:10], 1):
        year = paper.metadata.basic.year or "?"
        authors = paper.metadata.basic.authors[:2] if paper.metadata.basic.authors else []
        author_str = ", ".join(authors) if authors else "?"
        print(f"  {i}. [{year}] {title}")
        print(f"      Authors: {author_str}")
        print()

    print("="*80)
    print("SUGGESTIONS:")
    print("="*80)
    print(f"1. {len(missing_doi)} papers could benefit from DOI lookup via:")
    print("   - Title + year search on CrossRef")
    print("   - Author + title search")
    print()
    print(f"2. {len([p for t, p in missing_abstract if p.metadata.id.doi])} papers have DOI but no abstract")
    print("   - Re-query these DOIs with force=True")
    print("   - Try PubMed for biomedical papers")
    print()
    print(f"3. {len(missing_all)} papers missing everything")
    print("   - May be unpublished, preprints, or books")
    print("   - Manual inspection recommended")
    print("="*80)

if __name__ == "__main__":
    analyze_gaps()
