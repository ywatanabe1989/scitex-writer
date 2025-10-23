<!-- ---
!-- Timestamp: 2025-05-06 07:29:45
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/GIT_GITHUB.md
!-- --- -->

# Git/GitHub Rules

- `git_init command creates local `./.git` and remote origin `git@ywatanabe1989:repository-name.git`
- Always work on develop branch
- Add periodically
- Commit in a meaningful chunks
- Push to origin/develop
- Create pull request from origin/develop to origin/main
- Create releases with tags in the format of v1.0.0

## Git Aliases and Functions
#### /home/ywatanabe/.bash.d/all/010_git/git_add_gitignore_template.src
#### /home/ywatanabe/.bash.d/all/010_git/git_advanced.src
#### /home/ywatanabe/.bash.d/all/010_git/git_basics.src
#### /home/ywatanabe/.bash.d/all/010_git/git_checkout.src
#### /home/ywatanabe/.bash.d/all/010_git/git_cleanup_locks.src
#### /home/ywatanabe/.bash.d/all/010_git/git_configure.src
#### /home/ywatanabe/.bash.d/all/010_git/git_diff.src
#### /home/ywatanabe/.bash.d/all/010_git/git_download_dir.src
#### /home/ywatanabe/.bash.d/all/010_git/git_encrypt_secrets.src
#### /home/ywatanabe/.bash.d/all/010_git/git_init.src
#### /home/ywatanabe/.bash.d/all/010_git/git_merge.src
#### /home/ywatanabe/.bash.d/all/010_git/git_pulls.src
#### /home/ywatanabe/.bash.d/all/010_git/git_rename_remote.src
#### /home/ywatanabe/.bash.d/all/010_git/git_reset.src
#### /home/ywatanabe/.bash.d/all/010_git/git_resolve_timestamp_conflicts.src
#### /home/ywatanabe/.bash.d/all/010_git/git_sync_.src
#### /home/ywatanabe/.bash.d/all/010_git/git_track.src
#### /home/ywatanabe/.bash.d/all/010_git/git_tree.src
#### /home/ywatanabe/.bash.d/all/010_git/git_unstage.src
#### /home/ywatanabe/.bash.d/all/010_git/git_untrack.src

## GH Aliases and Functions
#### $HOME/.bash.d/010_github/github_add_release.src
#### $HOME/.bash.d/010_github/github_basics.src
#### $HOME/.bash.d/010_github/github_load_config.sh
#### $HOME/.bash.d/010_github/github_jump.src
#### $HOME/.bash.d/010_github/github_variables.src

## Git/GitHub scripts
#### $HOME/.bin/git/gh_pull_request.sh
#### $HOME/.bin/git/git_acp_custom_lisp_modules.sh
#### $HOME/.bin/git/git_create_tests_tree.sh
#### $HOME/.bin/git/git_sync.sh
#### $HOME/.bin/git/git_upload_public_dotfiles.sh
#### $HOME/.bin/git/merge_timestamp.sh
#### $HOME/.bin/git/monitor_repository.sh
#### $HOME/.bin/git/update_dotfiles_priv.sh

## GitHub Authentications
#### $HOME/.ssh/conf.d/ywata.conf
#### $HOME/.bash.d/secrets/access_tokens/github.txt 
#### $GITHUB_TOKEN

```
Host github-ywatanabe1989 github-p github-y
    ControlPath ~/.ssh/.control-ywatanabe1989:%h:%p:%r
    HostName github.com
    User git
    ForwardX11 no
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
```

<!-- EOF -->