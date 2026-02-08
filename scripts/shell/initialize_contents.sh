#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-09
# File: scripts/shell/initialize_contents.sh
# Purpose: Reset all content files to clean template placeholders

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Document filter (optional argument: manuscript, supplementary, revision, shared)
DOC_FILTER="${1:-}"

echo -e "${YELLOW}=== SciTeX Writer: Initialize Contents ===${NC}"
echo ""
if [ -n "$DOC_FILTER" ]; then
    echo "This will RESET ${DOC_FILTER} content files to clean template placeholders."
else
    echo "This will RESET all content files to clean template placeholders."
    echo "The following will be overwritten:"
    echo "  - 00_shared/    (title, authors, keywords, journal, bibliography)"
    echo "  - 01_manuscript/ (abstract, introduction, methods, results, discussion, ...)"
    echo "  - 02_supplementary/ (methods, results, figure/table captions)"
    echo "  - 03_revision/  (introduction, conclusion, editor/reviewer responses)"
fi
echo ""

# Safety: create snapshot before destructive operation
cd "$PROJECT_ROOT"
if git rev-parse --is-inside-work-tree &>/dev/null; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    SNAPSHOT_TAG="snapshot/pre-init-${TIMESTAMP}"

    # Stage and commit everything (including untracked content files)
    if git status --porcelain 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}Uncommitted changes detected. Creating snapshot...${NC}"
        git add -A
        git commit -m "snapshot: pre-init ${TIMESTAMP}" --no-verify --quiet
        echo -e "${GREEN}Snapshot committed.${NC}"
    fi

    # Tag current state
    git tag "$SNAPSHOT_TAG"
    echo -e "${GREEN}Snapshot tagged: ${SNAPSHOT_TAG}${NC}"
    echo "  To revert: make revert ID=${SNAPSHOT_TAG}"
    echo ""
else
    echo -e "${YELLOW}Not a git repository. No snapshot created.${NC}"
    echo ""
fi

read -rp "Are you sure you want to proceed? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}Initializing contents...${NC}"

# Helper: check if section should run
should_run() {
    [ -z "$DOC_FILTER" ] || [ "$DOC_FILTER" = "$1" ]
}

# ============================================================================
# 00_shared/ — Metadata
# ============================================================================
if should_run "shared" || [ -z "$DOC_FILTER" ]; then
echo "  Resetting shared metadata..."

cat >"$PROJECT_ROOT/00_shared/title.tex" <<'LATEX'
%% -*- coding: utf-8 -*-
\title{
Your Manuscript Title Here
}

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/00_shared/authors.tex" <<'LATEX'
%% -*- coding: utf-8 -*-
\author[1]{First Author\corref{cor1}}
\author[2]{Second Author}
\author[3]{Third Author}

\address[1]{First Institution, Department, City, Country}
\address[2]{Second Institution, Department, City, Country}
\address[3]{Third Institution, Department, City, Country}

\cortext[cor1]{Corresponding author. Email: your.email@institution.edu}

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/00_shared/keywords.tex" <<'LATEX'
% \pdfbookmark[1]{Keywords}{keywords}
\begin{keyword}
keyword one \sep keyword two \sep keyword three \sep keyword four \sep keyword five
\end{keyword}
LATEX

cat >"$PROJECT_ROOT/00_shared/journal_name.tex" <<'LATEX'
\journal{Journal Name Here}
LATEX

# Bibliography: single example entry
cat >"$PROJECT_ROOT/00_shared/bib_files/bibliography.bib" <<'BIBTEX'
@article{example_reference_2020,
  author  = {Author, First and Author, Second},
  title   = {Example Article Title},
  journal = {Journal Name},
  year    = {2020},
  volume  = {1},
  pages   = {1--10},
  doi     = {10.1234/example.2020},
}

@article{example_method_2019,
  author  = {Method, First and Method, Second},
  title   = {Example Method Reference},
  journal = {Methods Journal},
  year    = {2019},
  volume  = {5},
  pages   = {100--115},
  doi     = {10.1234/method.2019},
}
BIBTEX

# Remove agent-generated and merged/enriched bib files
rm -f "$PROJECT_ROOT/00_shared/bib_files/by_claude.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/by_gemini.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/by_gpt5.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/by_grok.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/field_background.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/methods_refs.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/my_papers.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/related_work.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/scitex-system.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/merged_all.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/enriched_all.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/enriched_all.bib"
rm -f "$PROJECT_ROOT/00_shared/bib_files/enriched_all_v2.bib"

# ============================================================================
# 01_manuscript/ — Main Manuscript
# ============================================================================
echo "  [2/6] Resetting manuscript contents..."

cat >"$PROJECT_ROOT/01_manuscript/contents/abstract.tex" <<'LATEX'
%% -*- coding: utf-8 -*-
\begin{abstract}
  \pdfbookmark[1]{Abstract}{abstract}

Replace this text with your manuscript abstract. Typically 150--250 words summarizing objectives, methods, key findings, and conclusions.

\end{abstract}

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/introduction.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section{Introduction}

Replace this with your introduction. Establish context, review relevant work \cite{example_reference_2020}, identify gaps, and state your objectives.

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/methods.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section{Methods}

Replace this with your methods. Describe study design, data collection, and analysis procedures \cite{example_method_2019}. Provide enough detail for reproducibility.

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/results.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section{Results}

Replace this with your results. Present findings with references to figures (Figure~\ref{fig:01_example_figure}) and tables (Table~\ref{tab:01_example_table}).

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/discussion.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section{Discussion}

Replace this with your discussion. Interpret findings, compare with previous work, discuss limitations, and state conclusions.

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/highlights.tex" <<'LATEX'
%% -*- coding: utf-8 -*-
%% \begin{highlights}
%% \pdfbookmark[1]{Highlights}{highlights}

%% \item Highlight \#1

%% \item Highlight \#2

%% \item Highlight \#3

%% \end{highlights}

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/graphical_abstract.tex" <<'LATEX'
%%Graphical abstract
%\pdfbookmark[1]{Graphical Abstract}{graphicalabstract}
%\begin{graphicalabstract}
%\includegraphics{grabs}
%\end{graphicalabstract}
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/data_availability.tex" <<'LATEX'
%% -*- coding: utf-8 -*-
\pdfbookmark[1]{Data Availability Statement}{data_availability}

\section*{Data Availability Statement}

The data and code that support the findings of this study are available from the corresponding author upon reasonable request.

\label{data and code availability}

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/additional_info.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\pdfbookmark[1]{Additional Information}{additional_information}

\pdfbookmark[2]{Ethics Declarations}{ethics_declarations}
\section*{Ethics Declarations}
Replace with your ethics statement.
\label{ethics declarations}

\pdfbookmark[2]{Contributors}{author_contributions}
\section*{Author Contributions}
Replace with author contributions.
\label{author contributions}

\pdfbookmark[2]{Acknowledgments}{acknowledgments}
\section*{Acknowledgments}
Replace with acknowledgments.
\label{acknowledgments}

\pdfbookmark[2]{Declaration of Interests}{declaration_of_interest}
\section*{Declaration of Interests}
The authors declare that they have no competing interests.
\label{declaration of interests}

\pdfbookmark[2]{Declaration of Generative AI in Scientific Writing}{declaration_of_generative_ai}
\section*{Declaration of Generative AI in Scientific Writing}
Disclose any use of generative AI tools here.
\label{declaration of generative ai in scientific writing}

%%%% EOF
LATEX

# Figure caption — fix label to match filename convention
cat >"$PROJECT_ROOT/01_manuscript/contents/figures/caption_and_media/01_example_figure.tex" <<'LATEX'
%% Example figure caption
\caption{Replace with your figure caption.}
\label{fig:01_example_figure}
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/figures/caption_and_media/02_another_example.tex" <<'LATEX'
%% Example figure caption
\caption{Replace with your figure caption.}
\label{fig:02_another_example}
LATEX

# Table caption — fix label to match filename convention
cat >"$PROJECT_ROOT/01_manuscript/contents/tables/caption_and_media/01_example_table.tex" <<'LATEX'
%% Example table caption
\caption{Replace with your table caption.}
\label{tab:01_example_table}
LATEX

cat >"$PROJECT_ROOT/01_manuscript/contents/tables/caption_and_media/01_example_table.csv" <<'CSV'
Category,Value,Description
Example A,1.00,Replace with your data
Example B,2.00,Replace with your data
Example C,3.00,Replace with your data
CSV

# Clean compiled figure/table outputs
rm -f "$PROJECT_ROOT/01_manuscript/contents/figures/caption_and_media/jpg_for_compilation/"[0-9]*.jpg
rm -f "$PROJECT_ROOT/01_manuscript/contents/figures/compiled/"[0-9]*.tex
rm -f "$PROJECT_ROOT/01_manuscript/contents/tables/compiled/"[0-9]*.tex

# ============================================================================
# 02_supplementary/ — Supplementary Materials
# ============================================================================
echo "  [3/6] Resetting supplementary contents..."

cat >"$PROJECT_ROOT/02_supplementary/contents/methods.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section*{Supplementary Methods}

Replace this with supplementary methods that provide additional detail beyond the main manuscript.

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/02_supplementary/contents/results.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\section*{Supplementary Results}

Replace this with supplementary results and additional analyses.

%%%% EOF
LATEX

# Fix supplementary naming: S1_ -> 01_ (required by preprocessing)
SUPPL_FIG_DIR="$PROJECT_ROOT/02_supplementary/contents/figures/caption_and_media"
if [ -f "$SUPPL_FIG_DIR/S1_example_supplementary_figure.tex" ]; then
    mv "$SUPPL_FIG_DIR/S1_example_supplementary_figure.tex" \
        "$SUPPL_FIG_DIR/01_example_supplementary_figure.tex"
fi
cat >"$SUPPL_FIG_DIR/01_example_supplementary_figure.tex" <<'LATEX'
%% Supplementary figure caption
\caption{Replace with your supplementary figure caption.}
\label{fig:01_example_supplementary_figure}
LATEX

SUPPL_TBL_DIR="$PROJECT_ROOT/02_supplementary/contents/tables/caption_and_media"
# Remove SciTeX-specific data tables
rm -f "$SUPPL_TBL_DIR/01_compilation_options.csv"
rm -f "$SUPPL_TBL_DIR/01_compilation_options.tex"
rm -f "$SUPPL_TBL_DIR/02_compilation_engines.csv"
rm -f "$SUPPL_TBL_DIR/03_yaml_configuration.csv"
rm -f "$SUPPL_TBL_DIR/04_supported_formats.csv"
rm -f "$SUPPL_TBL_DIR/05_citation_styles.csv"
rm -f "$SUPPL_TBL_DIR/05_citation_styles.tex"
if [ -f "$SUPPL_TBL_DIR/S1_example_supplementary_table.tex" ]; then
    mv "$SUPPL_TBL_DIR/S1_example_supplementary_table.tex" \
        "$SUPPL_TBL_DIR/01_example_supplementary_table.tex"
fi
cat >"$SUPPL_TBL_DIR/01_example_supplementary_table.tex" <<'LATEX'
%% Supplementary table caption
\caption{Replace with your supplementary table caption.}
\label{tab:01_example_supplementary_table}
LATEX

cat >"$SUPPL_TBL_DIR/01_example_supplementary_table.csv" <<'CSV'
Parameter,Value,Unit
Example parameter A,1.00,ms
Example parameter B,2.00,Hz
Example parameter C,3.00,mV
CSV

# Clean compiled supplementary outputs
rm -f "$PROJECT_ROOT/02_supplementary/contents/figures/caption_and_media/jpg_for_compilation/"[0-9]*.jpg
rm -f "$PROJECT_ROOT/02_supplementary/contents/figures/compiled/"[0-9]*.tex
rm -f "$PROJECT_ROOT/02_supplementary/contents/tables/compiled/"[0-9]*.tex

# ============================================================================
# 03_revision/ — Revision Responses
# ============================================================================
echo "  [4/6] Resetting revision contents..."

cat >"$PROJECT_ROOT/03_revision/contents/introduction.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\noindent\hrulefill
\pdfbookmark[1]{Introduction}{introduction}

\section*{Introduction}

We thank the Editor and Reviewers for their constructive feedback. We have carefully addressed each point raised during the review process.

\editorText{Original comments are presented in gray italicized text.}

\authorText{Our responses are shown in blue text.}

Changes made to the manuscript are highlighted using latexdiff formatting, with \DIFadd{additions shown in blue} and \DIFdel{deletions shown in red with strikethrough}.

%%%% EOF
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/conclusion.tex" <<'LATEX'
%% -*- coding: utf-8 -*-

\noindent\hrulefill

\section*{Conclusion}

We appreciate the time and expertise devoted to evaluating our manuscript. All concerns raised have been addressed. We look forward to your decision.

Sincerely,

The Authors

%%%% EOF
LATEX

# Editor comments/responses
cat >"$PROJECT_ROOT/03_revision/contents/editor/E_01_comments.tex" <<'LATEX'
%% Editor comment 1
\subsection*{Editor Comment 1}

\editorText{Replace with editor comment.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/editor/E_01_response.tex" <<'LATEX'
%% Response to editor comment 1
\subsection*{Response to Editor Comment 1}

\authorText{Replace with your response.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/editor/E_01_revision.tex" <<'LATEX'
%% Revision for editor comment 1
%% Describe specific manuscript changes here
LATEX

# Reviewer 1 comments/responses
cat >"$PROJECT_ROOT/03_revision/contents/reviewer1/R1_01_comments.tex" <<'LATEX'
%% Reviewer 1 comment 1
\subsection*{Reviewer 1, Comment 1}

\editorText{Replace with reviewer comment.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/reviewer1/R1_01_response.tex" <<'LATEX'
%% Response to reviewer 1 comment 1
\subsection*{Response to Reviewer 1, Comment 1}

\authorText{Replace with your response.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/reviewer1/R1_01_revision.tex" <<'LATEX'
%% Revision for reviewer 1 comment 1
%% Describe specific manuscript changes here
LATEX

# Reviewer 2 comments/responses
cat >"$PROJECT_ROOT/03_revision/contents/reviewer2/R2_01_comments.tex" <<'LATEX'
%% Reviewer 2 comment 1
\subsection*{Reviewer 2, Comment 1}

\editorText{Replace with reviewer comment.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/reviewer2/R2_01_response.tex" <<'LATEX'
%% Response to reviewer 2 comment 1
\subsection*{Response to Reviewer 2, Comment 1}

\authorText{Replace with your response.}
LATEX

cat >"$PROJECT_ROOT/03_revision/contents/reviewer2/R2_01_revision.tex" <<'LATEX'
%% Revision for reviewer 2 comment 1
%% Describe specific manuscript changes here
LATEX

# Clean compiled revision outputs
rm -f "$PROJECT_ROOT/03_revision/contents/figures/compiled/"[0-9]*.tex
rm -f "$PROJECT_ROOT/03_revision/contents/tables/compiled/"[0-9]*.tex

# ============================================================================
# Clean generated PDFs and diffs
# ============================================================================
echo "  [5/6] Cleaning compiled outputs..."

rm -f "$PROJECT_ROOT/01_manuscript/manuscript.pdf"
rm -f "$PROJECT_ROOT/01_manuscript/manuscript_diff.pdf"
rm -f "$PROJECT_ROOT/02_supplementary/supplementary.pdf"
rm -f "$PROJECT_ROOT/02_supplementary/supplementary_diff.pdf"
rm -f "$PROJECT_ROOT/03_revision/revision.pdf"

# ============================================================================
# Summary
# ============================================================================
echo "  [6/6] Done."
echo ""
echo -e "${GREEN}=== Contents initialized to clean template ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit 00_shared/title.tex, authors.tex, keywords.tex"
echo "  2. Write your manuscript in 01_manuscript/contents/"
echo "  3. Add figures to 01_manuscript/contents/figures/caption_and_media/"
echo "  4. Add tables to 01_manuscript/contents/tables/caption_and_media/"
echo "  5. Add references to 00_shared/bib_files/bibliography.bib"
echo "  6. Run: make manuscript"

###% EOF
