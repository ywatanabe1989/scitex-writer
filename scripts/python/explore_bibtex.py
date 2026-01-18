#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 21:37:02 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/scripts/python/explore_bibtex.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./scripts/python/explore_bibtex.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
BibTeX Explorer - Analyze and filter bibliography using scitex.scholar

Functionalities:
  - Loads BibTeX file with Papers.from_bibtex()
  - Filters by citation count, impact factor, year, keywords
  - Sorts by multiple criteria
  - Compares against currently cited papers in manuscript
  - Identifies high-impact uncited papers
  - Exports filtered results

Dependencies:
  - packages:
    - scitex.scholar
    - argparse
    - pathlib

IO:
  - input-files:
    - BibTeX file (enriched with citation_count, journal_impact_factor)
    - Manuscript .tex files (for cited papers comparison)

  - output-files:
    - Filtered results to stdout or file
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Set

# Import bibtexparser
try:
    import bibtexparser
except ImportError:
    print("Error: bibtexparser is required. Install with: pip install bibtexparser")
    sys.exit(1)


# Simple Paper and Papers classes (lightweight implementation)
class Paper:
    """Lightweight Paper class for BibTeX entries."""

    def __init__(self, **kwargs):
        self.key = kwargs.get("key", "")
        self.title = kwargs.get("title", "")
        self.authors = kwargs.get("authors", [])
        self.year = kwargs.get("year")
        self.journal = kwargs.get("journal")
        self.citation_count = kwargs.get("citation_count")
        self.journal_impact_factor = kwargs.get("journal_impact_factor")
        self.abstract = kwargs.get("abstract", "")
        self.doi = kwargs.get("doi")
        self.keywords = kwargs.get("keywords", [])
        self._original_entry = kwargs.get("_original_entry", {})

    def __repr__(self):
        return f"Paper(key='{self.key}', title='{self.title[:50]}...')"


class Papers:
    """Lightweight Papers collection."""

    def __init__(self, papers: List[Paper]):
        self._papers = papers

    def __len__(self):
        return len(self._papers)

    def __iter__(self):
        return iter(self._papers)

    def __getitem__(self, index):
        return self._papers[index]

    @classmethod
    def from_bibtex(cls, filepath: Path) -> "Papers":
        """Load papers from BibTeX file."""
        with open(filepath, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        papers = []
        for entry in bib_db.entries:
            # Parse fields
            authors = []
            if "author" in entry:
                authors = [a.strip() for a in entry["author"].split(" and ")]

            year = None
            if "year" in entry:
                try:
                    year = int(entry["year"])
                except ValueError:
                    pass

            citation_count = None
            if "citation_count" in entry:
                try:
                    citation_count = int(entry["citation_count"])
                except ValueError:
                    pass

            impact_factor = None
            if "journal_impact_factor" in entry:
                try:
                    impact_factor = float(entry["journal_impact_factor"])
                except ValueError:
                    pass

            keywords = []
            if "keywords" in entry:
                keywords = [k.strip() for k in entry["keywords"].split(",")]

            paper = Paper(
                key=entry.get("ID", ""),
                title=entry.get("title", "").strip("{}"),
                authors=authors,
                year=year,
                journal=entry.get("journal", ""),
                citation_count=citation_count,
                journal_impact_factor=impact_factor,
                abstract=entry.get("abstract", ""),
                doi=entry.get("doi", ""),
                keywords=keywords,
                _original_entry=entry,
            )
            papers.append(paper)

        return cls(papers)

    def filter(self, condition=None, **kwargs) -> "Papers":
        """Filter papers by condition or criteria."""
        if condition and callable(condition):
            filtered = [p for p in self._papers if condition(p)]
            return Papers(filtered)

        # Apply keyword filters
        filtered = self._papers

        # Metrics filters
        if "min_citations" in kwargs and kwargs["min_citations"] is not None:
            filtered = [
                p
                for p in filtered
                if p.citation_count and p.citation_count >= kwargs["min_citations"]
            ]

        if "max_citations" in kwargs and kwargs["max_citations"] is not None:
            filtered = [
                p
                for p in filtered
                if p.citation_count and p.citation_count <= kwargs["max_citations"]
            ]

        if "min_impact_factor" in kwargs and kwargs["min_impact_factor"] is not None:
            filtered = [
                p
                for p in filtered
                if p.journal_impact_factor
                and p.journal_impact_factor >= kwargs["min_impact_factor"]
            ]

        if "max_impact_factor" in kwargs and kwargs["max_impact_factor"] is not None:
            filtered = [
                p
                for p in filtered
                if p.journal_impact_factor
                and p.journal_impact_factor <= kwargs["max_impact_factor"]
            ]

        # Year filter
        if "year_min" in kwargs and kwargs["year_min"] is not None:
            filtered = [p for p in filtered if p.year and p.year >= kwargs["year_min"]]

        if "year_max" in kwargs and kwargs["year_max"] is not None:
            filtered = [p for p in filtered if p.year and p.year <= kwargs["year_max"]]

        # Text filters
        if "keyword" in kwargs and kwargs["keyword"]:
            kw = kwargs["keyword"].lower()
            filtered = [
                p
                for p in filtered
                if (p.title and kw in p.title.lower())
                or (p.abstract and kw in p.abstract.lower())
                or any(kw in k.lower() for k in p.keywords)
            ]

        if "journal" in kwargs and kwargs["journal"]:
            j = kwargs["journal"].lower()
            filtered = [p for p in filtered if p.journal and j in p.journal.lower()]

        if "author" in kwargs and kwargs["author"]:
            a = kwargs["author"].lower()
            filtered = [
                p for p in filtered if any(a in author.lower() for author in p.authors)
            ]

        return Papers(filtered)

    def sort_by(self, key_func, reverse=False) -> "Papers":
        """Sort papers by key function or field name."""
        if isinstance(key_func, str):
            # Handle string field names
            field_name = key_func

            def get_field(paper):
                value = getattr(paper, field_name, None)
                # Handle None values for proper sorting
                if value is None:
                    return float("-inf") if reverse else float("inf")
                return value

            sorted_papers = sorted(self._papers, key=get_field, reverse=reverse)
        else:
            # Handle callable functions
            sorted_papers = sorted(self._papers, key=key_func, reverse=reverse)
        return Papers(sorted_papers)

    def save(self, filepath: Path, format="bibtex"):
        """Save papers to file."""
        if format == "bibtex":
            # Reconstruct BibTeX
            bib_db = bibtexparser.bibdatabase.BibDatabase()
            bib_db.entries = [p._original_entry for p in self._papers]

            with open(filepath, "w", encoding="utf-8") as f:
                bibtexparser.dump(bib_db, f)


def get_cited_papers(manuscript_dir: Path) -> Set[str]:
    """Extract all cited paper keys from manuscript .tex files.

    Args:
        manuscript_dir: Directory containing manuscript .tex files

    Returns:
        Set of cited paper keys
    """
    cited = set()
    tex_files = [
        "abstract.tex",
        "introduction.tex",
        "methods.tex",
        "results.tex",
        "discussion.tex",
    ]

    for fname in tex_files:
        fpath = manuscript_dir / fname
        if fpath.exists():
            content = fpath.read_text()
            matches = re.findall(r"\\cite\{([^}]+)\}", content)
            for match in matches:
                cited.update(key.strip() for key in match.split(","))

    return cited


def extract_coauthors_from_tex(authors_tex_path: Path) -> List[str]:
    """Extract co-author names from authors.tex file.

    Args:
        authors_tex_path: Path to authors.tex file

    Returns:
        List of author names (last names)
    """
    if not authors_tex_path.exists():
        return []

    authors = []
    content = authors_tex_path.read_text()

    # Extract author names from \author[X]{Name} format
    author_pattern = r"\\author\[[^\]]+\]\{([^}]+)\}"
    matches = re.findall(author_pattern, content)

    for match in matches:
        # Remove ALL LaTeX commands and their arguments (handles nested braces)
        clean_name = re.sub(r"\\[a-zA-Z]+(?:\{[^}]*\})?", "", match).strip()
        # Extract last name (assuming format: "First Last" or "First Middle Last")
        parts = clean_name.split()
        if parts:
            last_name = parts[-1]
            authors.append(last_name)

    return authors


def calculate_score(paper: Paper, weights: dict = None) -> float:
    """Calculate composite score for ranking papers.

    Args:
        paper: Paper object
        weights: Dictionary with 'citations' and 'impact_factor' weights

    Returns:
        Composite score
    """
    if weights is None:
        weights = {"citations": 1.0, "impact_factor": 10.0}

    citations = paper.citation_count if paper.citation_count else 0
    impact = paper.journal_impact_factor if paper.journal_impact_factor else 0

    return (citations * weights["citations"]) + (impact * weights["impact_factor"])


def print_papers_table(
    papers: Papers,
    cited_keys: Optional[Set[str]] = None,
    show_score: bool = True,
    max_papers: Optional[int] = None,
):
    """Print papers in formatted table.

    Args:
        papers: Papers collection to display
        cited_keys: Set of already cited paper keys (to mark them)
        show_score: Whether to show composite score
        max_papers: Maximum number of papers to display
    """
    if len(papers) == 0:
        print("No papers match the criteria.")
        return

    # Prepare header
    header_parts = [
        ("Key", 40),
        ("Cites", 7),
        ("IF", 6),
    ]
    if show_score:
        header_parts.append(("Score", 8))
    header_parts.extend([("Year", 6), ("Journal", 25), ("Title", 50)])

    # Print header
    print("=" * 145)
    header = ""
    for name, width in header_parts:
        header += f"{name:<{width}} "
    print(header.rstrip())
    print("-" * 145)

    # Print papers
    count = 0
    for paper in papers:
        if max_papers and count >= max_papers:
            break

        # Check if cited
        is_cited = cited_keys and paper.key in cited_keys
        prefix = "✓ " if is_cited else "  "

        # Format fields
        key = (paper.key[:38] + "..") if len(paper.key) > 40 else paper.key
        cites = str(paper.citation_count) if paper.citation_count else "N/A"
        impact = (
            f"{paper.journal_impact_factor:.1f}"
            if paper.journal_impact_factor
            else "N/A"
        )
        score = f"{calculate_score(paper):.0f}" if show_score else ""
        year = str(paper.year) if paper.year else "N/A"
        journal = (
            (paper.journal[:23] + "..")
            if paper.journal and len(paper.journal) > 25
            else (paper.journal or "N/A")
        )
        title = (
            (paper.title[:48] + "..")
            if paper.title and len(paper.title) > 50
            else (paper.title or "No title")
        )

        # Build row
        row = f"{prefix}{key:<38} {cites:<7} {impact:<6} "
        if show_score:
            row += f"{score:<8} "
        row += f"{year:<6} {journal:<25} {title}"

        print(row)
        count += 1

    print("=" * 145)
    print(f"Showing {count} of {len(papers)} papers")


def print_summary_stats(papers: Papers, cited_keys: Optional[Set[str]] = None):
    """Print summary statistics for the paper collection.

    Args:
        papers: Papers collection
        cited_keys: Set of cited paper keys
    """
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total = len(papers)
    with_citations = len(
        papers.filter(lambda p: p.citation_count is not None and p.citation_count > 0)
    )
    with_impact = len(
        papers.filter(
            lambda p: p.journal_impact_factor is not None
            and p.journal_impact_factor > 0
        )
    )
    with_both = len(
        papers.filter(
            lambda p: p.citation_count is not None
            and p.citation_count > 0
            and p.journal_impact_factor is not None
            and p.journal_impact_factor > 0
        )
    )

    print(f"Total papers: {total}")
    print(
        f"Papers with citation count: {with_citations} ({with_citations / total * 100:.1f}%)"
    )
    print(
        f"Papers with impact factor: {with_impact} ({with_impact / total * 100:.1f}%)"
    )
    print(f"Papers with both metrics: {with_both} ({with_both / total * 100:.1f}%)")

    if cited_keys:
        cited_count = sum(1 for p in papers if p.key in cited_keys)
        uncited_count = total - cited_count
        print(
            f"\nCited in manuscript: {cited_count} ({cited_count / total * 100:.1f}%)"
        )
        print(f"Not yet cited: {uncited_count} ({uncited_count / total * 100:.1f}%)")

    # Citation statistics
    citations = [p.citation_count for p in papers if p.citation_count]
    if citations:
        print("\nCitation count statistics:")
        print(f"  Min: {min(citations)}")
        print(f"  Max: {max(citations)}")
        print(f"  Mean: {sum(citations) / len(citations):.1f}")
        print(f"  Median: {sorted(citations)[len(citations) // 2]}")

    # Impact factor statistics
    impacts = [p.journal_impact_factor for p in papers if p.journal_impact_factor]
    if impacts:
        print("\nImpact factor statistics:")
        print(f"  Min: {min(impacts):.1f}")
        print(f"  Max: {max(impacts):.1f}")
        print(f"  Mean: {sum(impacts) / len(impacts):.1f}")
        print(f"  Median: {sorted(impacts)[len(impacts) // 2]:.1f}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Explore and analyze BibTeX files using scitex.scholar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all papers with metrics
  %(prog)s bibliography.bib

  # Filter high-impact papers (>100 citations, IF>5)
  %(prog)s bibliography.bib --min-citations 100 --min-if 5.0

  # Find uncited high-impact papers
  %(prog)s bibliography.bib --uncited --min-score 100

  # Filter by year and keyword
  %(prog)s bibliography.bib --year-min 2020 --keyword "seizure"

  # Sort by different criteria
  %(prog)s bibliography.bib --sort citation_count --reverse
  %(prog)s bibliography.bib --sort journal_impact_factor --reverse

  # Export filtered results
  %(prog)s bibliography.bib --min-citations 100 --output filtered.bib
        """,
    )

    # Required arguments
    parser.add_argument("bibtex_file", type=Path, help="Path to BibTeX file")

    # Filter arguments
    parser.add_argument("--min-citations", type=int, help="Minimum citation count")
    parser.add_argument("--max-citations", type=int, help="Maximum citation count")
    parser.add_argument("--min-if", type=float, help="Minimum impact factor")
    parser.add_argument("--max-if", type=float, help="Maximum impact factor")
    parser.add_argument("--min-score", type=float, help="Minimum composite score")
    parser.add_argument("--year-min", type=int, help="Minimum publication year")
    parser.add_argument("--year-max", type=int, help="Maximum publication year")
    parser.add_argument(
        "--keyword", type=str, help="Filter by keyword in title/abstract"
    )
    parser.add_argument(
        "--journal", type=str, help="Filter by journal name (partial match)"
    )
    parser.add_argument(
        "--author", type=str, help="Filter by author name (partial match)"
    )
    parser.add_argument(
        "--co-authors",
        action="store_true",
        help="Filter papers by manuscript co-authors from 00_shared/authors.tex",
    )
    parser.add_argument(
        "--authors-tex",
        type=Path,
        default=Path("./00_shared/authors.tex"),
        help="Path to authors.tex file (default: ./00_shared/authors.tex)",
    )

    # Comparison arguments
    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        default=Path("./01_manuscript/contents"),
        help="Directory with manuscript .tex files (default: ./01_manuscript/contents)",
    )
    parser.add_argument(
        "--cited",
        action="store_true",
        help="Show only papers already cited in manuscript",
    )
    parser.add_argument(
        "--uncited",
        action="store_true",
        help="Show only papers NOT cited in manuscript",
    )

    # Sort arguments
    parser.add_argument(
        "--sort",
        type=str,
        choices=[
            "citation_count",
            "journal_impact_factor",
            "year",
            "title",
            "score",
        ],
        default="score",
        help="Sort papers by field (default: score)",
    )
    parser.add_argument(
        "--reverse", action="store_true", help="Sort in descending order"
    )

    # Display arguments
    parser.add_argument("--limit", type=int, help="Maximum number of papers to display")
    parser.add_argument(
        "--no-score", action="store_true", help="Hide composite score column"
    )
    parser.add_argument("--stats", action="store_true", help="Show summary statistics")

    # Output arguments
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Export filtered papers to BibTeX file",
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.bibtex_file.exists():
        print(f"Error: BibTeX file not found: {args.bibtex_file}")
        sys.exit(1)

    if args.cited and args.uncited:
        print("Error: Cannot use --cited and --uncited together")
        sys.exit(1)

    # Load papers
    print(f"Loading papers from {args.bibtex_file}...")
    try:
        papers = Papers.from_bibtex(args.bibtex_file)
        print(f"✓ Loaded {len(papers)} papers\n")
    except Exception as e:
        print(f"Error loading BibTeX file: {e}")
        sys.exit(1)

    # Get cited papers if needed
    cited_keys = None
    if args.cited or args.uncited or args.manuscript_dir.exists():
        if args.manuscript_dir.exists():
            cited_keys = get_cited_papers(args.manuscript_dir)
            print(f"✓ Found {len(cited_keys)} cited papers in manuscript\n")
        else:
            print(f"Warning: Manuscript directory not found: {args.manuscript_dir}\n")

    # Apply filters
    filtered = papers

    # Metrics filters
    if args.min_citations or args.max_citations:
        filtered = filtered.filter(
            min_citations=args.min_citations, max_citations=args.max_citations
        )

    if args.min_if or args.max_if:
        filtered = filtered.filter(
            min_impact_factor=args.min_if, max_impact_factor=args.max_if
        )

    # Score filter (custom)
    if args.min_score:
        filtered = filtered.filter(lambda p: calculate_score(p) >= args.min_score)

    # Year filter
    if args.year_min or args.year_max:
        filtered = filtered.filter(year_min=args.year_min, year_max=args.year_max)

    # Text filters
    if args.keyword:
        filtered = filtered.filter(keyword=args.keyword)

    if args.journal:
        filtered = filtered.filter(journal=args.journal)

    if args.author:
        filtered = filtered.filter(author=args.author)

    # Co-authors filter
    if args.co_authors:
        if args.authors_tex.exists():
            coauthors = extract_coauthors_from_tex(args.authors_tex)
            print(f"✓ Found co-authors: {', '.join(coauthors)}\n")
            # Filter papers where any co-author appears
            filtered = filtered.filter(
                lambda p: any(
                    any(coauthor.lower() in author.lower() for author in p.authors)
                    for coauthor in coauthors
                )
            )
        else:
            print(f"Warning: authors.tex not found at {args.authors_tex}\n")

    # Cited/uncited filter
    if args.cited and cited_keys:
        filtered = filtered.filter(lambda p: p.key in cited_keys)
    elif args.uncited and cited_keys:
        filtered = filtered.filter(lambda p: p.key not in cited_keys)

    print(f"Applied filters: {len(papers)} → {len(filtered)} papers\n")

    # Sort
    if args.sort == "score":
        # Sort by composite score (custom)
        filtered = filtered.sort_by(
            lambda p: calculate_score(p),
            reverse=args.reverse or True,  # Default descending for score
        )
    else:
        filtered = filtered.sort_by(args.sort, reverse=args.reverse)

    # Show statistics
    if args.stats:
        print_summary_stats(filtered, cited_keys)

    # Display results
    print_papers_table(
        filtered,
        cited_keys=cited_keys,
        show_score=not args.no_score,
        max_papers=args.limit,
    )

    # Export if requested
    if args.output:
        filtered.save(args.output, format="bibtex")
        print(f"\n✓ Exported {len(filtered)} papers to {args.output}")


if __name__ == "__main__":
    main()

# EOF
