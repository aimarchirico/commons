# Skill Conventions

Orchestration conventions shared by the skills and agents in this plugin.
`${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md` governs how code and history
are authored; this file governs how skills run. Reference a section from a
skill the same way CONTRIBUTING sections are referenced, for example
`${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#verification`.

---

## Branch Setup

Determine `<branch-name>` following the naming rules in
`${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#branches`, and resolve
`<base-branch>`:

- When solving an issue, `<base-branch>` comes from the issue's open blockers
  (see the invoking skill for the script that resolves it). If multiple
  candidate branches are reported, prompt the user to pick one, offering the
  candidate PR branches and the repository default branch.
- Otherwise `<base-branch>` is the repository default branch, resolved via
  `gh repo view --json defaultBranchRef`.

Always create the branch from the up-to-date remote base, never from whatever
the local tree happens to be at:

```bash
git fetch origin
```

Skip branch creation entirely if already on a branch the invoking skill created
in an earlier, resumed run for the same work.

---

## Worktrees

Skills that implement changes do so in an isolated worktree, so the user's
working tree is never disturbed. `<worktree-path>` is `../worktrees/<branch-name>`,
nested under a `worktrees/` directory that is itself a sibling of the repository
root.

Create a new branch and worktree together:

```bash
git worktree add -b <branch-name> <worktree-path> origin/<base-branch>
```

Check an existing remote branch out into a worktree:

```bash
git worktree add <worktree-path> <branch-name>
```

Remove the worktree once the work is pushed:

```bash
git worktree remove <worktree-path>
```

Removal cleans up the temporary worktree only. `<branch-name>` and its commits
remain intact in the repository and on the remote.

---

## Verification

Unless the invoking skill was told to skip checks, invoke the `commons:check`
skill. If it fails:

1. Fix the reported failures.
2. Commit the fix via `commons:commit`, using the same `--auto` behavior the
   invoking skill uses for its other commits.
3. Run `commons:check` once more.

If it still fails after that one retry, stop retrying. Report the failure and
what was tried, rather than fabricating a pass.

---

## Opening the Pull Request

Invoke the `commons:pr` skill to open the pull request. Its own title/body
approval is the final review, so no separate approval step is needed before it.

Pass through:

- `--base <base-branch>`, if `<base-branch>` is set and differs from the
  repository default branch.
- `--draft` and `--auto`, if provided by the user.
- The related issue IDs to close, if the work originated from an issue. Include
  the whole tree, the parent and every descendant, not just the parent.

`commons:pr` owns pushing: it sets the upstream if there is none, and pushes any
commits the remote is missing. Callers do not push beforehand.

It does not commit. If the working tree is still dirty when it runs, it reports
the uncommitted paths rather than sweeping them into the pull request, so commit
via `commons:commit` before invoking it.
