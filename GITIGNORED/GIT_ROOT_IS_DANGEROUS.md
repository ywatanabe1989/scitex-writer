<!-- ---
!-- Timestamp: 2026-01-19 04:07:10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/GITIGNORED/GIT_ROOT_IS_DANGEROUS.md
!-- --- -->

- [ ] SHELL SCRIPTS HAVE HEADERS due to convenience for me to develop in Emacs; may be better to remove
- [ ] GIT_ROOT as PROJECT_ROOT is dengerous especially when we will handle multiple projects or use as child directory

For example,

```
DIR=/tmp/my-paper-test-2
git clone https://github.com/ywatanabe1989/scitex-writer.git $DIR
"$DIR"/compile.sh manuscript
```

- [ ] Actually, we would like to handle multiple scitex-writer projects for MCP use

<!-- EOF -->