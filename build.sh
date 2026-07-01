#!/usr/bin/env bash
set -euo pipefail
latexmk -xelatex -jobname=KookboekFamilieSpoor main.tex
latexmk -xelatex -output-directory=. -jobname=KookboekFamilieSpoor-cover cover/cover.tex

if ! python3 -c "import fitz" >/dev/null 2>&1; then
  pip3 install --quiet pymupdf >/dev/null 2>&1 || \
    pip3 install --quiet --break-system-packages pymupdf >/dev/null 2>&1 || true
fi

if python3 -c "import fitz" >/dev/null 2>&1; then
  python3 scripts/lulu_lint.py KookboekFamilieSpoor.pdf
else
  echo "note: skipping Lulu print check — install pymupdf (pip3 install pymupdf)"
fi
