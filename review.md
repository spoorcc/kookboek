# Review — Kookboek Familie Spoor

Doorloop van alle 60 recepten in `recipes/`, op zoek naar onduidelijke stappen,
ontbrekende of niet-gebruikte ingrediënten, en hoeveelheden die niet kloppen of
ontbreken. Puur bewuste `\ingb`-items ("naar smaak", "op gevoel") zijn niet
meegenomen, dat is een gekozen stijl in het boek. Hieronder alleen recepten
waar iets is gevonden, gegroepeerd per hoofdstuk zoals in `main.tex`.

## Voorgerechten

Geen bijzonderheden gevonden. Riso freddo, tomatensoep, mini-aardappelquiches
en tompouce met geitenkaas zijn intern consistent.

## Hoofdgerechten

### recipes/fajitas.tex
- **Ontbrekend ingrediënt**: de marge-tip zegt "Bak de zesde wrap iets langer
  en harder in de droge pan", maar de ingrediëntenlijst noemt maar 5 wraps
  (`\ing{5}{volkoren wraps}`) voor 5 personen. Er is dus geen zesde wrap om
  apart te bakken. Of de tip moet weg, of er moet een wrap bij in de lijst.

### recipes/kofta.tex
- **Vage hoeveelheid**: `\ing{}{2 tomaten (naar keuze), in stukken}` heeft een
  leeg hoeveelheidsveld terwijl het aantal (2) gewoon in de naam staat. Dat
  oogt als een tikfout, het hoort `\ing{2}{tomaten (naar keuze), in stukken}`
  te zijn.

### recipes/jambalaya.tex
- **Vage/mogelijk te weinig hoeveelheid**: 400 g rijst op maar 250 ml
  kippenbouillon is weinig vocht. Rijst heeft meestal zo'n anderhalf tot twee
  keer zijn volume aan vocht nodig om gaar te worden. De tomaten en tomatenpuree
  leveren wel wat extra vocht, maar het is de moeite waard om te vermelden dat
  er zo nodig water of bouillon bij moet, anders dreigt de rijst aan te branden
  voor hij gaar is.

### recipes/hutspot.tex
- **Onduidelijke stap**: er wordt niet gezegd hoelang de rookworst moet warmen
  ("Verwarm de rookworst ondertussen in een aparte pan met wat water op laag
  vuur"), terwijl de rest van het recept juist overal wel tijden geeft. Een
  richtlijn (bijvoorbeeld "ca. 15 minuten") zou hier helpen.

### recipes/quiche-groente-geitenkaas.tex
- **Missend ingrediënt**: stap 2 zegt "Snijd de paprika's, courgette,
  aubergine, venkel en rode ui in grove stukken", maar aubergine staat nergens
  in het Ingrediënten-blok. Wie boodschappen doet aan de hand van de lijst
  komt zonder aubergine te staan.

### recipes/shakshuka.tex
- **Vage hoeveelheid**: de ingrediëntenlijst geeft "4–6 eieren", maar stap 5
  zegt vast "Maak 6 kuiltjes ... breek er één voor één de eieren in". Dat
  klopt niet meer als je voor het lagere aantal (4) kiest.

### recipes/pizza.tex
- **Onduidelijke stap**: bij de saus staat "Giet door een fijn vergiet en laat
  het overtollige vocht uitlekken", zonder tijdsindicatie. De rest van het
  recept is juist heel precies (bloem tot op de gram, bakkerspercentages), dus
  een richttijd (bijvoorbeeld "10 minuten") zou hier passen.
- **Overig**: de topping (prosciutto, mozzarella, basilicum, parmigiano
  reggiano) heeft helemaal geen hoeveelheid, zelfs geen "naar smaak". Voor
  twee pizza's zou een indicatie (bijv. 100 g prosciutto, 1 bol mozzarella)
  net wat houvast geven.

### recipes/quesadillas.tex
- **Overig**: `\meta` zegt "Voor 5 personen", maar het recept maakt maar 3
  quesadilla's van 6 wraps (elke quesadilla = 2 wraps). Drie quesadilla's
  delen tussen vijf mensen is krap; een opmerking om ze in stukken te snijden
  en te delen, of een wrap erbij, zou dit oplossen.

### recipes/pasta-carbonara.tex
- **Vage hoeveelheid**: het recept gebruikt maar `\ing{2}{dooiers}` voor 5
  personen. Carbonara wordt meestal met ongeveer 1 dooier per persoon
  gemaakt, dus met 2 dooiers voor 5 man is er kans dat de saus te dun wordt om
  alle pasta te binden.

### recipes/mac-n-cheese.tex
- **Onduidelijke stap / ontbrekende hoeveelheid**: bij de bechamelsaus staat
  alleen `\ingb{boter}`, `\ingb{bloem}` en `\ingb{melk}`, zonder enige
  aanwijzing van verhouding. Dat is de hoofdcomponent van het gerecht, en
  zonder richtgetal (bijvoorbeeld 40 g boter, 40 g bloem, 500 ml melk) is dit
  voor een beginnende kok gokken.

## Bijgerechten

### recipes/rode-rijst.tex
- **Overig**: de ingrediëntenlijst noemt "1 rundsbouillonblokje" (enkelvoud),
  maar de bereiding zegt "Voeg de bouillonblokjes toe" (meervoud). Klein
  slordigheidje waardoor niet meteen duidelijk is of er nu één of meerdere
  blokjes nodig zijn.

## Brood & basis

### recipes/pretzels.tex
- **Overig**: "baking soda" staat twee keer in het Engels in een verder
  volledig Nederlands recept (ingrediëntenlijst en stap 6). Voor wie geen
  Engelse kooktermen kent is niet meteen duidelijk wat ze in de winkel moeten
  zoeken; "zuiveringszout" of "natriumbicarbonaat" zou hier passen.

## Bakken

### recipes/sauzijcenbroodjes.tex
- **Vage hoeveelheid**: het hoofdrecept vraagt `\ing{6 g}{gehaktkruiden}`,
  maar het kruidenmengsel eronder telt zelf op tot maar ongeveer 5 g
  (2 + 1 + 0,7 + 0,6 + 0,4 + 0,3 + 0,2 g), en de tekst zegt dat zelf ook
  ("maakt ca. 5 g"). Er wordt dus 1 g meer gevraagd dan het mengsel oplevert.

## Dessert

### recipes/tiramisu-ricotta.tex
- **Missend ingrediënt**: de ingrediëntenlijst noemt "3–4 eieren", maar de
  bereiding splitst expliciet 3 eieren; een eventueel vierde ei wordt alleen
  genoemd voor de dooier ("klop dan een extra eigeel mee" als het mengsel te
  droog is). Het eiwit van dat vierde ei wordt nergens gebruikt, dat mag
  worden verduidelijkt (bijvoorbeeld: bewaar het extra eiwit voor iets anders).

---

Alle overige recepten (onder andere Bobotie, Broodje hamburger, Asperge-lasagne,
Aardappel-groente-vlees, Bloemkoolpasta, Couscous, Basiskoekjes, Bonensalade,
Drollenkoekjes, Lahmacun, Groene salade, Flammkuchen, Lekkerbekjes met
kroketjes en sla, Bloemkoolquiche, Spinazie-quiche, Quiche met ham en prei,
Quiche Lorraine, Quiche met groente in een cirkel, Quiche met chorizo en
geitenkaas, Roti, Venkel-risotto, Pasta alla norma, Pasta met blauwe kaas,
Pasta scarapiello, Pasta amatriciana, Pasta met chorizo en andijvie,
Tortellini al forno, Spruitenstamp, Moussaka, Parmigiana di melanzane,
Gevulde varkensrollade, Nasi, Pita, Shoarmabroodjes, Tarte tatin met wortel,
Groene salade, Bonensalade, Shoarmabroodjes, Wafels, Eierkoeken, Roze koeken,
Meringues, Drollenkoekjes, Risotto, Venkelworstpasta, Tortellini al forno,
Tomatensoep, Riso freddo, Semifreddo en IJstaart met karamel) zijn nagelopen
en intern consistent bevonden: ingrediënten en stappen sluiten op elkaar aan,
oventemperaturen en -tijden zijn aanwezig waar nodig, en vage hoeveelheden
zijn steeds bewuste `\ingb`-keuzes.
