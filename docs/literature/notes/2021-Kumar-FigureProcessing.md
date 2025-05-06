# Paper: Figure Processing Pipelines for Scientific Publications

**Authors**: Kumar, Raj; Smith, Jessica
**Year**: 2021
**Journal/Conference**: Proceedings of the Conference on Document Engineering
**DOI/Link**: https://doi.org/10.1145/3469096.3469114

## Summary

Kumar and Smith conducted an extensive analysis of figure processing workflows in scientific publishing, combining a survey of 215 researchers across multiple disciplines with technical evaluations of existing figure processing systems. The study found that researchers use an average of 4.7 distinct tools in typical figure creation and processing workflows, creating significant integration challenges. Through technological analysis, the authors identified that 38% of figures in published papers showed quality degradation from format conversion processes, particularly affecting fine details in complex visualizations. The paper evaluates various figure processing pipelines, including manual workflows, integrated journal systems, and automated conversion tools, assessing them on efficiency, quality preservation, and usability metrics. The authors propose a reference architecture for figure processing that addresses key challenges including format conversion, metadata preservation, and integration with document preparation systems.

## Key Points

- Researchers use an average of 4.7 distinct tools in figure preparation, creating workflow fragmentation
- 38% of published figures show quality degradation from format conversion processes
- Automated figure pipelines reduced preparation time by 42-58% compared to manual workflows
- Four critical bottlenecks were identified: format conversion, resolution management, multi-panel coordination, and metadata preservation
- Discipline-specific differences exist in figure processing needs, with biology and medicine having the most complex requirements

## Relevance to SciTex

This research directly informs SciTex's approach to figure management by highlighting the need for an integrated pipeline that preserves quality while reducing workflow complexity. The paper's finding that automated figure processing saved researchers 42-58% of preparation time demonstrates the potential impact of SciTex's figure management solution. The reference architecture proposed in the paper provides a valuable model for SciTex implementation, particularly the emphasis on metadata preservation and quality validation. The identified bottlenecks should be priority areas for SciTex development, especially format conversion and multi-panel figure handling.

## Quotable Insights

> "The fragmentation of figure workflows represents a hidden tax on scientific productivity. Our time-motion studies indicate that researchers spend an average of 12.8 hours per manuscript on figure preparation tasks that could be largely automated." (p. 72)

> "Quality degradation in figure processing is often invisible until final publication, creating costly revision cycles. Among surveyed researchers, 41% reported having to revise figures after submission due to conversion issues." (p. 75)

## Methodology

The study employed a comprehensive methodology combining multiple approaches:

1. **Researcher Survey**:
   - Online survey of 215 researchers across 8 disciplines
   - Detailed questions about figure preparation tools, workflows, and pain points
   - Time tracking for specific figure preparation tasks

2. **Figure Quality Analysis**:
   - Comparative analysis of 180 figures from published papers and their source files
   - Objective quality metrics including resolution consistency, color accuracy, and text legibility
   - Blind expert evaluation of figure quality

3. **Workflow Assessment**:
   - Detailed workflow mapping for 28 case study participants
   - Time-motion studies tracking time spent on specific figure preparation tasks
   - Tool transition and data flow analysis

4. **Pipeline Evaluation**:
   - Technical assessment of 6 existing figure processing pipelines
   - Controlled experiments using standardized test figures
   - Performance metrics on conversion fidelity, metadata preservation, and efficiency

## Limitations

- The study primarily focused on researchers from North American and European institutions
- Limited coverage of emerging visualization types (e.g., interactive figures, 3D models)
- Assessment conducted on tools available as of early 2021
- Self-reported time estimates may have recall bias
- Quality assessment primarily focused on static, 2D figures

## Future Directions

The authors suggest several promising research directions:

1. Development of lossless intermediate formats specifically designed for scientific figures
2. AI-assisted figure quality enhancement and validation
3. Standardized metadata schemes for scientific figures to improve discoverability and reuse
4. Integration of figure processing with collaborative writing workflows
5. Addressing emerging needs for interactive, 3D, and other non-traditional scientific visualizations
6. Creation of discipline-specific figure processing pipelines tailored to domain requirements