---
name: compilation
description: Compile manuscript, supplementary, and revision documents to PDF.
---

# Compilation

```python
writer = sw.Writer("/path/to/project")

# Main manuscript
result = writer.compile_manuscript()

# Supplementary materials
result = writer.compile_supplementary()

# Revision with tracked changes
result = writer.compile_revision()

# Get section content
content = writer.get_section("introduction")
content = writer.get_section("methods", doc_type="supplementary")

# Get PDF path
pdf = writer.get_pdf("manuscript")
pdf = writer.get_pdf("supplementary")
pdf = writer.get_pdf("revision")
```
