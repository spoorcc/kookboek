# Chef tips review

Source: transcript of a general professional-cooking-tips video, reviewed
2026-07-17 against every file in `recipes/`. Tips that mapped cleanly onto an
existing step were applied directly (see commit `680fcdd`). This file tracks
what's left: tips that were considered and rejected for a specific recipe,
and tips that don't map to any current recipe but are worth checking against
new recipes as they're added.

## Applied

- `kokos-vis.tex` — pat fish dry before it hits the hot oil
- `jambalaya.tex` — bloom the cajunkruiden with the tomato paste instead of
  dumping it in with the stock
- `paella.tex` — give the smoked paprika a half-minute in the hot rice before
  the wet tomato goes in
- `pasta-primavera.tex` — rinse the blanched broccoli under cold water so it
  doesn't dull while it waits
- `eierkoeken.tex` — room-temperature eggs, since this recipe whips them to a
  ruban stage where temperature matters most

## Considered, not applied

- **`mac-n-cheese.tex`** — "never add cold liquid to a roux, it goes lumpy."
  The recipe already adds the milk gradually while stirring continuously,
  which is the actual lump-prevention technique (many classic bechamel
  recipes use cold milk this way on purpose). Warming the milk first would be
  a nice-to-have, not a fix for a real gap.
- **`pommes-fondante.tex`** — "cook garlic before adding liquid, raw garlic
  in a sauce turns bitter." The garlic here braises 25–35 minutes in the oven
  submerged in stock; it's a deliberate infusion technique, not a rushed
  raw-garlic-in-a-quick-sauce case.
- **`lahmacun.tex`** — "cook out tomato paste before it hits liquid." The
  topping is mixed raw and spread directly onto the dough, then cooked
  together in a covered pan; there's no separate saute stage to fold a
  cook-the-puree step into without changing the method.
- **`pide.tex`**, vulling gehakt-tomaat — onion, spices, and tomato go into
  the pan together rather than onion-then-spices-then-tomato. The filling
  gets another 20–25 minutes in the oven after assembly, so raw-onion/raw-spice
  flavor has time to mellow anyway. Splitting the step felt like more
  complexity than the benefit justified.
- **Pasta water salt ratio** ("~1 el zout per 5 L water," don't add oil to
  the water) — checked `pasta-amatriciana.tex`, `pasta-primavera.tex`,
  `gnocchi-sorrentina.tex`, `venkelworstpasta.tex`,
  `marcella-hazan-tomatensaus.tex`, `gnocchi.tex`, `gnocchi-salie-roomboter.tex`,
  `verse-pasta.tex`, `bloemkoolpasta.tex`. All just say "(ruim) gezouten
  water," which is already the house convention and no recipe adds oil to
  the water. Repeating the same boilerplate ratio across nine files felt
  like more churn than a small hint — skipped rather than force it in.

## Not yet checked against a specific recipe

These didn't match anything in the current book (either no recipe uses the
relevant ingredient/technique, or nothing obviously violates the tip), but
they're worth keeping in mind when writing or editing recipes going forward.

**Prep and knife work** — mise en place before starting (veg cut, tinned
tomatoes measured out, ready to go); claw grip; use a fine grater instead of
a knife when a recipe wants garlic/ginger very fine; a bench scraper for
moving chopped veg.

**Pan technique** — heavy-bottomed pans, properly preheated; never overcrowd
a pan, work in batches; when searing for a braise, leave the meat mostly
undisturbed to build crust (opposite of flipping a steak often); food
stuck to stainless steel releases itself once it's ready, don't force it; a
probe thermometer over guessing; baste roasts and rotate the pan for oven
hot spots; score duck leg/breast or pork belly skin before rendering.

**Braises, stews, stock** — save Parmesan rinds in ragùs and sauces; freeze
stock in small portions; buy good tinned tomatoes, the difference shows;
reduce sauces in a wide pan, not a tall one; swirl in cold butter at the end
for gloss (monter au beurre); let a braise or stew cool a couple of hours
before it goes in the fridge; rest braised or confit meat in its own cooking
liquid or fat so it doesn't dry out.

**Storage** — lemongrass and chilies keep well frozen, grate straight from
frozen; fresh herbs stored like cut flowers, in water in the fridge (except
basil, which stays out of the fridge); raw meat and fish go on the bottom
fridge shelf; label and date anything that goes in the freezer.

**Baking** — weigh ingredients in grams rather than cups/tablespoons; sift
flour for cakes and sponges; tap the tin on the counter to release air
bubbles before baking; parchment paper instead of greasing and flouring.

**Seasoning and finishing** — add pepper later in a cook, early high heat
can turn it bitter; fresh soft herbs (parsley, basil) go in at the very end,
hard herbs (rosemary, thyme, bay) at the start; zest citrus before juicing
it (already followed everywhere the book currently does both); rest meat
before slicing, on a rack over a tray so the crust doesn't steam; warm
plates before serving; wipe the plate before it goes to the table.

## Notes

This remote session had no LaTeX/hunspell toolchain installed, so the
applied changes above were reviewed by eye only — run `./build.sh` and
`python3 scripts/spellcheck.py` before merging.
