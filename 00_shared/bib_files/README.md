# Bibliography Files

All `.bib` files in this directory are automatically merged and deduplicated into `bibliography.bib` during compilation.

## How It Works

1. Place your `.bib` files here (any name except reserved ones below)
2. During compilation, all `.bib` files are merged into `bibliography.bib`
3. `bibliography.bib` is symlinked into the manuscript contents directory
4. LaTeX uses `bibliography.bib` for citations

## Adding References

Add entries to any `.bib` file. Organize by topic if you like:

```
bib_files/
├── bibliography.bib              # AUTO-GENERATED (merged output)
├── .bibliography_cache.json      # Cache (auto-managed)
├── my_papers.bib                 # Your own publications
├── related_work.bib              # Related work references
├── methods_refs.bib              # Methodology references
└── README.md
```

## Reserved Filenames

These are managed by the system -- do not edit manually:

- `bibliography.bib` - merged output (overwritten each compilation)
- `.bibliography_cache.json` - deduplication cache

## Example Entry

```bibtex
@article{smith_neural_2023,
  author  = {Smith, John and Doe, Jane},
  title   = {Neural Network Analysis of EEG Signals},
  journal = {Journal of Neuroscience Methods},
  year    = {2023},
  volume  = {400},
  pages   = {1--15},
  doi     = {10.1016/j.jneumeth.2023.001},
}
```

## Citing in Manuscript

```latex
Previous work \cite{smith_neural_2023} demonstrated...
```

## Validation

Run `make check` to verify bibliography files exist before compilation.

<!-- EOF -->
