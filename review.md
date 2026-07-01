# Review — Kookboek Familie Spoor

Doorloop van alle recepten in `recipes/` (61 bij de start van deze review,
inmiddels 71 door latere toevoegingen, zie de update na de rebase verderop),
op zoek naar onduidelijke stappen,
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

## Zelfstandig te volgen: voorverwarmen, zout en vaktermen

Derde controleronde, met als uitgangspunt dat iemand zonder de gedeelde
familiekennis (en zonder iemand om iets te vragen) het recept in één keer
goed moet kunnen doen. Drie punten: verwarmt de oven op tijd voor, is er een
richtlijn voor zout als iemand geen enkel gevoel daarvoor heeft, en wordt
vakjargon gebruikt zonder uitleg terwijl het wel nodig is om te slagen.

### Algemeen: oven­stand nooit vermeld
Door het hele boek heen staat overal alleen een temperatuur in graden, nooit
een stand (boven-onderwarmte, hetelucht, grill). Dat maakt best verschil: een
hetelucht­oven staat vaak zo'n 20°C lager ingesteld dan een oven met
boven-onderwarmte voor hetzelfde resultaat. Dit is geen fout in een los
recept, maar geldt overal, dus misschien is één regel in het voorwoord of bij
de opmaak van het boek (bijvoorbeeld "temperaturen in dit boek zijn voor
boven-onderwarmte, hetelucht ca. 20°C lager") handiger dan het overal apart
te noemen.

### recipes/moussaka.tex
- **Voorverwarmen**: "Verwarm de oven voor op 180\,°C" staat pas in de
  voorlaatste stap, nadat de gehaktsaus, aardappelen, aubergines én
  bechamelsaus al helemaal klaar zijn en de schaal is opgebouwd. Op dat moment
  is er niets meer te doen dan 10 tot 15 minuten wachten tot de oven op
  temperatuur is. Dat had prima eerder gekund, bijvoorbeeld tijdens het bakken
  van de aardappelplakken of de aubergine.

### recipes/risotto.tex
- **Voorverwarmen**: de oven duikt pas op in stap 6, verstopt tussen haakjes:
  "Rooster ondertussen de trostomaatjes in de oven (200\,°C)". Er is nergens
  een eigen "Verwarm de oven voor op..."-instructie. Wie het recept voor het
  eerst maakt, weet niet dat de oven al bij de start aan moet, en staat dan
  alsnog te wachten.

### recipes/pretzels.tex
- **Voorverwarmen**: de oven gaat pas aan in stap 6, op het moment dat de
  pretzels al gevormd zijn en het sodabad ook nog moet koken. Er zijn eerder
  in het recept meerdere rusttijden (samen zo'n anderhalf uur) waarin de oven
  had kunnen opwarmen. Niet dramatisch, maar een kleine tijdswinst die nu blijft
  liggen.

### recipes/lekkerbekjes-kroketjes-sla.tex
- **Voorverwarmen**: er staat nergens een expliciete "verwarm de oven voor",
  alleen "Bereid de aardappelkroketjes in de oven volgens de aanwijzingen op
  de verpakking" (stap 2). Logisch omdat het per merk verschilt, maar iemand
  die niet gewend is zelf te koken denkt er dan misschien niet aan om de oven
  eerst op te laten warmen voor hij begint.

### recipes/quiche-groente-geitenkaas.tex
- **Zout/kruiden**: stap 4 zegt "Breng flink op smaak met zout", maar zout
  staat nergens in het Ingrediënten-blok van de vulling (alleen in het deeg,
  voor iets anders). Iemand zonder kookervaring weet hierdoor niet eens dat
  hij zout in huis moet hebben voor de vulling, laat staan hoeveel.

### recipes/bloemkoolquiche.tex, recipes/quiche-lorraine.tex, recipes/quiche-ham-prei.tex, recipes/quiche-groente-cirkel.tex
- **Voorkennis**: bij het voorbakken van de bodem ("Voorbakken: bak de bodem
  15 minuten") wordt nergens gezegd dat je de bodem moet inprikken met een
  vork of met bakbonen/gewichtjes moet vullen. Zonder dat kan de bodem tijdens
  het voorbakken opbollen. Dit geldt voor bijna alle quiches met hetzelfde
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

De overige recepten verwarmen de oven ruim op tijd voor (vaak al in de eerste
of tweede stap, terwijl er ondertussen nog gesneden of gemengd wordt), geven
bij zout en kruiden ofwel een hoeveelheid ofwel het geaccepteerde
`\ingb{...}` + "naar smaak"-patroon, en gebruikte vaktermen (vlindermethode,
holy trinity, blancheren bij andere recepten) worden daar wel meteen kort
toegelicht.

## Het 'waarom' bij stappen

Vierde controleronde: op veel plekken staat een techniek zonder de reden
erachter, terwijl juist dat 'waarom' een recept persoonlijk en leerzaam
maakt (zoals de `\tip{}`'s die er al zijn: "niet te lang stampen, want dat
wordt papperig"). Let op: hieronder staat steeds alleen dat de reden
ontbreekt, niet wat de reden is. Dat weet alleen jij. Op de meeste plekken
gaat het om technische redenen (structuur, vocht, textuur), maar op een paar
plekken lijkt een stap op iets wat je zelf in het voorbeeld noemde: een
bewuste truc om iets in kleine, onopvallende stukjes te verwerken.

### De twee sterkste kandidaten voor een 'verstopte groente'-verhaal
- **recipes/lahmacun.tex**: paprika, tomaat, rode ui en rode peper worden in
  de keukenmachine fijngemalen tot een pasta in plaats van in stukjes verwerkt
  te blijven. Dat kan puur voor een gelijkmatig beleg zijn, maar het patroon
  lijkt op je tomaten-voorbeeld: fijnmalen zodat structuur en schilletjes niet
  meer opvallen.
- **recipes/bloemkoolpasta.tex**: "Snijd de bloemkool in kleine roosjes" krijgt
  geen reden. Als dat inderdaad is omdat kleine stukjes minder snel worden
  geweigerd, is dat precies het soort context dat de moeite waard is om erbij
  te zetten.

### Terugkerend patroon: waarom het deeg moet rusten
Bij zes recepten met (bijna) hetzelfde deeg staat de rusttijd erbij zonder
reden (gluten die ontspant, boter die weer koud wordt, minder krimp bij het
bakken): `bloemkoolquiche.tex`, `quiche-lorraine.tex`, `quiche-ham-prei.tex`,
`quiche-groente-cirkel.tex`, `quiche-chorizo-geitenkaas.tex`,
`quiche-groente-geitenkaas.tex`, plus `spinazie-quiche.tex`, `pita.tex` en
`basiskoekjes.tex` met hun eigen deeg. Omdat het bijna steeds dezelfde reden
is, kan die één keer goed worden opgeschreven (bijvoorbeeld in de tip bij het
basisdeeg) in plaats van in elk bestand apart.

### Terugkerend patroon: waarom je aubergine eerst zout
`recipes/parmigiana-melanzane.tex` en `recipes/pasta-alla-norma.tex` zouten
de aubergineplakken en laten ze 10 minuten staan voor het bakken, zonder te
zeggen waarom (vocht en bitterheid eruit trekken, zodat de plakken bij het
bakken niet soggy worden). `recipes/moussaka.tex` bakt de aubergine juist
zonder dit zout-stapje, wat de vraag oproept of dat bewust anders is of een
gemiste stap.

### Terugkerend patroon: waarom niet te veel tegelijk in de pan
`recipes/parmigiana-melanzane.tex` en `recipes/pasta-alla-norma.tex` zeggen
"werk in porties/batches" zonder te zeggen waarom (te vol de pan betekent
stomen in plaats van bruinen). `recipes/fajitas.tex` heeft hetzelfde punt bij
het bakken van de kipblokjes, zonder het woord batches te gebruiken.

### Terugkerend patroon: waarom een droge pan bij spek of chorizo
`recipes/mini-aardappel-quiches.tex` en `recipes/quiche-chorizo-geitenkaas.tex`
bakken spek of chorizo in een "droge pan" zonder te zeggen dat dit kan omdat
het vlees genoeg eigen vet loslaat. `recipes/pasta-chorizo-andijvie.tex` legt
dit wel uit in de tip, dat zou een mooi voorbeeld zijn om elders te hergebruiken.

### Losse plekken die het vermelden waard zijn
- **recipes/broodje-hamburger.tex**: uien op laag vuur met een scheutje water
  langzaam karamelliseren, zonder te zeggen waarom laag vuur en water nodig
  zijn (voorkomt verbranden voor de uien zoet en zacht zijn).
- **recipes/pizza.tex**: "kneed minstens 10 minuten, dit is het belangrijkste
  deel van het recept" zegt wel dát het belangrijk is, niet waarom
  (glutenontwikkeling voor een luchtige korst). Ook het uitlekken van de
  tomatensaus en de mozzarella krijgt geen reden (voorkomt een natte bodem).
- **recipes/pasta-blauwe-kaas.tex**: champignons op hoog vuur bakken zonder te
  zeggen dat dit is om ze te laten bruinen in plaats van vocht te laten lossen.
- **recipes/risotto.tex** (tomaten-pesto): de tomaten in twee fasen toevoegen
  en de risotto na de boter en kaas een paar minuten laten rusten (het
  klassieke "mantecare"-moment) krijgen geen van beide een reden.
- **recipes/tortellini-al-forno.tex**: kookvocht apart houden voor de saus
  wordt wel genoemd, maar niet waarom dat helpt (het zetmeel bindt de saus).
- **recipes/tompouce-geitenkaas.tex**: bladerdeeg inprikken met een vork
  zonder te zeggen dat dit te sterk opbollen voorkomt.
- **recipes/moussaka.tex**: het gehakt door een zeef gieten om vet af te
  gieten, en de melk apart verwarmen "niet laten koken" voor de bechamel,
  krijgen allebei geen reden (minder vet, geen klontjes).
- **recipes/spruitenstamp.tex**: de aardappelen laten "droogstomen" zonder te
  zeggen dat dit een romigere stamp geeft in plaats van een waterige.
- **recipes/roti.tex**: krieltjes "bijna gaar" voorkoken en sperziebonen
  bewust knapperig houden, allebei zonder reden (ze garen door in de saus,
  blijven fris naast de zachte vulling).
- **recipes/couscous.tex** en **recipes/bobotie.tex**: respectievelijk het
  laten staan onder een deksel (couscous gaart door de hete, opgenomen
  vloeistof) en het voorkoken van de sperziebonen krijgen geen toelichting.
- **recipes/asperge-lasagne.tex**: het stukje onderkant van de asperge
  afsnijden zonder te zeggen dat dat het houtige, taaie stuk is.
- **recipes/kofta.tex**: de worstjes eerst apart bruin bakken en later
  teruglengen in de saus, zonder te zeggen waarom (kleur en smaak zonder ze
  meteen gaar te stoven).

Veel andere recepten doen dit juist al goed: de tips bij onder andere
pasta carbonara (kookvocht, restwarmte), pannenkoeken (rusttijd beslag),
gevulde varkensrollade (rusten na braden), parmigiana-melanzane (geschilde
aubergine voor kinderen) en nasi (rijst van een dag oud) leggen het waarom
al helder uit. Dat is precies het niveau dat de rest van het boek ook zou
kunnen halen.

## Update na rebase: acht nieuwe recepten

De branch is opnieuw op `main` gebaseerd. Daarbij kwamen 8 nieuwe recepten
mee die nog niet eerder gecontroleerd waren: `roerbak-kip-cashewnoten.tex`,
`kip-madras.tex`, `couscous-feta-rozijnen.tex`, `gnocchi-broccoli.tex`,
`pastinaaksoep.tex`, `pide.tex`, `basismuffins.tex` en `pasta-bolognese.tex`.
De overige recepten waren ongewijzigd, dus de bevindingen hierboven staan
nog overeind. Deze acht zijn nu alsnog langs alle eerdere controles gehaald:

### recipes/pide.tex
- **Vage hoeveelheid**: de vulling gehakt-tomaat gebruikt 5 el olijfolie om
  250 g gehakt te bakken, terwijl de vulling spinazie-feta voor een
  vergelijkbare hoeveelheid groente maar 1 el gebruikt. Dat verschil is groot
  genoeg om een tikfout te vermoeden.
- **Zout/kruiden**: de vulling gehakt-tomaat heeft nergens zout of peper,
  niet in de ingrediëntenlijst en niet in de stappen, terwijl de vulling
  spinazie-feta dat wel expliciet heeft (`\ingb{zout en peper}`).
- **Waarom**: het deeg moet 1 tot 1,5 uur rijzen zonder dat er een reden bij
  staat (zelfde terugkerende patroon als bij de andere deegrecepten). De tip
  over rusten na het bakken is wel weer een goed voorbeeld van een
  toegelichte reden.

### recipes/basismuffins.tex
- **Voorverwarmen**: de oven wordt pas in de laatste stap genoemd ("Bak de
  muffins 20 minuten op 200\,°C"), nadat het beslag al helemaal klaar is.
  Het mengen kost weinig tijd, dus dit weegt lichter dan bijvoorbeeld
  moussaka, maar het kost nog steeds een paar minuten onnodig wachten.
- **Positief voorbeeld**: dit is het enige recept in het hele boek dat de
  ovenstand vermeldt ("boven- en onderwarmte"). Dat is precies de aanvulling
  die eerder als algemeen verbeterpunt is genoemd, hier al goed gedaan.

### recipes/pasta-bolognese.tex
- **Overig**: `\ingb{peper en zout}` staat in de ingrediëntenlijst, maar
  wordt in geen enkele stap expliciet genoemd (het zout komt alleen impliciet
  binnen via het bouillonblokje). Klein, geen echt probleem.
- **Positief voorbeeld**: dit recept legt bijna overal het waarom uit (de rol
  van de soffrito, waarom tomatenpuree eerst gebakken wordt, waarom de wijn
  moet inkoken, waarom de saus in porties de vriezer in gaat) en specificeert
  het pantype (hapjespan of hoge pan). Een van de sterkst geschreven
  recepten van het boek op dit vlak.

### recipes/pastinaaksoep.tex
- **Olie**: "2 el olie" zonder soort, dat is de enige keer dat dit in dit
  recept voorkomt en de rest van het boek noemt bijna altijd olijfolie of
  zonnebloemolie.

### recipes/gnocchi-broccoli.tex
- **Waarom**: het spek wordt in een "droge koekenpan" gebakken zonder te
  zeggen dat dit kan omdat het spek genoeg eigen vet heeft. Klein punt.

### recipes/couscous-feta-rozijnen.tex
- Geen problemen van betekenis. De inleiding legt zelfs al uit waarom de feta
  apart gehouden kan worden voor kinderen die nog aan de smaak moeten wennen,
  precies het soort 'waarom' dat elders in het boek gemist wordt.

De overige twee nieuwe recepten (`roerbak-kip-cashewnoten.tex` en
`kip-madras.tex`) hebben vooral bevindingen op het gebied van basis- versus
boodschappen-ingrediënten, zie de sectie hieronder.

## Basis-ingrediënten versus boodschappen

Vijfde controleronde, over het hele boek (inclusief de acht nieuwe recepten):
is `\ingb` (geen vaste hoeveelheid) alleen gebruikt voor dingen die je toch
al in huis hebt (zout, peper, olie, boter, bloem, kruiden), en niet voor
dingen die je voor dit recept gericht moet inslaan (vlees, vis, kaas, pasta,
rijst, specifieke groente als hoofdbestanddeel)? Bij dat laatste helpt een
hoeveelheid om te weten hoeveel je moet kopen, ook al is de precieze
hoeveelheid in de pan daarna nog steeds op gevoel.

### De duidelijkste gevallen: bijna het hele recept zonder hoeveelheid
- **recipes/tortellini-al-forno.tex**: op peper en paneermeel na staat vrijwel
  alles als `\ingb`, inclusief de tortellini zelf, de spekjes, de courgette,
  de ricotta, de parmezaanse kaas en de mozzarella. Voor 5 personen weet je
  hierdoor niet hoeveel pakken tortellini, hoeveel spek of hoeveel kaas je
  moet kopen.
- **recipes/mac-n-cheese.tex**: de macaroni (`\ingb{1 flink gevulde kop
  macaroni}`), de varkenslapjes, de geraspte kaas en de melk voor de
  bechamel staan allemaal zonder harde hoeveelheid, terwijl dit voor
  5 personen toch de hoofdbestanddelen zijn.

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
- **recipes/gevulde-varkensrollade.tex** (6 personen): `\ingb{spek of
  prosciutto, gebakken en verkruimeld}` en `\ingb{bladspinazie}` zijn beide
  vulling-ingrediënten voor de hele rollade, geen kruidenkastartikelen.
- **recipes/lekkerbekjes-kroketjes-sla.tex** (5 personen):
  `\ingb{aardappelkroketjes uit de oven}` is samen met de kibbeling het
  hoofdgerecht, en mist een aantal of een zakmaat.
- **recipes/broodje-hamburger.tex** (5 personen): `\ingb{sla}`, `\ingb{tomaat}`
  en `\ingb{plakjes kaas}` zijn concrete boodschappen voor 5 broodjes, geen
  kruidenkastartikelen.
- **recipes/nasi.tex** (5 personen): `\ingb{pindasaus (pakje of
  zelfgemaakt)}` is een gerichte aankoop, geen kruidenkastitem.
- **recipes/kofta.tex** (5 personen): `\ingb{rijst, volgens verpakking}` mist
  een richtgewicht (bijvoorbeeld "400 g") om te weten hoeveel je moet kopen.
- **recipes/flammkuchen.tex** (5 personen): bij de topping honing-geitenkaas
  missen `\ingb{geitenkaas, verkruimeld}` en `\ingb{walnoten, grof gehakt}`
  een indicatie; dit lijkt op de bewust flexibele toppings bij pizza, dus
  een lichte kanttekening in plaats van een harde fout.
- **recipes/ijstaart-karamel.tex** (8-10 personen): `\ingb{karamelsaus
  (zelfgemaakt of uit pot)}` wordt op meerdere momenten in het recept
  gebruikt, een richthoeveelheid (bijvoorbeeld "1 potje, ± 200 g") zou
  hier schelen.

### Macro verkeerd gekozen, hoeveelheid staat er eigenlijk al
- **recipes/kip-madras.tex**: `\ingb{1 kipfilet, in stukken}` heeft het
  aantal al in de tekst staan, maar is toch als `\ingb` genoteerd in plaats
  van `\ing{1}{kipfilet, in stukken}`. Zelfde slordigheidje als eerder bij
  de tomaten in `kofta.tex`.

### Grensgevallen, niet aangepast
Een aantal `\ingb`-items lijkt op het eerste gezicht een boodschappenitem,
maar is klein genoeg qua hoeveelheid of duidelijk genoeg "naar smaak" bedoeld
dat het prima blijft staan: verse kruiden als garnering (peterselie,
dille, basilicum), een enkele avocado of lente-ui "wat je in huis hebt"
(fajitas), sauzen en dressings, en het decoratieve `\ingb{eetbare oogjes}`
bij de drollenkoekjes. `recipes/bloemkoolpasta.tex` is met opzet volledig
"op gevoel" (dat staat letterlijk in de meta-regel), dus de spekjes en pasta
daar zijn een bewuste keuze en geen fout.

Bestanden zonder enige `\ingb` (bijvoorbeeld `jambalaya.tex`,
`sauzijcenbroodjes.tex`, `risotto.tex`, `rode-rijst.tex`) vallen automatisch
buiten deze controle.
