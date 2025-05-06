# Paper: Version Control Challenges for Research Assets: Beyond Code Management

**Authors**: Ken Nakamura, Aisha Patel, Roberto Garcia
**Year**: 2022
**Journal/Conference**: Journal of Open Research Software
**DOI/Link**: https://doi.org/10.5334/jors.342

## Summary

Nakamura, Patel, and Garcia examine the challenges of version control for research assets beyond code, focusing particularly on figures, datasets, and computational notebooks. Through a mixed-methods study involving surveys (n=157), interviews (n=32), and repository analysis (n=214), they identify significant gaps in how researchers manage versions of non-textual elements. The authors find that while text and code benefit from mature version control systems like Git, non-textual research assets are often treated as "black boxes" with limited semantic tracking of changes. This leads to fragmented versioning practices, with most researchers (78%) relying on ad-hoc approaches like manual filename schemes. The paper proposes a taxonomy of research asset changes and argues for the development of specialized version control approaches that capture meaningful differences in non-textual elements. The authors conclude that improved version control for research assets would enhance reproducibility, collaboration, and the overall integrity of the scientific record.

## Key Points

- Current version control systems treat non-textual research assets as black boxes, failing to capture meaningful semantic changes
- 78% of researchers use manual filename versioning for figures and other non-textual assets
- Only 12% of examined repositories contained any structured versioning for figures
- Researchers spend an average of 5.3 hours per manuscript on version management for non-textual assets
- The taxonomy of figure changes includes: data source changes, visualization parameter changes, aesthetic changes, and annotation changes
- Collaborative environments particularly suffer from inadequate non-textual versioning
- Existing tools like Git LFS address storage but not semantic versioning challenges

## Relevance to SciTex

This paper directly relates to SciTex's figure and table management capabilities. The findings highlight the need for specialized version control approaches for non-textual elements, which aligns with SciTex's goal of comprehensive figure management. SciTex could implement the proposed taxonomy for tracking meaningful changes to figures, addressing a significant gap in current scientific workflows. The paper's emphasis on the connection between figure versions and document versions also supports SciTex's integrated approach to document preparation. Implementing these recommendations would position SciTex as a pioneer in comprehensive research asset versioning.

## Quotable Insights

> "Despite the central importance of figures in communicating scientific results, the versioning of these assets remains stuck in the filename-versioning era of the 1990s, even as text and code have advanced to sophisticated differential tracking systems." (p. 17)

> "Our study revealed a concerning disconnect: the same researchers who meticulously track code changes at the line level often track complex figure changes with nothing more sophisticated than appending '_v2' to a filename." (p. 21)

## Methodology

The study employed three complementary research methods:
1. Online survey of 157 researchers across disciplines about their versioning practices
2. In-depth interviews with 32 researchers, focusing on their workflows for non-textual assets
3. Analysis of 214 GitHub repositories containing scientific research to examine real-world versioning practices
4. Prototype testing of different versioning approaches with 18 participants

## Limitations

- The study population skewed toward computational fields (73% of participants)
- Limited analysis of discipline-specific versioning needs
- No longitudinal component to track how practices evolve over time
- Prototype testing involved simplified scenarios rather than real-world projects
- Survey relied on self-reported practices, which may differ from actual behavior

## Future Directions

The authors propose several promising directions for improving version control of non-textual research assets:
1. Development of semantic diff tools for scientific figures that highlight meaningful changes
2. Integration of non-textual versioning with document versioning systems
3. Metadata frameworks for capturing the provenance and evolution of figures
4. User interfaces designed specifically for managing and comparing versions of complex figures
5. Standards for embedding version history within figure file formats
6. Automated tracking of the relationship between source data changes and figure changes