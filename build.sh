#!/usr/bin/env bash
set -euo pipefail
latexmk -xelatex -jobname=KookboekFamilieSpoor main.tex
latexmk -xelatex -output-directory=. -jobname=KookboekFamilieSpoor-cover cover/cover.tex

if [ ! -x .venv/bin/python3 ]; then
  python3 -m venv .venv >/dev/null 2>&1 || true
fi
if [ -x .venv/bin/python3 ]; then
  PYTHON=.venv/bin/python3
  "$PYTHON" -m pip install --quiet -r scripts/requirements.txt >/dev/null 2>&1 || true
else
  PYTHON=python3
fi

if "$PYTHON" -c "import fitz" >/dev/null 2>&1; then
  # Flatten PDF transparency (TikZ `path fading` soft masks on the cover
  # art) before the print check — Lulu strongly recommends against
  # shipping transparency to print.
  "$PYTHON" scripts/flatten_transparency.py KookboekFamilieSpoor.pdf
  "$PYTHON" scripts/flatten_transparency.py KookboekFamilieSpoor-cover.pdf
  "$PYTHON" scripts/lulu_lint.py KookboekFamilieSpoor.pdf
else
  echo "note: skipping Lulu print check — install pymupdf (pip3 install -r scripts/requirements.txt)"
fi
