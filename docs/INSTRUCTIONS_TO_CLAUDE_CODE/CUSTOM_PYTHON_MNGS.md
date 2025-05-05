<!-- ---
!-- Timestamp: 2025-05-06 08:43:32
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/prompt_factory/CUSTOM_PYTHON_MNGS.md
!-- --- -->


# MNGS-based Python Rule
#### `./.env`
- Python env can be created by `$HOME/.bin/python/python_init_with_local_mngs.sh`

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

<!-- EOF -->