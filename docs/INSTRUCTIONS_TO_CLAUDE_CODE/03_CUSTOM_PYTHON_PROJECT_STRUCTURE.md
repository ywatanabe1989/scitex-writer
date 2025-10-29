<!-- ---
!-- Timestamp: 2025-05-06 08:43:26
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/prompt_factory/_custom_python_project_structure.md
!-- --- -->

#### Example Rules
- Implement `./examples`

#### Keep Clean and Tidy Project
- Project structure, file/variable names, and code must be clean as you are professional
- Keep repository clean
  - Move unnecessary files like this:
      - `/path/to/unnecessary/file.ext`
      - `/path/to/unnecessary/.old/file-TIMESTAMP.ext`
- Refactor the codebase all the time
  - Functional code must be beautiful
  - Keep it simple, stupid
  - Do not repeat yourself

#### Python Rules
- Do not forget `$ source ./.env/bin/activate`
- Prepare `./requirements.txt` if necessary upon the `./.env`

#### Git Rules
- Use git/gh commands
  - `$ git_init` inializes local and remote repositories using the name of the directory
    - Also, it automatically switches to develop, which you are expected to work on
    - For feature addition, create branch `feature/xxx` and merge into `develop` after completion
    - 
- `git_add_gitignore_template` automatically add my custom `.gitignore` in the current repository

#### Path Rules
- Always use relative path, starting with dots, like "./relative/example.py" or "../relative/example.txt"
  - This is important to make the repository portable
  - Scripts are assumed to be executed from the project root (e.g., ./scripts/example.sh)

#### Reuse Rules
- Do Not Repeat Yourself
  - Use symbolic links wisely
  - Especially large data must be clearly organized and reused
  - Independent modules, such as functions and classes, should be saved in a reusable manner
    - You might want to create utils directory under scripts: `./scripts/utils/awesome_func.py`
    - Then, for example, `from scripts.utils.awesome_func import awesome_func` from multiple files

#### Configuration Rules
- Configuration files should be stored under `./config` in YAML format (e.g., `./config/PATH.yaml`)
- In Python scripts, the `CONFIG` variable stores all YAML files contents as a dot-accessible dictionary
  - `import mngs; CONFIG = mngs.io.load_configs()`
- f-string are acceptable in config YAML files
  - In Python, `eval(CONFIG.VARIABLE.WITH.F.EXPRESSION)` works to fill variables
  - Also, f-string are utilized in a custom manner
    - For example, the following line will be used to search and glob data for patient at specific datetime:
      f"./data/mat/Patient_{patient_id}/Data_{year}_{month}_{day}/Hour_{hour}/UTC_{hour}_{minute}_00.mat"

#### Data Rules
- Centralize data files or symbolic links under `./data`
  - This is the place to locate large files (.npy, .csv, .jpg, and .pth data)
    - However, the outputs of a script should be located close to the script
      - e.g., `./scripts/example.py_out/output.jpg`
    - Then, symlinked to `./data` directory
      - e.g., `./scripts/example.py_out/data/output.jpg` -> `./data/output.jpg`
  - This is useful to link scripts and outputs, while keeping centralized data directory structure
  - Large files under `./scripts` and `./data` are git-ignored
    - Symbolic links are tracked by git to show structure

<!-- EOF -->