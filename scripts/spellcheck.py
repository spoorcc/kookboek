#!/usr/bin/env python3
"""Dutch spell check for the LaTeX prose in this cookbook.

Strips this project's LaTeX macros down to plain prose (custom macros
like \\ing, \\kicker, \\lettrine are project-specific, so the generic
hunspell TeX filter mangles them) and runs the result through hunspell's
nl_NL dictionary, plus a project wordlist for recipe vocabulary that
isn't in the standard dictionary (loanwords, unit abbreviations, proper
nouns).

Usage:
    python3 scripts/spellcheck.py [--wordlist FILE] [FILES...]

Exits non-zero if any word outside the dictionary/wordlist is found.
"""

import argparse
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_WORDLIST = REPO_ROOT / "scripts" / "spellcheck-wordlist.txt"

# Commands whose arguments are not prose and should be dropped entirely.
DROP_WITH_ARGS = (
    "label", "ref", "pageref", "nameref", "eqref", "autoref", "cref", "Cref",
    "cite", "includegraphics", "index", "heroimagefade", "marginimage",
    "input", "usepackage", "documentclass", "setmainfont", "geometry",
    "pagestyle", "thispagestyle", "color", "textcolor", "addcontentsline",
)

# Environments that hold diagram/drawing code, not prose.
DROP_ENVIRONMENTS = ("tikzpicture",)


def strip_latex(text: str) -> str:
    # Comments (a bare, non-escaped %).
    text = re.sub(r"(?<!\\)%.*", "", text)

    # Diagram/drawing environments: none of their content is prose.
    for env in DROP_ENVIRONMENTS:
        text = re.sub(
            rf"\\begin{{{env}}}.*?\\end{{{env}}}", " ", text, flags=re.DOTALL
        )

    # \lettrine{X}{rest} is one word split across two macro arguments;
    # reunite it before stripping braces, or the first letter is lost.
    text = re.sub(r"\\lettrine\{([^}]*)\}\{([^}]*)\}", r"\1\2", text)

    # \heroimage{file}{caption}: the file path isn't prose, the caption is.
    text = re.sub(r"\\heroimage\{[^}]*\}\{([^}]*)\}", r"\1", text)

    # \begin{env}/\end{env}: the environment name isn't prose.
    text = re.sub(r"\\(begin|end)\{[^}]*\}", " ", text)

    # Spacing control sequences carry no words.
    text = re.sub(r"\\[,; ]", " ", text)

    # Drop commands whose argument(s) aren't prose.
    for cmd in DROP_WITH_ARGS:
        text = re.sub(rf"\\{cmd}\*?(\[[^\]]*\])?(\{{[^}}]*\}})*", " ", text)

    # Math mode content isn't prose.
    text = re.sub(r"\$[^$]*\$", " ", text)

    # Drop optional [...] arguments (e.g. \kicker[Hoofdgerecht,...]).
    text = re.sub(r"\\[a-zA-Z]+\*?\[[^\]]*\]", " ", text)

    # Remaining commands: drop the command name, keep brace content as text.
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = text.replace("{", " ").replace("}", " ")

    # LaTeX escapes for literal characters.
    text = text.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_")

    # LaTeX typographic double quotes aren't part of the word they wrap.
    text = text.replace("``", " ").replace("''", " ")

    # Number ranges (2--3), fractions (1/2) and length units (1.6cm, 6pt)
    # aren't dictionary words.
    text = re.sub(
        r"\b\d+(?:[.,]\d+)?(?:-{1,2}\d+(?:[.,]\d+)?)?(?:/\d+)?"
        r"(?:pt|cm|mm|em|ex)?\b",
        " ",
        text,
    )

    return text


def load_wordlist(path: pathlib.Path) -> set[str]:
    if not path.exists():
        return set()
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words.add(line.lower())
    return words


def check_file(path: pathlib.Path, wordlist: set[str]) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    stripped = strip_latex(text)

    proc = subprocess.run(
        ["hunspell", "-d", "nl_NL", "-l"],
        input=stripped,
        capture_output=True,
        text=True,
        env={"LC_ALL": "C.UTF-8"},
    )
    # hunspell sometimes reports an unrecognised word together with
    # trailing/leading sentence punctuation it failed to split off.
    tokens = (w.strip(".,;:!?()[]{}\"") for w in proc.stdout.split())

    # Tokens with no letters at all (stray quote marks, "+", leftover
    # punctuation) can never be real dictionary words.
    unknown = [
        w for w in tokens if w and w.lower() not in wordlist and re.search(r"[^\W\d_]", w)
    ]

    if not unknown:
        return []

    # Map each unknown word back to a line number for a useful report.
    lines = text.splitlines()
    hits = []
    for word in unknown:
        line_no = next(
            (i + 1 for i, line in enumerate(lines) if word in line), 0
        )
        hits.append((line_no, word))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=pathlib.Path)
    parser.add_argument("--wordlist", type=pathlib.Path, default=DEFAULT_WORDLIST)
    args = parser.parse_args()

    files = args.files or sorted(
        [*REPO_ROOT.glob("main.tex"),
         *REPO_ROOT.glob("frontmatter/*.tex"),
         *REPO_ROOT.glob("recipes/*.tex")]
    )

    wordlist = load_wordlist(args.wordlist)

    total_hits = 0
    for path in files:
        hits = check_file(path, wordlist)
        if hits:
            rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
            for line_no, word in sorted(hits):
                print(f"{rel}:{line_no}: {word}")
            total_hits += len(hits)

    if total_hits:
        print(
            f"\n{total_hits} word(s) not recognised by the nl_NL dictionary "
            f"or {args.wordlist.name}.",
            file=sys.stderr,
        )
        return 1

    print("Spelling check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
