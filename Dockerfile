FROM texlive/texlive:latest

# Fonts are vendored in fonts/ — no runtime download needed.

# PyMuPDF powers scripts/lulu_lint.py (Lulu.com print-readiness checks run by build.sh).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && (pip3 install --no-cache-dir pymupdf || pip3 install --no-cache-dir --break-system-packages pymupdf)

WORKDIR /work
