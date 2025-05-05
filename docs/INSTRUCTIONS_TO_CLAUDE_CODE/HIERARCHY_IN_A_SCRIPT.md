<!-- ---
!-- Timestamp: 2025-05-06 06:01:21
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/prompt_factory/programming_hierarchy.md
!-- --- -->

#### Programming Hierarchy Rules
- Use the following kinds of separators. Not that the upper, abstract functions should be written in top.
  - For Python scripts
  ```python
  # 1. Main entry point
  # ---------------------------------------- 


  # 2. Core functions
  # ---------------------------------------- 


  # 3. Helper functions
  # ---------------------------------------- 
  ```
  - For Elisp scripts
  ```elisp
  ;; 1. Main entry point
  ;; ---------------------------------------- 


  ;; 2. Core functions
  ;; ---------------------------------------- 


  ;; 3. Helper functions
  ;; ---------------------------------------- 
  ```
  - For Shell scripts
  ```shell
  # 1. Main entry point
  # ---------------------------------------- 


  # 2. Core functions
  # ---------------------------------------- 


  # 3. Helper functions
  # ---------------------------------------- 
  ```

  - Heading titles can be edited flexibly
  - But keep the separating lines

<!-- EOF -->