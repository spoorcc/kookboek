# Kookboek — Familie Spoor

<img src="docs/cover-preview.png" alt="Cover of Kookboek — Familie Spoor" width="360">

A family cookbook: the recipes one family actually cooks, written down and
typeset as a proper vintage, two-color book — cream paper, a handwriting
accent, drop caps, margin "Tip van Ben" notes, a category table of contents,
and an alphabetical index at the back.

## Browse it online

[spoorcc.github.io/kookboek](https://spoorcc.github.io/kookboek/) — search the
recipes and read any of them right in the browser.

## Get a printed copy

The book is printed on demand via [Lulu.com](https://www.lulu.com). To order one:

1. Go to [lulu.com/create](https://www.lulu.com/create) and start a new print book.
2. Upload `KookboekFamilieSpoor.pdf` (interior) and `KookboekFamilieSpoor-cover.pdf` (cover).
3. Pick **Crown Quarto** (189 × 246 mm / 7.44 × 9.68 in) as the trim size — the
   book is typeset to that exact format.

## Build it locally

Requires XeLaTeX. Run:

```sh
./build.sh
```

This produces `KookboekFamilieSpoor.pdf` and `KookboekFamilieSpoor-cover.pdf`.

## License

The book itself — recipes, prose, and illustrations — is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see
[LICENSE](LICENSE)): copy it, adapt it, print your own family's version, just
credit Familie Spoor and share it under the same license.

The code that builds it is licensed separately under [MIT](LICENSE-MIT) —
Creative Commons licenses aren't meant for software.
