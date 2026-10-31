# 5. Release from Conventional Commits on each merge

## Status

Accepted

## Context

commvnist asked for CI that bumps the version and publishes the release on its own, incrementing major, minor or patch correctly, or as something in the pull request says (2026-10-31). Until now a release meant bumping `plugin.json` by hand, regenerating the Codex files, renaming the changelog section, tagging and publishing; v0.6.0 was merged without its tag or release. Commits on main are squash merges whose subjects are the pull request titles, in Conventional Commits.

Options considered:

- **Bump on each merge, from the commit subjects**, with a `release:` label on the pull request to override. Nothing to install; the title the author already writes decides the version.
- **A release pull request** (release-please and similar): a bot keeps a pull request open with the next version and changelog, and merging it releases. Batches several merges into one release, but adds a dependency, a second pull request to merge, and a bot-made pull request that our checks won't run on, since GitHub doesn't trigger workflows on what the workflow's own token creates.
- **A label as the only signal**: every pull request needs one, and forgetting it skips the release.
- **Changelog generated from commit subjects**: less to write, but subjects tell a reviewer what the diff does, not what a user notices; plumb's changelog is written for users.

## Decision

Bump on each merge. `scripts/release.py` reads the commits since the last tag: a `!` or a `BREAKING CHANGE:` footer is major, `feat` minor, `fix` and `perf` patch, any other type releases nothing; a `release:major|minor|patch|none` label on the commit's pull request overrides its subject, and the largest bump wins. Semantic versioning's rule is applied as written below 1.0 too, so the first breaking change releases 1.0.0. The changelog stays hand-written: the `## Unreleased` section becomes the version's section and the release notes, and commit subjects are listed only when there is none. A version already in the files without a tag is released as it is, which releases v0.6.0 and lets a failed run, or a bump made by hand, finish on the next merge.

## Consequences

- Every user-facing merge publishes a release; batching several needs `release:none` on all but the last.
- The workflow pushes a `chore(release)` commit to main with its own token, which needs main to accept that push; branch protection that requires pull requests would block it.
- The cleaned zip is attached by calling its workflow from the release workflow, since the release event from the workflow's token doesn't trigger it. A release published by hand still triggers it directly.
- A pull request whose title has the wrong type releases the wrong bump; the label is the fix before merging.
