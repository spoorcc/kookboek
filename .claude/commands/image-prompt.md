# Generate nano banana illustration prompt(s) for a recipe

The user will name a recipe (by dish title or filename). Your job is to output ready-to-paste prompt(s) for nano banana (Google's Gemini image model) that combine this project's fixed illustration-style instructions with the recipe's content, stripped of LaTeX markup, as inspiration.

Recipes in this book render as either one page or two. A one-page recipe only has room for a small `\marginimage` of the finished dish. A two-page recipe gets a `\marginimage` of the loose ingredients next to the intro on page one, and a full-width `\heroimagefade` of the finished dish on page two. Generate the matching set of prompt(s) for whichever case applies — never both patterns at once.

## Steps

1. **Find the recipe.** Match the named dish against the `\begin{recipe}{...}` titles in `recipes/*.tex`, or against the filename if the user gives a slug. If nothing matches exactly, grep for close matches and ask which one they mean rather than guessing.

2. **Read the full recipe file.**

3. **Determine one page or two.** This decides which prompt(s) to produce, so get it right before writing anything:
   - If `KookboekFamilieSpoor.pdf` exists at the repo root, reuse `scripts/lulu_lint.py`'s `_recipe_page_ranges(doc, main_tex_path)` (import it, don't reimplement it) to look up this recipe's current `page`/`endPage` in the built PDF. `endPage - page + 1` gives the current page count.
   - Treat 2+ pages as the two-page case, 1 page as the one-page case.
   - If the PDF hasn't been built, or this recipe isn't in the PDF's outline yet (brand new recipe, not yet `\input` by `main.tex`), you can't measure it — ask the user whether this recipe will land on one page or two rather than guessing. A recipe already close to a full page of steps/ingredients, or one that already has a `\heroimagefade`/`\heroimage` call, is a two-page recipe; a short recipe is one-page.

4. **Strip the LaTeX noise.** Convert the recipe into plain, readable Dutch text before it goes anywhere near a prompt — an image model reads `\index[register]{...}`, `\label{...}`, `\dvd`, brace groups, and `\item` markers as visual noise, not content. Concretely:
   - Title: from `\begin{recipe}{Naam}`, plain, no braces.
   - Kicker: the human-readable text argument of `\kicker[...]{...}` (e.g. `Voorgerecht · vlees · Nederlands`), not the bracketed tag list.
   - Meta: the `\meta{...}` text with `\dvd` replaced by `·`.
   - Intro: the `\lettrine{X}{rest}` paragraph reassembled into a normal sentence (`X` + `rest`), with any trailing `\index`/`\label`/comments dropped.
   - Ingredients: one line per `\ing{amount}{name}` → `amount name`, and per `\ingb{name}` → `name`, dropping every `\index[register]{...}` tag.
   - Steps: the text of each `\item`, dropping `\index`/`\label`, as a numbered or bulleted list.
   - Tip: the plain text of `\tip{...}`, if present.
   - Drop entirely: `\heroimage`/`\heroimagefade`/`\heroplaceholder`/`\ingredientsketch`/`\marginimage` calls, `\blockrule{...}` labels (the "Ingrediënten"/"Bereiding" section names can stay as plain headings if useful, but the macro itself goes), and any `%` comments.
   - Don't otherwise summarize, translate, or embellish the recipe — keep every ingredient, amount, and step, only the LaTeX markup is removed.

5. **One-page case: output a single margin-image prompt.** The finished dish only, small and tidy — this is the exact style already used for `kibbeling-kroketjes-sla`, `asperges`, `coleslaw`, `ovenfriet`, and `spinazierisotto`.

   ```
   Gebruik dit recept als inspiratie. Maak een verfijnde waterverfillustratie van het opgediende gerecht, in dezelfde stijl als de andere illustraties in dit kookboek:
   - Gezichtspunt: driekwart vanuit een licht verhoogde hoek, niet recht van boven en niet recht van opzij, zodat je in de kom, pan of op het bord kijkt.
   - Compositie: alleen het gerecht in zijn kom, pan of op zijn bord, verder niets — geen losse ingrediënten, geen rekwisieten. Bij een ovenschotel of ander gerecht waarvan de vulling al zichtbaar is (lasagne, moussaka, quiche, gevulde rollade), eventueel met een aangesneden punt of plak zodat de laagjes/vulling zichtbaar zijn.
   - Kleuren: zachte, natuurlijke aquarelkleuren (crème, terracotta, zachtgroen, warme bruinen), geen felle of verzadigde kleuren.
   - Detailniveau: herkenbare texturen en vormen, maar los en schilderachtig aangezet, niet fotorealistisch.
   - Achtergrond: puur wit, geen tafel of ondergrond getekend, alleen een zachte, koelgrijze slagschaduw onder het gerecht.
   - Geen losse artistieke verfspatten of vlekken op de achtergrond.
   - Geen tekst, geen rand.
   Geschikt voor een professioneel kookboek, als klein bijschrift-formaat plaatje in de marge.

   <cleaned plain-text version of the recipe>
   ```

6. **Two-page case: output two separate prompts**, each in its own fenced code block, clearly labeled so the user knows which is which.

   **6a. Ingredients prompt** (for the page-one `\marginimage`) — ask directly for a narrow, vertical arrangement so it drops into the margin column with no further rearranging needed:

   ```
   Gebruik dit recept als inspiratie. Maak een verfijnde waterverfillustratie van alleen de losse, rauwe ingrediënten uit dit recept (geen bereid of opgediend gerecht), in dezelfde stijl als de andere illustraties in dit kookboek:
   - Compositie: een smalle, verticale compositie (portretformaat, veel hoger dan breed) met de hoofdingrediënten los onder elkaar geplaatst, van boven naar beneden, met duidelijke witruimte tussen elk item. Geen bord, kom, pan of ander kookgerei — alleen de ingrediënten zelf. Sla generieke, niet-visuele items over (zout, peper, water, bouillon) en beperk je tot de ingrediënten die je ook echt zou herkennen op een plaatje.
   - Kleuren: zachte, natuurlijke aquarelkleuren (crème, terracotta, zachtgroen, warme bruinen), geen felle of verzadigde kleuren.
   - Detailniveau: herkenbare texturen en vormen, maar los en schilderachtig aangezet, niet fotorealistisch.
   - Achtergrond: puur wit, geen tafel of ondergrond getekend, alleen een zachte, koelgrijze slagschaduw onder elk ingrediënt.
   - Geen losse artistieke verfspatten of vlekken op de achtergrond.
   - Geen tekst, geen rand.
   Geschikt voor een professioneel kookboek, als smalle illustratie in de marge naast de inleidende tekst.

   <cleaned plain-text version of the recipe>
   ```

   **6b. Hero prompt** (for the page-two `\heroimagefade`) — the finished dish alone, generously framed for a full-width shot:

   ```
   Gebruik dit recept als inspiratie. Maak een verfijnde waterverfillustratie van het opgediende gerecht, in dezelfde stijl als de andere illustraties in dit kookboek:
   - Gezichtspunt: driekwart vanuit een licht verhoogde hoek, niet recht van boven en niet recht van opzij, zodat je in de kom, pan of op het bord kijkt.
   - Compositie: alleen het gerecht in zijn kom, pan of op zijn bord, verder niets — geen losse ingrediënten, geen rekwisieten, die staan al in een apart plaatje. Bij een ovenschotel of ander gerecht waarvan de vulling al zichtbaar is (lasagne, moussaka, quiche, gevulde rollade), eventueel met een aangesneden punt of plak zodat de laagjes/vulling zichtbaar zijn. Geef het gerecht ruim baan: een bredere, landschapsgerichte compositie past beter bij een pagina-brede illustratie dan een vierkante of hoge crop.
   - Kleuren: zachte, natuurlijke aquarelkleuren (crème, terracotta, zachtgroen, warme bruinen), geen felle of verzadigde kleuren.
   - Detailniveau: herkenbare texturen en vormen, maar los en schilderachtig aangezet, niet fotorealistisch.
   - Achtergrond: puur wit, geen tafel of ondergrond getekend, alleen een zachte, koelgrijze slagschaduw onder het gerecht.
   - Geen losse artistieke verfspatten of vlekken op de achtergrond.
   - Geen tekst, geen rand.
   Geschikt voor een professioneel kookboek, als pagina-brede illustratie.

   <cleaned plain-text version of the recipe>
   ```

   Both style blocks were derived by reviewing the existing split illustrations in `images/` (e.g. `tortellini-al-forno-ingredienten.png`/`tortellini-al-forno-hero.png`); if the book's visual style shifts, re-derive them from a fresh sample rather than hand-tweaking them out of sync with the actual art.

7. **Add a link.** After the prompt(s), add a plain link to `https://gemini.google.com/app` so there's one click to get to nano banana. Gemini doesn't support pre-filling the prompt via a URL parameter (that only works with a third-party browser extension the user may not have), so don't build a link with the prompt baked in — the prompt still needs to be pasted in manually.

8. **Flag existing art.** If the recipe already has a `\heroimage{...}{...}`/`\heroimagefade{...}` call and/or a `\marginimage{...}` call, say so briefly for each one found so the user knows a new illustration would replace existing art — but still produce the prompt(s) if they want them anyway.

9. **Stop there.** This skill's job is producing the prompt(s), not generating the image, saving it under `images/`, or wiring it into the recipe with `\heroimage`/`\heroimagefade`/`\marginimage`. Only help with those follow-up steps if the user separately asks.
