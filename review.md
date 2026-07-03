# Review — Kookboek Familie Spoor

Doorloop van alle recepten in `recipes/` (76 op dit moment), op zoek naar
onduidelijke stappen, ontbrekende of niet-gebruikte ingrediënten, en
hoeveelheden die niet kloppen of ontbreken. Puur bewuste `\ingb`-items
("naar smaak", "op gevoel") zijn niet meegenomen, dat is een gekozen stijl
in het boek. Alleen nog-openstaande punten staan hieronder; alles wat al is
opgelost is uit dit document verwijderd. Een grote sweep loste sindsdien
vrijwel alle kookgerei-, olie-, ovenstand- en 'waarom'-bevindingen op; wat
hieronder staat is wat daarna nog overbleef.

## Hoofdgerechten

### recipes/jambalaya.tex
- **Vage/mogelijk te weinig hoeveelheid**: 400 g rijst op maar 250 ml
  kippenbouillon is weinig vocht. Rijst heeft meestal zo'n anderhalf tot twee
  keer zijn volume aan vocht nodig om gaar te worden. De tomaten en tomatenpuree
  leveren wel wat extra vocht, maar het is de moeite waard om te vermelden dat
  er zo nodig water of bouillon bij moet, anders dreigt de rijst aan te branden
  voor hij gaar is.

### recipes/quesadillas.tex
- **Overig**: het recept maakt 3 quesadilla's van 6 wraps (elke quesadilla =
  2 wraps). Bij de stilzwijgende 5 personen uit het voorwoord is dat krap
  om te delen; een opmerking om ze in stukken te snijden en te delen, of een
  wrap erbij, zou dit oplossen.
- **Kookgerei**: de ui, paprika en knoflook worden gebakken in "olijfolie"
  zonder pantype (stap 2), en pas later wordt gesproken van "een andere
  koekenpan" voor de quesadilla's zelf (stap 4). Het woordje "andere"
  impliceert dat de eerste pan een ander type was, maar dat is nooit gezegd.

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

### recipes/kofta.tex
- **Kookgerei**: de worstjes worden bruin gebakken in "een pan" zonder dat er
  een type genoemd wordt, en later teruggelegd om te sudderen in dezelfde pan.
  Dat vraagt om een pan met genoeg diepte en bij voorkeur een deksel.

### recipes/moussaka.tex
- **Kookgerei**: de gehaktsaus wordt met naam gemaakt in een "hapjespan" en de
  bechamel in een "hoge pan", maar bij het bakken van de aardappelplakken
  staat nog steeds alleen "Verhit ruim olijfolie in een pan" (stap 7). Omdat
  het recept al twee andere pannen noemt, is niet meteen duidelijk of dit een
  derde, bredere pan moet zijn (nodig om plakken in porties te bakken).
- **Voorverwarmen**: "Verwarm de oven voor op 180\,°C" staat pas in de
  voorlaatste stap, nadat de gehaktsaus, aardappelen, aubergines én
  bechamelsaus al helemaal klaar zijn en de schaal is opgebouwd. Op dat moment
  is er niets meer te doen dan 10 tot 15 minuten wachten tot de oven op
  temperatuur is. Dat had prima eerder gekund, bijvoorbeeld tijdens het bakken
  van de aardappelplakken of de aubergine.

### recipes/quiche-chorizo-geitenkaas.tex
- **Kookgerei**: de prei wordt gebakken "in een pan met een scheutje olijfolie"
  (stap 2) zonder pantype, terwijl de chorizo-stap er direct naast inmiddels
  wel een "droge koekenpan" noemt. Dat maakt de prei-stap de enige nog
  onbenoemde pan in dit recept.

### recipes/aardappel-groente-vlees.tex
- **Kookgerei**: "bak ze in wat boter" voor de krieltjes (stap 3) noemt geen
  pantype. Niet dramatisch, maar een koekenpan vermelden kost weinig en
  voorkomt twijfel.

## Dessert

### recipes/tiramisu-ricotta.tex
- **Missend ingrediënt**: de ingrediëntenlijst noemt "3–4 eieren", maar de
  bereiding splitst expliciet 3 eieren; een eventueel vierde ei wordt alleen
  genoemd voor de dooier ("klop dan een extra eigeel mee" als het mengsel te
  droog is). Het eiwit van dat vierde ei wordt nergens gebruikt, dat mag
  worden verduidelijkt (bijvoorbeeld: bewaar het extra eiwit voor iets anders).

---

Alle overige recepten in dit hoofdstuk zijn intern consistent: ingrediënten
en stappen sluiten op elkaar aan, en vage hoeveelheden zijn steeds bewuste
`\ingb`-keuzes.

## Ovenstand

Vrijwel het hele boek is inmiddels aangevuld met "(boven- en onderwarmte)"
bij elke voorverwarmstap, precies wat hier eerder als algemeen verbeterpunt
stond. Er is nog één recept blijven liggen:

### recipes/parmigiana-melanzane.tex
- **Overig**: "Verwarm de oven voor op 180\,°C." heeft als enige recept in
  het boek nog geen ovenstand erbij.

## Zelfstandig te volgen: voorverwarmen, zout en vaktermen

### recipes/moussaka.tex, recipes/risotto.tex, recipes/pretzels.tex
- **Voorverwarmen**: in alledrie gaat de oven pas laat aan. Bij `moussaka.tex`
  pas in de voorlaatste stap, na het volledig opbouwen van de schaal. Bij
  `risotto.tex` (tomaten-pesto) duikt de oven pas op in stap 6, verstopt
  tussen haakjes, zonder eigen "Verwarm de oven voor op..."-instructie. Bij
  `pretzels.tex` gaat de oven pas aan in stap 6, op het moment dat de
  pretzels al gevormd zijn, terwijl er eerder in het recept al zo'n
  anderhalf uur rusttijd is geweest waarin de oven had kunnen opwarmen.

### recipes/lekkerbekjes-kroketjes-sla.tex
- **Voorverwarmen**: er staat nergens een expliciete "verwarm de oven voor",
  alleen "Bereid de aardappelkroketjes in de oven volgens de aanwijzingen op
  de verpakking" (stap 2). Logisch omdat het per merk verschilt, maar iemand
  die niet gewend is zelf te koken denkt er dan misschien niet aan om de oven
  eerst op te laten warmen voor hij begint.

### recipes/bloemkoolquiche.tex, recipes/quiche-lorraine.tex, recipes/quiche-ham-prei.tex
- **Voorkennis**: bij het voorbakken van de bodem ("Voorbakken: bak de bodem
  15 minuten") wordt nergens gezegd dat je de bodem moet inprikken met een
  vork of met bakbonen/gewichtjes moet vullen. Zonder dat kan de bodem tijdens
  het voorbakken opbollen. Dit geldt voor deze drie quiches met hetzelfde
  deeg, dus dit is één keer bij het basisrecept te verhelpen in plaats van in
  elk bestand apart.

### recipes/bloemkoolpasta.tex
- **Voorkennis**: "Blancheer de bloemkool kort" (stap 3) gebruikt de term
  blancheren zonder uitleg. Er staat wel een doel bij ("net zacht, maar nog
  een beetje stevig"), dus het is te doen, maar voor iemand die de term niet
  kent, zou een korte toevoeging ("kort koken in kokend water") schelen.

### recipes/sauzijcenbroodjes.tex
- **Voorkennis**: "Splits het ei" (stap 3) wordt niet uitgelegd. Een kleine
  toevoeging over hoe je eiwit en eigeel scheidt, zou hier helpen voor wie dit
  nog nooit gedaan heeft.

## Het 'waarom' bij stappen

Vrijwel alle terugkerende patronen (deegrust, aubergine zouten, niet te vol
de pan, droge pan bij spek/chorizo) en losse plekken zijn inmiddels van een
korte reden voorzien. Twee kandidaten voor een bewuste 'verstopte
groente'-truc staan nog open, puur omdat alleen jij weet of dat de echte
reden is:

- **recipes/lahmacun.tex**: paprika, tomaat, rode ui en rode peper worden in
  de keukenmachine fijngemalen tot een pasta in plaats van in stukjes verwerkt
  te blijven. Dat kan puur voor een gelijkmatig beleg zijn, maar het patroon
  lijkt op het tomaten-voorbeeld: fijnmalen zodat structuur en schilletjes
  niet meer opvallen.
- **recipes/bloemkoolpasta.tex**: "Snijd de bloemkool in kleine roosjes" krijgt
  geen reden. Als dat inderdaad is omdat kleine stukjes minder snel worden
  geweigerd, is dat precies het soort context dat de moeite waard is om erbij
  te zetten.

## Basis-ingrediënten versus boodschappen

Is `\ingb` (geen vaste hoeveelheid) alleen gebruikt voor dingen die je toch
al in huis hebt (zout, peper, olie, boter, bloem, kruiden), en niet voor
dingen die je voor dit recept gericht moet inslaan (vlees, vis, kaas, pasta,
rijst, specifieke groente als hoofdbestanddeel)? Bij dat laatste helpt een
hoeveelheid om te weten hoeveel je moet kopen, ook al is de precieze
hoeveelheid in de pan daarna nog steeds op gevoel.

### De duidelijkste gevallen: bijna het hele recept zonder hoeveelheid
- **recipes/tortellini-al-forno.tex**: op ui, courgette, peper en paneermeel
  na staat vrijwel alles als `\ingb`, inclusief de tortellini zelf, de
  spekjes, de ricotta, de parmezaanse kaas en de mozzarella. Voor 5 personen
  weet je hierdoor niet hoeveel pakken tortellini, hoeveel spek of hoeveel
  kaas je moet kopen.
- **recipes/mac-n-cheese.tex**: de varkenslapjes, de geraspte kaas en de melk
  voor de bechamel staan zonder harde hoeveelheid, terwijl dit voor
  5 personen toch hoofdbestanddelen zijn.

### Hoofdingrediënt van het gerecht zonder hoeveelheid
- **recipes/pasta-carbonara.tex** (5 personen): `\ingb{spaghetti (geen verse
  pasta)}`, `\ingb{guanciale (varkenswang) of ongerookt spek}` en
  `\ingb{Parmezaanse kaas, geraspt}` zijn alledrie de kern van het gerecht,
  niet iets wat toevallig in de kast ligt.
- **recipes/pasta-scarapiello.tex** (3 personen): `\ingb{spaghetti of andere
  pasta}` is de enige koolhydraatbron van het gerecht.
- **recipes/pasta-bolognese.tex** (5 personen): `\ingb{pasta naar keuze}` en
  `\ingb{Parmezaanse kaas, geraspt}` (die er "ruim" doorheen gaat) missen
  allebei een richtgewicht.
- **recipes/pizza.tex** (2 pizza's): `\ingb{prosciutto}` en `\ingb{mozzarella}`
  zijn de hoofdtoppings, zonder hoeveelheid weet je niet hoeveel je bij de
  toonbank moet vragen.
- **recipes/quiche-ham-prei.tex** en **recipes/quiche-lorraine.tex**
  (6 porties): `\ingb{hamblokjes}` en de kaas (`witte kaas`/`oude kaas`)
  vormen samen de hele vulling van de quiche, en missen allebei een gewicht.
- **recipes/spinazie-quiche.tex** (5 personen): `\ingb{cherrytomaatjes,
  gehalveerd}` als zichtbare topping en `\ingb{handvol geraspte kaas}` missen
  allebei een aantal/gewicht.
- **recipes/roerbak-kip-cashewnoten.tex** (5 personen): `\ingb{eiernoodles}`
  en `\ingb{kip, in reepjes}` zijn de twee hoofdbestanddelen van het gerecht
  en missen allebei een hoeveelheid.
- **recipes/aardappel-groente-vlees.tex** (5 personen): `\ingb{vlees naar
  keuze: slavink, hamburger, ...}` mag qua soort naar keuze zijn, maar mist
  een aantal (bijvoorbeeld "5 stuks") om te weten hoeveel je moet kopen.
  Ook `\ingb{snackwortels}` is iets wat je gericht inslaat, geen kruidenkast.
- **recipes/gevulde-varkensrollade.tex** (6 personen): `\ingb{spek,
  ongebakken}` en `\ingb{plakken koude prosciutto}` zijn vulling-ingrediënten
  voor de hele rollade, geen kruidenkastartikelen.
- **recipes/broodje-hamburger.tex** (5 personen): `\ingb{sla}` is de enige
  boodschap die nog zonder hoeveelheid staat; voor een krop sla is dat een
  redelijke keuze en geen harde fout.
- **recipes/nasi.tex** (5 personen): `\ingb{pindasaus (pakje of
  zelfgemaakt)}` is een gerichte aankoop, geen kruidenkastitem.
- **recipes/kofta.tex** (5 personen): `\ingb{langkorrelige rijst, volgens
  verpakking}` mist een richtgewicht (bijvoorbeeld "400 g") om te weten
  hoeveel je moet kopen.
- **recipes/flammkuchen.tex** (5 personen): bij de topping honing-geitenkaas
  missen `\ingb{geitenkaas, verkruimeld}` en `\ingb{walnoten, grof gehakt}`
  een indicatie; dit lijkt op de bewust flexibele toppings bij pizza, dus
  een lichte kanttekening in plaats van een harde fout.
- **recipes/ijstaart-karamel.tex** (8-10 personen): `\ingb{karamelsaus
  (zelfgemaakt of uit pot)}` wordt op meerdere momenten in het recept
  gebruikt, een richthoeveelheid (bijvoorbeeld "1 potje, ± 200 g") zou
  hier schelen.

### Grensgevallen, niet aangepast
Een aantal `\ingb`-items lijkt op het eerste gezicht een boodschappenitem,
maar is klein genoeg qua hoeveelheid of duidelijk genoeg "naar smaak" bedoeld
dat het prima blijft staan: verse kruiden als garnering (peterselie,
dille, basilicum), een enkele avocado of lente-ui "wat je in huis hebt"
(fajitas), sauzen en dressings, en het decoratieve `\ingb{eetbare oogjes}`
bij de drollenkoekjes. `recipes/bloemkoolpasta.tex` is met opzet volledig
"op gevoel" (dat staat letterlijk in de meta-regel), dus de spekjes en pasta
daar zijn een bewuste keuze en geen fout.

Bestanden zonder enige `\ingb` (bijvoorbeeld `rode-rijst.tex`) vallen
automatisch buiten deze controle.

## Nieuwste recepten

`burritos.tex` en `pasta-primavera.tex` noemen inmiddels allebei een
pantype (koekenpan resp. hapjespan). Alleen `lasagne-simpel.tex` heeft dat
nog niet: "Verhit de olijfolie in een pan en bak de ui glazig" (stap 2)
noemt geen type. Verder zijn alle drie solide: hoeveelheden kloppen, de oven
wordt op tijd voorverwarmd (`lasagne-simpel.tex` geeft zelfs een
gasovenstand erbij als alternatief), en `pasta-primavera.tex` legt het
waarom van een paar stappen (geen room nodig, pasta zeer al dente koken)
goed uit.
