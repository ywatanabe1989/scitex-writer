<!-- ---
!-- Timestamp: 2025-09-28 18:42:06
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/scripts/shell/modules/README.md
!-- --- -->

## Figure conversion cascade

process_conversion()
1. Supported formats: pptx, tif/tiff, mmd, png, jpeg/jpg
2. When pptx located, try to convert to tif
3. When cropping option enabled, try to crop tif
4. When tif/tiff located, try to convert to png
5. When mmd located, try to convert to png
6. When png located, try to convert to jpg

## Table handling
Based on your system, you could also use:
  - pandoc with CSV reader for even more formats
  - csvkit for advanced CSV manipulation
  - tabulate Python library for prettier table formatting

<!-- EOF -->