<!-- ---
!-- Timestamp: 2025-05-05 13:00:27
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/TO_CLAUDE.md
!-- --- -->

# Requests to Claude Code Agent

#### General Requests

- [ ] DO NEVER CHANGE THIS FILE ITSELF
- [ ] Understand the repository
- [ ] Periodically check this file and review the project to find room for improvement

#### Package Manager
- [ ] Use `apt` to install/uninstall packages without sudo privilege

#### Documentation Rule
- [ ] Implement usage of the repository itself especially for other users and LLM agents
  - [ ] `./docs/USAGE_FOR_LLM.md.md`
  - [ ] Update README.md files in important directories

#### Plan Rule
- [ ] Create and update `./docs/PLAN.md` as the project advances
  - [ ] Include `## Goals` and `## Milestones` sections
  - [ ] If we need to change original plan, revise the contents

#### Progress Rule
- [ ] Regularly update progress
  - [ ] Implement mermaid file: `./docs/progress/progress.mmd` in the `TD` Format
    - [ ] Use `mermaid-cli` and render as `./docs/progress/progress.png`
  - [ ] `./docs/progress/progress.md`

#### Structure Rule
- [ ] Update Structure
  - [ ] `./docs/structure/structure.mmd` -> `./docs/structure/structure.png`
    - [ ] Use `mermaid-cli` and render as `./docs/structure/structure.png`
  - [ ] `./docs/structure/structure.md`

#### Test Rule
- [ ] Implement test code, revising these files to follow the nature of the project
  - [ ] `./run_tests.sh`
  - [ ] `./tests/sync_tests_with_source.sh`
  - [ ] `./tests`
  - [ ] `./.github/workflows/xxx.yml`

#### Example Rule
- [ ] Implement `./examples`

#### Escalation Rule
- [ ] Create `./docs/TROUBLE_REPORTS.md` and append encounters problems for future refinement

#### Keep Clean and Tidy Project
- [ ] Project structure, file/variable names, and code must be clean as you are professional
- [ ] Keep repository clean
  - [ ] Move unnecessary files like this:
      - [ ] `/path/to/unnecessary/file.ext`
      - [ ] `/path/to/unnecessary/.old/file-TIMESTAMP.ext`
- [ ] Refactor the codebase all the time
  - [ ] Functional code must be beautiful
  - [ ] Keep it simple, stupid
  - [ ] Do not repeat yourself

#### Python Rule
- [ ] Python env can be created by `$ python_init_with_local_mngs.sh` as `./.env`
- [ ] Do not forget `$ source ./.env/bin/activate`

#### Git Rule
- [ ] Use git/gh commands
  - [ ] `$ git_init` inializes local and remote repositories using the name of the directory
    - [ ] Also, it automatically switches to develop, which you are expected to work on
    - [ ] For feature addition, create branch `feature/xxx` and merge into `develop` after completion
    - [ ] 
- [ ] `git_add_gitignore_template` automatically add my custom `.gitignore` in the current repository

#### Path Rule
- [ ] Always use relative path, starting with dots, like "./relative/example.py" or "../relative/example.txt"
  - [ ] This is important to make the repository portable
  - [ ] Scripts are assumed to be executed from the project root (e.g., ./scripts/example.sh)

#### Reuse Rule
- Do Not Repeat Yourself
  - Use symbolic links wisely
  - Especially large data must be clearly organized and reused
  - Independent modules, such as functions and classes, should be saved in a reusable manner
    - You might want to create utils directory under scripts: `./scripts/utils/awesome_func.py`
    - Then, for example, `from scripts.utils.awesome_func import awesome_func` from multiple files

#### Configuration Rule
- Configuration files should be stored under `./config` in YAML format (e.g., `./config/PATH.yaml`)
- In Python scripts, the `CONFIG` variable stores all YAML files contents as a dot-accessible dictionary
  - `import mngs; CONFIG = mngs.io.load_configs()`
- f-string are acceptable in config YAML files
  - In Python, `eval(CONFIG.VARIABLE.WITH.F.EXPRESSION)` works to fill variables
  - Also, f-string are utilized in a custom manner
    - For example, the following line will be used to search and glob data for patient at specific datetime:
      f"./data/mat/Patient_{patient_id}/Data_{year}_{month}_{day}/Hour_{hour}/UTC_{hour}_{minute}_00.mat"

#### Data Rule
- Centralize data files or symbolic links under `./data`
  - This is the place to locate large files (.npy, .csv, .jpg, and .pth data)
    - However, the outputs of a script should be located close to the script
      - e.g., `./scripts/example.py_out/output.jpg`
    - Then, symlinked to `./data` directory
      - e.g., `./scripts/example.py_out/data/output.jpg` -> `./data/output.jpg`
  - This is useful to link scripts and outputs, while keeping centralized data directory structure
  - Large files under `./scripts` and `./data` are git-ignored
    - Symbolic links are tracked by git to show structure

#### MNGS-based Python scripting Rule
- For python scripts, ensure to follow this MNGS FORMAT:
  ``` python
  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-
  # Time-stamp: "2024-11-03 10:33:13 (ywatanabe)"
  # File: placeholder.py

  __file__ = "placeholder.py"

  """This scripts does XYZ...

  Dependencies:
    - scripts:
      - /path/to/script1
      - /path/to/script2
    - packages:
      - package1
      - package2

    - input:
      - /path/to/input/file.xxx
      - /path/to/input/file.xxx

    - output:
      - /path/to/input/file.xxx
      - /path/to/input/file.xxx

  (Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
  """

  """Imports"""
  import os
  import sys
  import argparse

  """Warnings"""
  # mngs.pd.ignore_SettingWithCopyWarning()
  # warnings.simplefilter("ignore", UserWarning)
  # with warnings.catch_warnings():
  #     warnings.simplefilter("ignore", UserWarning)

  """Parameters"""
  # from mngs.io import load_configs
  # CONFIG = load_configs()

  """Functions & Classes"""
  def main(args):
      pass

  import argparse
  def parse_args() -> argparse.Namespace:
      """Parse command line arguments."""
      import mngs
      script_mode = mngs.gen.is_script()
      parser = argparse.ArgumentParser(description='')
      # parser.add_argument(
      #     "--var",
      #     "-v",
      #     type=int,
      #     choices=None,
      #     default=1,
      #     help="(default: %(default)s)",
      # )
      # parser.add_argument(
      #     "--flag",
      #     "-f",
      #     action="store_true",
      #     default=False,
      #     help="(default: %%(default)s)",
      # )
      args = parser.parse_args()
      mngs.str.printc(args, c='yellow')
      return args

  def run_main() -> None:
      """Initialize mngs framework, run main function, and cleanup.

      mngs framework manages:
        - Parameters defined in yaml files under `./config dir`
        - Setting saving directory (/path/to/file.py -> /path/to/file.py_out/)
        - Symlink for `./data` directory
        - Logging timestamp, stdout, stderr, and parameters
        - Matplotlib configurations (also, `mngs.plt` will track plotting data)
        - Random seeds

      THUS, DO NOT MODIFY THIS RUN_MAIN FUNCTION
      """
      global CONFIG, CC, sys, plt

      import sys
      import matplotlib.pyplot as plt
      import mngs

      args = parse_args()

      CONFIG, sys.stdout, sys.stderr, plt, CC = mngs.gen.start(
          sys,
          plt,
          args=args,
          file=__file__,
          sdir_suffix=None,
          verbose=False,
          agg=True,
      )

      exit_status = main(args)

      mngs.gen.close(
          CONFIG,
          verbose=False,
          notify=False,
          message="",
          exit_status=exit_status,
      )

  if __name__ == '__main__':
      run_main()

  # EOF
  ```

- Always use `argparse`
  - Use argparse Even when no arguments are necessary
  - Thus, a python file should have at least one argument: -h|--help

- Docstrings should be writte in the NumPy style:
  ```python
  def func(arg1: int, arg2: str) -> bool:
      """Summary line.

      Extended description of function.

      Example
      ----------
      >>> xx, yy = 1, "test"
      >>> out = func(xx, yy)
      >>> print(out)
      True

      Parameters
      ----------
      arg1 : int
          Description of arg1
      arg2 : str
          Description of arg2

      Returns
      -------
      bool
          Description of return value

      """
      ...
  ```
- Take modular approaches
  - Smaller functions will increase readability and maintainability

- Naming rules are:
  - lpath(s)/spath(s) for path(s) to load/save

- Use my custom python utility package, `mngs` (monogusa; meaning lazy person in Japanese). 
  - Especially, use 
    - `mngs.gen.start(...)` (fixme; it might be better for me to handle this automatically using hook)
    - `mngs.gen.close(...)` (fixme; it might be better for me to handle this automatically using hook)
    - `mngs.io.load_configs()`
      - Load YAML files under ./config and concatenate as a dot-accesible dictionary
      - Centralize variables here
        - e.g., paths to ./config/PATH.yaml
        - e.g., mnist-related parameters to ./config/MNIST.yaml
    - `mngs.io.load()`
      - Ensure to use relative path from the project root
      - Ensure to load data from (symlinks of) `./data` directory, instead of from `./scripts`
      - Use CONFIG.PATH.... to load data
    - `mngs.io.save(obj, spath, symlink_from_cwd=True)`
      - From the extension of spath, saving code will be handled automatically
      - Note that save path must be relative to use symlink_from_cwd=True
        - Especially, this combination is expected because this organize data (and symlinks) under the ./data directory: `mngs.io.save(obj, ./data/path/to/data.ext, symlink_from_cwd=True)`
    - `mngs.plt.subplots(ncols=...)`
      - Use CONFIG.PATH.... to save data
      - This is a matplotlib.plt wrapper. 
      - Plotted data will be saved in the csv with the same name of the figure
      - CSV file will be the same format expected in a plotting software, SigmaPlot
    - `mngs.str.printc(message, c='blue)`
      - Acceptable colors: 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', or 'grey' 
        - (default is None, which means no color)

- Use `tqdm` for iteractions to show progress

- If errors or issues found in previous rounds, fix them


## Project-specific Requests
- [ ] Improve figure/table handling
  - [ ] Improve documentation for how to link figures and tables when compilation
  - [ ] Where to place
  - [ ] How file names allocated
  - [ ] How to reference in manuscript files:
    - [ ]  `./manuscript/src/{introduction.tex,methods.tex,results.tex,discussion.tex}`
- [ ] Prepare `./requirements.txt` if necessary upon the `./.env`
- [ ] Imprement an example manuscript as a self-descriptive template
- [ ] Imprement an functionality "literature review"
  - [ ] Add pdf files under `./docs/literature`
  - [ ] Update `./manuscript/src/bibliography.bib`
  - [ ] Find the gap to fill
- [ ] Understand the LaTeX compilation scripts under `./scripts/`

<!-- EOF -->