# Improvement backlog

Look is locked in. These are the next things worth fixing, grouped by effort.

---

## Dead code / cleanup (low effort)

- **`preamble.tex` — double `\setmainfont`**: line 78 is immediately overridden by line 80. Delete line 78.
- **`preamble.tex` — stale early `\geometry`**: there's a bare `\geometry{paperwidth=7in...}` call that is always overridden by the mobile/desktop conditional block below it. Delete the early one.
- **`main.tex` — broken NT block**: the `\newif\ifallbooks` / `\allbooksfalse` / bare `\if` block still wraps all the NT `\input` lines. The bare `\if` without a condition is a LaTeX error waiting to happen (currently the block never executes). Either delete it or replace with a proper `\ifallbooks`.
- **`prompt.md`**: dev scratch note committed to the repo. Delete it.
- **`index.html`**: left over from GitHub Pages, which was removed. Delete it.
- **`README.md`**: still references the upstream template (maxkratz). Rewrite to describe the actual project.

---

## Repository hygiene (low–medium effort)

- **No `.gitignore`**: generated files (`srb_bibeln/usx/**`, `render/GT/**`, `render/NT/**`, `compile/**`, `srb_config.tex`, `render/preview.tex`, `render/full.tex`, `*.pdf`, `*.aux`, `*.log`) are all committed. Add a `.gitignore` and decide which generated files should stay tracked.
- **CharisSIL fonts in `raw_data_bible/release/`**: four TTF files committed but never referenced anywhere in the LaTeX. Remove them or document why they're kept.
- **`misc/` logo versions**: 14 PNG variants with no indication of which is current. Either prune to the one that's used or add a note.

---

## Build pipeline (medium effort)

- **`usx_to_tex.py` is not run in CI**: the generated files (`srb_bibeln/usx/`, `render/GT/`, etc.) are committed, so a change to `usx_config.json` or the raw USX data won't take effect until someone manually runs the script locally. Add a CI step that runs `python usx_to_tex.py` and fails if the output differs from what's committed (or just always regenerates before compiling).
- **Three workflows all fire on every push**: `ci.yml`, `main.yml`, and `webpage_plus_pdf.yml` overlap in what they build. Consolidate or add path filters so the heavy per-book parallel job doesn't run on docs-only commits.
- **No local build command documented**: a new contributor has no idea how to compile locally. A `Makefile` with `make preview` / `make print` / `make ereader` targets would make this obvious.

---

## Feature flags split across two files (medium effort)

`usx_config.json` controls content features (verse numbers, section headings, footnotes, cross-references) while `render_config.tex` controls layout features (mobile, background, back button, TOC). This means enabling verse numbers requires re-running the Python generator, while toggling the back button does not. Consider either:

- Moving the content feature flags into `render_config.tex` as well (requires changing how `usx_to_tex.py` always emits `\versenumber` calls and letting LaTeX suppress them), or
- Keeping the split but documenting clearly which file does what and that a Python re-run is needed for content changes.

---

## Typography (medium–hard effort)

- **Poetry layout**: Psalms and other poetic books (Job, Proverbs, Isaiah, etc.) currently render as continuous prose. The USX format has `<para style="q1">` / `<para style="q2">` markers for poetic lines and indentation. Parsing these and emitting `\begin{verse}` or custom indented blocks would significantly improve readability of about half the Bible.
- **Drop cap letter exceptions**: only `J` has a custom `lraise` tuning. Several other letters (`I`, `T`, `Q`, `Y`) have similar height/baseline issues that may need per-letter adjustments. Worth auditing all 66 first-chapter opening letters.
- **TOC page numbers drift**: noted in `render_config.tex`. Root cause is that `\tableofcontents` is emitted before the chapter content, so page numbers are from the previous compile pass. Two-pass compilation (`latexmk`) helps but doesn't fully fix it for long documents. Consider switching TOC to a separate compile or suppressing page numbers in the TOC entirely for the print variant.

---

## Longer-term

- **Variant build artifacts in CI**: right now CI produces one PDF built from whatever `render_config.tex` happens to say. It would be useful to produce all three variants (print, e-reader, mobile) as named artifacts on every push without manual flag toggling. This could be done by overriding flags via `\def` on the command line (`xelatex '\def\variant{ereader}\input{main}'`) and generating three separate PDFs in one workflow run.
- **Font subsetting for e-reader PDF**: EB Garamond embeds full font tables. For the e-reader variant, enabling font subsetting in XeLaTeX would reduce PDF size noticeably.
