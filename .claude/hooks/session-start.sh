#!/bin/bash
set -euo pipefail

# Only needed for Claude Code on the web — the devcontainer already has these.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# LaTeX (XeLaTeX + latexmk) for building main.pdf and cover/cover.tex, plus
# the qpdf/ghostscript/hunspell tooling scripts/lulu_lint.py, flatten_transparency.py
# and spellcheck.py need. Mirrors .devcontainer's texlive/texlive image and
# .github/workflows/build-pdf.yml's apt installs.
apt-get update -qq
apt-get install -y --no-install-recommends \
  texlive-xetex \
  texlive-latex-extra \
  texlive-fonts-extra \
  texlive-fonts-recommended \
  texlive-plain-generic \
  texlive-lang-european \
  latexmk \
  qpdf \
  ghostscript \
  hunspell \
  hunspell-nl \
  python3-pip \
  python3-venv \
  >/dev/null
