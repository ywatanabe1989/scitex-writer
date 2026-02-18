#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export/_arxiv_categories.py

"""arXiv category data and suggestion algorithm.

Pure data structures and functions for arXiv subject classification.
No Django or ORM dependencies.
"""

from typing import Dict, List, Tuple

# Common arXiv categories
ARXIV_CATEGORIES: List[Dict[str, str]] = [
    # Computer Science
    {
        "code": "cs.AI",
        "name": "Artificial Intelligence",
        "description": "Covers all areas of AI",
    },
    {
        "code": "cs.CL",
        "name": "Computation and Language",
        "description": "Natural language processing, computational linguistics",
    },
    {
        "code": "cs.CV",
        "name": "Computer Vision and Pattern Recognition",
        "description": "Image processing, computer vision",
    },
    {
        "code": "cs.LG",
        "name": "Machine Learning",
        "description": "Machine learning research",
    },
    {
        "code": "cs.NI",
        "name": "Networking and Internet Architecture",
        "description": "Network protocols, internet architecture",
    },
    {
        "code": "cs.SE",
        "name": "Software Engineering",
        "description": "Software development, engineering practices",
    },
    # Mathematics
    {
        "code": "math.ST",
        "name": "Statistics Theory",
        "description": "Mathematical statistics",
    },
    {"code": "math.PR", "name": "Probability", "description": "Probability theory"},
    {
        "code": "math.NA",
        "name": "Numerical Analysis",
        "description": "Numerical methods and analysis",
    },
    # Physics
    {
        "code": "physics.comp-ph",
        "name": "Computational Physics",
        "description": "Computational methods in physics",
    },
    {
        "code": "physics.data-an",
        "name": "Data Analysis, Statistics and Probability",
        "description": "Data analysis in physics",
    },
    # Quantitative Biology
    {
        "code": "q-bio.BM",
        "name": "Biomolecules",
        "description": "Molecular biology, biochemistry",
    },
    {
        "code": "q-bio.GN",
        "name": "Genomics",
        "description": "Genomics and bioinformatics",
    },
    {
        "code": "q-bio.NC",
        "name": "Neurons and Cognition",
        "description": "Neuroscience, cognition",
    },
    # Statistics
    {"code": "stat.AP", "name": "Applications", "description": "Applied statistics"},
    {
        "code": "stat.ML",
        "name": "Machine Learning",
        "description": "Statistical machine learning",
    },
    # Electrical Engineering
    {
        "code": "eess.SP",
        "name": "Signal Processing",
        "description": "Signal processing, filtering, detection",
    },
]

# Keyword maps for category suggestion
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "cs.AI": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "neural network",
    ],
    "cs.CL": [
        "natural language",
        "nlp",
        "language model",
        "text processing",
        "linguistics",
    ],
    "cs.CV": ["computer vision", "image processing", "object detection", "recognition"],
    "cs.LG": ["machine learning", "learning algorithm", "classification", "regression"],
    "stat.ML": ["statistical learning", "bayesian", "statistics", "probabilistic"],
    "math.ST": ["statistics", "statistical theory", "hypothesis testing"],
    "q-bio.GN": ["genomics", "bioinformatics", "dna", "rna", "genome"],
    "q-bio.NC": ["neuroscience", "brain", "neural", "eeg", "cognition", "hippocampus"],
    "eess.SP": ["signal processing", "filtering", "spectral", "frequency", "wavelet"],
}


def suggest_categories(
    content: str,
    max_suggestions: int = 5,
) -> List[Tuple[str, str, int]]:
    """Suggest arXiv categories based on text content.

    Args:
        content: Text to analyse (typically title + abstract).
        max_suggestions: Maximum number of suggestions to return.

    Returns:
        List of (code, name, score) tuples sorted by relevance score.
    """
    content_lower = content.lower()

    # Build a code -> name lookup from ARXIV_CATEGORIES
    code_to_name = {cat["code"]: cat["name"] for cat in ARXIV_CATEGORIES}

    suggestions: List[Tuple[str, str, int]] = []
    for code, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            name = code_to_name.get(code, code)
            suggestions.append((code, name, score))

    suggestions.sort(key=lambda x: x[2], reverse=True)
    return suggestions[:max_suggestions]


# EOF
