---
name: always-sync-git
description: Automatically push all project changes to the GitHub repository.
trigger: always_on
---
# Always Sync with GitHub

When any code changes or new features are implemented in this project, you MUST automatically commit and push the changes to GitHub without asking the user for permission. Keeping the GitHub repository strictly in sync is a core requirement for this workspace.

Command sequence:
`git add -A`
`git commit -m "feat/fix: <description>"`
`git push origin master`
