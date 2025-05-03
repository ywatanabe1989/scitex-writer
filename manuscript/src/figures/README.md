# Figure Management

This directory contains all figure-related files for the manuscript.

## Directory Structure

- `compiled/`: Contains compiled .tex files for each figure.
- `src/`: Source directory for figure files.
  - Place .tex (legend-dedicated files) and .tif files here.
  - `jpg/`: Contains JPEG versions of figures.
- `templates/`: Templates for figure creation.
- `workspace/`: Working directory for figure development.

## Usage

1. Prepare .tex (legend-dedicated files) and .tif files in the `src` directory.
2. The compilation process will generate necessary files in the `compiled` directory.
3. JPEG versions of figures will be automatically created in `src/jpg/`.

## Note

Symlinks in the `src` directory point to files in the `workspace` subdirectories.

For any changes or additions to figures, work in the appropriate `workspace` subdirectory and update the files in `src` accordingly.

## Example Structure

```
.
├── compiled
│   ├── Figure_ID_01.tex
│   ├── Figure_ID_02.tex
│   ├── Figure_ID_03.tex
│   ├── Figure_ID_04.tex
│   ├── Figure_ID_05.tex
│   ├── Figure_ID_rank_dist.tex
│   └── Figure_ID_svc.tex
├── README.md
├── src
│   ├── Figure_ID_01.tex
│   ├── Figure_ID_01.tif
│   ├── Figure_ID_02.tex
│   ├── Figure_ID_02.tif
│   ├── Figure_ID_03.tex
│   ├── Figure_ID_03.tif
│   ├── Figure_ID_04.tex
│   ├── Figure_ID_04.tif
│   ├── Figure_ID_05.tex
│   ├── Figure_ID_05.tif
│   ├── Figure_ID_rank_dist.pptx -> ../workspace/08_rank_dist_KDE/Figure_08.pptx
│   ├── Figure_ID_rank_dist.tex
│   ├── Figure_ID_rank_dist.tif -> ../workspace/08_rank_dist_KDE/Figure_08.tif
│   ├── Figure_ID_svc.tex
│   ├── Figure_ID_svc.tif -> ../workspace/09_SVC/Figure_ID_svc.tif
│   └── jpg
│       ├── Figure_ID_01.jpg
│       ├── Figure_ID_02.jpg
│       ├── Figure_ID_03.jpg
│       ├── Figure_ID_04.jpg
│       ├── Figure_ID_05.jpg
│       ├── _Figure_ID_07.jpg
│       ├── Figure_ID_07.jpg
│       ├── Figure_ID_rank_dist.jpg
│       └── Figure_ID_svc.jpg
├── templates
│   ├── z_Figure_XX.jnt
│   └── z_Figure_XX.pptx
└── workspace
    ├── 01
    │   ├── ABC
    │   ├── DEF
    │   ├── Figure_01.pptx
    │   ├── Figure_01.tif
    │   ├── Figure_ID_01.pptx
    │   └── old
    ├── 02
    │   ├── A
    │   ├── _B
    │   ├── B
    │   ├── C
    │   ├── DE
    │   ├── Figure_02.pptx
    │   ├── Figure_02.tif
    │   ├── Figure_ID_02.pptx
    │   └── old
    ├── 03
    │   ├── AB
    │   ├── C
    │   ├── D
    │   ├── Figure_03.pptx
    │   ├── Figure_03.tif
    │   ├── Figure_ID_03.pptx
    │   ├── linear_regression_corr_100.tif
    │   ├── medians.xlsx
    │   └── old
    ├── 04
    │   ├── ACE
    │   ├── D
    │   ├── Figure_04.pptx
    │   ├── Figure_04.tif
    │   ├── Figure_ID_04.pptx
    │   └── old
    ├── 05
    │   ├── box
    │   ├── Figure_05A.JNB
    │   ├── Figure_05.pptx
    │   ├── Figure_05.tif
    │   ├── Figure_ID_05.pptx
    │   ├── line
    │   ├── old
    │   ├── _peri_SWR_dist_from_P_old_range_of_pre, mid, and post SWR.csv
    │   ├── _peri_SWR_dist_from_P_old_range_of_pre, mid, and post SWR.csv:com.dropbox.attrs
    │   └── _peri_SWR_dist_from_P_old_range_of_pre, mid, and post SWR.csv:Zone.Identifier
    ├── 06
    │   ├── Figure_06.JNB
    │   ├── Figure_06.pptx
    │   ├── Figure_06.tif
    │   ├── Figure_ID_06.pptx
    │   ├── old
    │   ├── _peri_SWR_pos_around_gE_and_gR
    │   ├── __peri_SWR_pos_around_gE_and_gR_new
    │   ├── _peri_SWR_pos_around_gE_and_gR_new
    │   ├── peri_SWR_pos_around_gE_and_gR_new
    │   └── peri_SWR_pos_around_gE_and_gR_old_range_of_pre, mid, post difinitions
    ├── 07
    │   ├── box
    │   ├── Figure_07.pptx
    │   ├── Figure_07.tif
    │   ├── Figure_08.pptx
    │   ├── Figure_ID_07.pptx
    │   ├── old
    │   ├── polar
    │   ├── scatter
    │   ├── SWR_direction_in_the_eSWR_direction
    │   └── SWR_directions_based_on_gE_and_gR
    ├── 08_rank_dist_KDE
    │   ├── ~$Figure_08.pptx
    │   ├── Figure_08.jnb
    │   ├── Figure_08_KDE_2024-09-29_17-23-39.jnb
```
