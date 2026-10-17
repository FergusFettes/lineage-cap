# Repository audit before public release

15 October 2026. Development history retained. On 16 October 2026 history was
rewritten once to remove the personal paths and private links listed below.

## Scope

Inspected all 356 reachable Git objects in the pre-cleanup repository, including
177 UTF-8 text blobs, historical file names, commit messages and author identities.
Searched historical blobs for common GitHub, OpenAI and AWS credential patterns
and private-key headers; reviewed text matches for personal paths, private
artifact links, email addresses and credential-related words. This is a targeted
repository audit, not a guarantee that every possible secret format is absent.
Ignored local files and external/private artifact contents are outside this scope.

## Findings

- No matches for the credential patterns checked. The `api-key` text match was
  an unpopulated integration-setting example in Beads configuration.
- Earlier README versions and the deleted `REVIEW.md` contained a personal wiki
  path, and README histories contained private Claude artifact links. On 16
  October 2026 these strings were replaced throughout history with
  `git filter-repo --replace-text`; commit hashes before that date changed.
- Author email addresses remain intentionally in publication and commit metadata.
  History also includes an agent author identity and development/review messages.
- `.beads/issues.jsonl` contains project task descriptions and author metadata.
  It remains tracked for development continuity; the Dolt database is ignored.
- Downloaded reference papers are ignored, and no PDF files appeared in the
  pre-cleanup reachable object names. The publication PDF is now tracked.
- Apparent path matches in PNG bytes were binary false positives, not embedded
  personal filesystem paths.

## Publication cleanup

The short publication is now `first-flush-likelihood.qmd` / `first-flush-likelihood.pdf` and is the
default build. The longer `paper.qmd` remains a draft. Publication briefs live in
`docs/`; numerical provenance stays in `notes/` and `results/`. Original repository
material was MIT licensed; from `v1.0-note` code is MIT and text, figures and data
are CC BY 4.0. Third-party cited works are not relicensed.

The baseline rerun reproduced its numerical tables and values. Its saved config
copy was older than the current input config (sweep settings and implementation
metadata differed); the saved copy and summary hash were refreshed. No model
inputs or numerical results were changed for publication cleanup.

## Verification

- `make baseline check`: baseline regenerated; 57 tests passed.
- `make`: PDF and HTML rendered without unresolved-citation warnings.
- Fresh local clone: locked dependencies installed, all 57 tests passed, and
  `make note-figures note` regenerated every note figure plus PDF and HTML.
- All 13 PDF pages visually reviewed; metadata contains the publication title
  and author, with no filesystem paths.

The repository was made public on 16 October 2026 and the note tagged
`v1.0-note`.

## Post-audit update (16 October 2026)

Since the audit verification above, the default build was made PDF-only,
the light-cone figure was dropped from the short note (six figures remain),
an interactive companion site was added, and the model wording was clarified
to effective retained-progress trajectories / growing arena requirements.
Those later changes did not alter the baseline numerical inputs or saved
sweep results. Read the verification block as the state at audit time, not
as a description of today's Makefile defaults.
