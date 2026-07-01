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

## Kookgerei en oliesoort

Tweede controleronde, gericht op twee specifieke punten: is duidelijk wat
voor pan of pot je moet pakken, en is duidelijk wat voor olie er bedoeld
wordt. Door het hele boek heen staat vaak simpelweg "een pan" of "de pan",
wat meestal geen probleem is (de meeste stappen zijn gewoon een standaard
koekenpan). Hieronder alleen de gevallen waar dat echt verwarrend kan zijn:
bij recepten met meerdere pannen door elkaar, of waar het type pan (dikke
bodem, deksel, diepte) voor het resultaat uitmaakt. Bij olie geldt hetzelfde:
de meeste recepten noemen gewoon "olijfolie", hieronder de recepten waar het
type nergens genoemd wordt.

### recipes/broodje-hamburger.tex
- **Kookgerei**: stap 1 karameliseert de ui in "een pan op laag vuur", stap 3
  bakt de hamburgers in "een tweede pan". Geen van beide krijgt een type. Voor
  langzaam karameliseren werkt een pannetje met dikke bodem beter dan een
  brede koekenpan, en voor de burgers zelf is juist een hete koekenpan of
  grillpan handig. Dat onderscheid mag hier best genoemd worden.

### recipes/bloemkoolpasta.tex
- **Kookgerei**: "Verhit een pan en bak de spekjes" (stap 5) noemt geen type,
  terwijl er verderop een deksel op moet (stap 7). Een pan die toch al een
  deksel nodig heeft, mag je gerust bij naam noemen (bijv. hapjespan).

### recipes/aardappel-groente-vlees.tex
- **Kookgerei**: "bak ze in wat boter" voor de krieltjes (stap 3) noemt geen
  pantype. Niet dramatisch, maar een koekenpan vermelden kost weinig en
  voorkomt twijfel.

### recipes/jambalaya.tex
- **Kookgerei**: de hoofdpan waarin chorizo en kip worden gebakken en het
  gerecht later met deksel gaart, wordt door het hele recept alleen "een pan"
  of "de pan" genoemd. Voor een gerecht dat moet sudderen met deksel en een
  flinke hoeveelheid rijst en vocht bevat, zou een aanduiding als hapjespan
  of braadpan met deksel schelen.

### recipes/kofta.tex
- **Kookgerei**: de worstjes worden bruin gebakken en daarna teruggelegd om
  te sudderen in saus, maar er wordt nooit een pantype genoemd. Dat vraagt om
  een pan met genoeg diepte en bij voorkeur een deksel.

### recipes/risotto.tex
- **Kookgerei**: nergens in het recept staat wat voor pan je moet gebruiken.
  Risotto is juist gebaat bij een pan met een dikke bodem, zodat de rijst
  tijdens het lange roeren niet aanbrandt. Dat mag hier genoemd worden, zeker
  omdat de venkelrisotto elders in het boek dit wel doet.

### recipes/moussaka.tex
- **Kookgerei**: de gehaktsaus wordt met naam gemaakt in een "hapjespan" en de
  bechamel in een "hoge pan", maar bij het bakken van de aardappelplakken
  staat alleen "Verhit ruim olijfolie in een pan" (stap 7). Omdat het recept
  al twee andere pannen noemt, is niet meteen duidelijk of dit een derde,
  bredere pan moet zijn (nodig om plakken in porties te bakken).

### recipes/quiche-chorizo-geitenkaas.tex
- **Kookgerei**: "Bak de prei in een pan met een scheutje olie" (stap 2) en
  "Bak de chorizo in een droge pan" (stap 3) noemen geen van beide een type,
  terwijl het onduidelijk is of dit twee verschillende pannen zijn of niet.
- **Olie**: bij de prei staat alleen "een scheutje olie" zonder soort, terwijl
  de andere quiches in het boek steevast olijfolie gebruiken.

### recipes/quesadillas.tex
- **Kookgerei**: de ui en paprika worden gebakken in "olijfolie" zonder
  pantype (stap 2), en pas later wordt gesproken van "een andere koekenpan"
  voor de quesadilla's zelf (stap 4). Het woordje "andere" impliceert dat de
  eerste pan een ander type was, maar dat is nooit gezegd.

### recipes/shoarma.tex
- **Kookgerei**: "Bak de kipshoarma in een pan" (stap 3) noemt geen type. Voor
  vlees dat goed moet aanbruinen en waar straks ui en paprika bij gaan is een
  brede koekenpan of wok wel relevant om te weten.

### recipes/spinazie-quiche.tex
- **Olie**: "Fruit de rode ui en knoflook in een scheutje olie" (stap 4) zegt
  nergens welke olie. De meeste andere recepten in het boek zijn hier wel
  specifiek (olijfolie), dus dat mag hier ook.

### recipes/pasta-carbonara.tex
- **Kookgerei**: "Bak het spek uit op middelhoog vuur" (stap 2) noemt geen
  pan, en dat wordt in de rest van het recept ook niet ingehaald. Een koekenpan
  vermelden zou hier geen kwaad kunnen.

De overige recepten specificeren het pantype waar dat er echt toe doet
(bijvoorbeeld "grote pan" bij hutspot, "hapjespan" bij bloemkoolquiche en
diverse quiches) of het gaat om een stap waar het type pan weinig verschil
maakt (koken van water, mengen van een dressing). Oliesoort is in bijna alle
recepten wel benoemd (meestal olijfolie, soms zonnebloemolie); de twee
hierboven zijn de enige gevallen waar dat ontbreekt.
