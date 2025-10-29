<!-- ---
!-- Timestamp: 2025-05-06 08:04:54
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/prompt_factory/PROGRAMMING_SMALL_ITERATIONS.md
!-- --- -->

#### WorkFlow


#### Branch
- Utilize origin/{main,develop,feature/xxx} in remote
- Utilize {main,develop,feature/descriptive-feature-branch-name} branches in local, correspondingly
- Initialize main and develop branch at first
- From develop branch, create feature/descriptive-feature-branch-name branch
- Your main working branch is feature/descriptive-feature-branch-name branch
  - When a specific feature implemented, merge it to develop

#### Working on feature branch
- To reduce the risk of devastating issues, start building from small, working blocks
- Ideal workflow is:
  1. Planning: 
     Create, update, or revise `./docs/{BLUEPRINT,TODO,PLAN,PROGRESS}.md`
  2. Implement ONE specific script
  3. Implement the corresponding test script
     Each test function must test only one functionality of the source script
     Many test functions are acceptable
     Tests directory must mirror the source script directory structure
  4. When errors occur, return to step 2 until the issue is resolved
  5. Refactor the code
  6. Git add, commit, push, and create pull requests in meaningful chunks

<!-- EOF -->