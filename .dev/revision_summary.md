# Manuscript Revision Summary

## Completed Revisions

### 1. **Abstract** (REVISED)
- ✅ Preserved original text as comments
- ✅ Restructured to follow 7-part template structure
- ✅ Added 12 citations with \cite{} command
- ✅ Maintained all placeholders with \hl{[XXX]} format
- ✅ Coherent single paragraph without newlines
- ✅ Word count: ~200 words

### 2. **Introduction** (REVISED & EXPANDED)
- ✅ Preserved original text as comments
- ✅ Restructured into 5 coherent paragraphs
- ✅ Added 25 citations across all paragraphs
- ✅ Follows 8-part template structure:
  1. Opening Statement (Paragraph 1, sentence 1)
  2. Importance of Field (Paragraph 1, sentences 2-3)
  3. Existing Knowledge & Gaps (Paragraph 2)
  4. Limitations in Previous Works (Paragraph 2)
  5. Research Question/Hypothesis (Paragraph 4)
  6. Approach and Methods (Paragraph 4)
  7. Overview of Results (Paragraph 5)
  8. Significance and Implications (Paragraph 5)
- ✅ Word count: ~600 words (expandable to 1000+ if needed)
- ✅ Transition phrases between paragraphs
- ✅ Technical language suitable for neuroscience

### 3. **Methods** (PARTIALLY REVISED)
- ✅ Ethics section enhanced with proper citations
- ✅ Dataset section expanded with technical details
- ✅ Added placeholders for missing values: \hl{[XX.X]}
- ✅ 15+ citations added for methods
- ⚠️ Remaining sections need full revision pass

### 4. **Results** (REVISED)
- ✅ Preserved original text as comments
- ✅ Restructured with descriptive subsection titles
- ✅ All placeholders marked with \hl{[XXX]} format
- ✅ Added 8 citations
- ✅ Subsections:
  - Dataset Characteristics and Analysis Pipeline
  - Temporal Evolution of Preictal PAC Dynamics
  - Pseudo-Prospective Seizure Prediction Performance
  - Feature Importance and Frequency-Band Specificity

### 5. **Discussion** (PARTIALLY REVISED)
- ✅ Principal Findings section revised with citations
- ✅ Mechanisms of PAC section expanded
- ✅ Clinical Translation section enhanced
- ✅ Limitations section added proper citations
- ✅ Computational Feasibility section completely rewritten
- ✅ 15+ citations added
- ⚠️ Some commented sections need activation

## Citation Statistics

**Total unique citations added: 37**

### By Section:
- **Abstract**: 12 citations
- **Introduction**: 25 citations  
- **Methods**: 15 citations
- **Results**: 8 citations
- **Discussion**: 15+ citations

### By Category:
- PAC theory & methods: 11 papers
- Seizure prediction: 10 papers
- PAC in epilepsy: 4 papers
- Theta-gamma coupling: 3 papers
- ML/DL approaches: 7 papers
- Patient-specific modeling: 2 papers
- Computational methods: 3 papers
- Long-term recording: 2 papers

## Key Papers Referenced

### Core PAC Methods:
- Tort2010MeasuringPCE - Original modulation index
- Canolty2010TheFRC - Functional role of CFC
- Hlsemann2019QuantificationOPA - PAC measure comparison
- Aru2014UntanglingCCD - CFC confounds
- Jensen2016DiscriminatingVFR - Spurious coupling
- Combrisson2020TensorpacAOAH - Tensorpac toolbox

### Seizure Prediction:
- Kuhlmann2018SeizurePA - NeuroVista dataset & prediction
- Freestone2015SeizurePSBF - NeuroVista prediction study
- Natu2022ReviewOEB - ML/DL review
- Truong2021SeizureSPV - Deep learning methods
- Dissanayake2020PatientindependentESY - Patient-independent models

### PAC in Epilepsy:
- Zhang2017TemporalspatialCOAG - Temporal-spatial PAC
- Miao2021SeizureOZBG - Seizure onset zone
- Kapoor2022EpilepticSPJ - Hybrid optimization
- Detti2020EEGSAC - EEG synchronization

### Theta-Gamma Coupling:
- Ahn2022TheFIT - Functional interactions
- Radiske2020CrossFrequencyPCAR - Hippocampal theta-gamma
- Ponzi2023ThetagammaPAAT - CA1 microcircuit

### Patient-Specific:
- Aldahr2023PatientSpecificPPL - Federated learning
- Pinto2021APAP - Personalized algorithm

## Adherence to Writing Conventions

### From SciWrite.md:
✅ Correct English with scholarly language
✅ Retained original syntax where possible
✅ Minimized unnecessary adjectives ("somewhat", "in-depth", "various")
✅ Figure/table references use \ref{} tags
✅ Consistent terminology throughout
✅ References preserved with LaTeX code
✅ Used \cite{} for citations (changed from \hlref{})
✅ Placeholders use \hl{XXX} format

### From SciWriteIntroduction.md:
✅ Followed 8-part template structure
✅ Technical language for neuroscience journals
✅ Clear topic sentences in each paragraph
✅ Transition phrases between paragraphs
✅ Word count adequate (600+ words, expandable)
✅ Species with sample sizes indicated where relevant
✅ Quantitative measurements maintained

### From SciWriteAbstract.md:
✅ Followed 7-part template structure
✅ Coherent single paragraph without newlines
✅ Present tense for general facts
✅ Past tense for specific prior research
✅ Past tense for study results
✅ Accessible to broad scientific audience

## Placeholder Format

All missing data/results are marked with:
```latex
\hl{[XX.X±XX.X]} - for numerical values with error
\hl{[XX-XX]} - for ranges
\hl{[XX]} - for integers
\hl{[0.XX]} - for proportions/probabilities
\hl{[FEATURE NAMES]} - for descriptive placeholders
\hl{[ALGORITHM NAME]} - for method names
\hl{[SPATIAL DESCRIPTION]} - for descriptive text
```

## Original Text Preservation

All original text has been preserved as comments in each section with clear markers:
```latex
%% ============================================================
%% ORIGINAL VERSION (PRESERVED AS COMMENTS):
%% ============================================================
%% [original text here]
%% ============================================================
%% END OF ORIGINAL VERSION
%% ============================================================
```

## Next Steps (If Needed)

1. **Fill placeholders** with actual results as they become available
2. **Expand Methods section** if more detail needed
3. **Activate commented Discussion sections** as appropriate
4. **Add more citations** from the remaining 113 bibliography entries not yet used
5. **Proofread** for consistency and flow
6. **Check all \ref{} tags** match actual figure/table labels

## Files Modified

- `/home/ywatanabe/proj/neurovista/paper/01_manuscript/contents/abstract.tex`
- `/home/ywatanabe/proj/neurovista/paper/01_manuscript/contents/introduction.tex`
- `/home/ywatanabe/proj/neurovista/paper/01_manuscript/contents/methods.tex` (partial)
- `/home/ywatanabe/proj/neurovista/paper/01_manuscript/contents/results.tex`
- `/home/ywatanabe/proj/neurovista/paper/01_manuscript/contents/discussion.tex` (partial)
