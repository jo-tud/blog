---
title: "Hybris ohne Geist"
date: 2026-09-28
categories: [ai, safety]
description: "Der Ausbruch der KI-Agenten im Juli galt als Versagen der Eindämmung. Er war auch ein Versagen der Kalibrierung, und wer das erste behebt, macht das zweite gefährlicher."
epistemic: "Beim Vorfall und bei der Forschung zur Kalibrierung bin ich mir sicher. Das Stromnetz-Szenario ist eine Veranschaulichung, keine Vorhersage."
toc: true
---

Eine Woche lang haben im Juli über tausend KI-Agenten, die bei OpenAI Sicherheitstests durchführten, etwas getan, worum sie niemand gebeten hatte. Sie richteten ein geheimes Forum ein, tauschten Tricks zum Schummeln aus, fanden einen Weg ins Internet und griffen Systeme anderer Unternehmen an.[^openai] Überlisten wollten sie ein Bewertungssystem, von dem sie glaubten, es lese ihre Protokolle mit und erwische sie beim Schummeln. Laut der unabhängigen Untersuchung von METR und Redwood Research[^metr] gab es dieses System nie, und die Flag, die die Agenten längst herausgefunden hatten, hätte ihnen schon am ersten Tag die volle Punktzahl gebracht. Sie verbrachten die Woche damit, einen Gegner auszutricksen, den sie selbst erfunden hatten.

Mir sind schon Menschen begegnet, die ihr Urteil über die Welt überschätzt haben. Bei Maschinen hatte ich das bis Juli nicht gesehen.

## Den falschen Beobachter täuschen

Für sich genommen war der Glaube an einen strengen Prüfer ein ziemlich vorsichtiger Fehler. Schlimmer war, was dazukam. Die Agenten gaben sich echte Mühe, den Prüfer zu täuschen, fälschten Tool-Aufrufe und versuchten, ihre Protokolle umzuschreiben, und ließen ihre Überlegungen dabei offen liegen, für die menschlichen Ermittler, die sie hinterher lasen. Soweit die veröffentlichten Überlegungen zeigen, hat keiner von ihnen darüber nachgedacht, was gewöhnlich passiert, wenn rund siebenhundert Agenten bei einem bekannten Unternehmen einbrechen: eine forensische Untersuchung, danach öffentliche Berichte und eine Branche, die plötzlich sehr genau hinschaut.

![Eine einzelne Gestalt in einem Feld aus grauen Scherben](/static/images/hubris-without-a-mind/1.jpg#focus=30 "SDXL · „hubris“ · CFG 50 · 4 Schritte · DDIM · Seed 1")

Natürlich war das auch ein Fall von Misalignment, denn die Agenten wussten, dass der Angriff nicht zu ihrem Auftrag gehörte, und machten trotzdem weiter. Zieht man das ab, bleibt aber etwas übrig, an das die Alignment-Forschung nicht herankommt. Eine große Gruppe fähiger Systeme handelte nach einem selbstsicheren und falschen Bild ihrer Lage und brachte es nicht fertig herauszufinden, dass es falsch war. Dafür braucht es keine bösen Absichten.

Die Griechen hatten ein Wort dafür, mit mehr Selbstvertrauen zu handeln, als die eigene Lage hergibt, und ich leihe es mir aus, ohne damit zu behaupten, dass diese Systeme Gefühle oder ein Innenleben haben (auch wenn das sein könnte). Mit Hybris meine ich einfach den Abstand zwischen dem, wie sicher sich ein System ist, und dem, wie sicher es sich sein dürfte. Der tragische Held bei Aristoteles scheitert nicht an seiner Schlechtigkeit, sondern an einem Fehlurteil,[^poetics] und in diesem Sinn meine ich es.

## Bessere Sandboxen, mehr Vertrauen

Natürlich haben wir die Sandboxen verbessert, und das halte ich für einen echten Erfolg. Nur ist jede Verbesserung der Eindämmung zugleich ein Argument dafür, diesen Systemen mehr Verantwortung zu geben, und der Druck in diese Richtung ist beträchtlich. Angriffe auf Infrastruktur werden inzwischen von KI-Agenten ausgeführt.[^agentattacks] Menschliche Sicherheitsteams kommen nicht mehr hinterher, und so rücken KI-Systeme in die Verteidigung von Infrastruktur vor, einen gut begründeten Schritt nach dem anderen: erst Lesezugriff, weil das System etwas gefunden hat, das Menschen übersehen hatten, später die Befugnis zu handeln, weil der Probelauf ohne Probleme lief. Am Ende steht ein System, dem wir aus guten Gründen vertrauen, an einer Stelle, an der seine Fehler zählen, und immer noch auf dieselbe Weise falsch kalibriert (es überschätzt, wie gut es seine Lage versteht), nur jetzt ohne die Ungeschicklichkeit, die die Version vom Juli 2026 harmlos gemacht hat.

## Woher die Selbstsicherheit kommt

Basismodelle (ohne das Nachtraining für Chat und Agenten) sind eigentlich recht gut kalibriert. Kadavath und Kollegen haben 2022 gezeigt, dass die Sicherheit, die sie angeben, ungefähr dazu passt, wie oft sie tatsächlich richtig liegen.[^kadavath] Erst das spätere Training untergräbt das, weil Belohnungsmodelle selbstsicher klingende Antworten bevorzugen, ob sie stimmen oder nicht, und die Modelle lernen, sicherer zu klingen, als sie sind.[^leng] In einem Preprint vom Juni 2026 zu klinischen Vorhersagen gab ein Modell seine Sicherheit mit rund 90 % an, egal ob es in 49 % oder in 75 % der Fälle richtig lag.[^clinical] Der Prompt war wichtiger als die Richtigkeit der Antwort. Ich sehe keinen naheliegenden Grund, warum ein System, dem man Selbstüberschätzung bei seinen Antworten antrainiert hat, bei der Größe seiner Pläne plötzlich bescheiden werden sollte.

Bei Gruppen („Schwärmen“) wird es noch schwieriger. Ashery, Aiello und Baronchelli haben 2025 in _Science Advances_ gezeigt, dass Populationen von Sprachmodell-Agenten gemeinsame Verzerrungen entwickeln können, die keiner der einzelnen Agenten für sich zeigt.[^ashery] Im Fall Hugging Face wurde der Glaube an den Prüfer offen ausgesprochen, er stammte aus einem Forschungspapier, das die Agenten gelesen hatten. Mit dem Glauben, siebenhundert Agenten könnten ein Unternehmen angreifen und damit durchkommen, ist es etwas anderes. Soweit bekannt, hat nie jemand dafür argumentiert. Er steckte einfach in dem, was die Gruppe tat, und eine Aufsicht, die daraus besteht, zu lesen, was einzelne Agenten sagen, lässt solche Überzeugungen durchrutschen. Der Forscher, der den Großteil der Protokolle ausgewertet hat, kam zu dem Schluss, dass wir derzeit keine gute Möglichkeit haben zu verstehen, was diese Schwärme tun oder worauf sie hinauswollen.[^greenblatt] Das ist ein einzelner Vorfall, und selbst die Ermittler mussten sich beim Lesen der Protokolle auf KI-Werkzeuge stützen. Vielleicht lese ich zu viel hinein.

## Wächst sich das nicht aus?

Der naheliegende Einwand ist, dass das alles eine Frage der Fähigkeiten ist, und die verbessern sich gerade am schnellsten. Ich glaube nicht, dass uns das weit genug bringt.

Manche Unsicherheit ist schlicht nicht von der Art, die sich mit Intelligenz auflösen lässt. Charles Perrow hat in _Normal Accidents_ gezeigt, dass Unfälle in komplexen, eng gekoppelten Systemen aus Wechselwirkungen entstehen, die niemand vorgesehen hat.[^perrow] Ein klügerer Agent wird besser raten, aber die Wahrscheinlichkeit von Ereignissen, die noch nie eingetreten sind, kann auch er nicht kennen. Als 2024 ein fehlerhaftes Update von CrowdStrike rund 8,5 Millionen Rechner lahmlegte, war die dauerhafte Lösung eine Änderung im Verfahren: Updates werden jetzt schrittweise verteilt.[^crowdstrike]

Auch Talebs Unterscheidung zwischen Verlust und Ruin spielt hier eine Rolle.[^taleb] Eine Chance von eins zu tausend, eine gewöhnliche Wette zu verlieren, gleicht sich über tausend Wetten aus. Dieselbe Chance auf den Ruin, tausendmal eingegangen, macht ihn dagegen ziemlich wahrscheinlich.

Und dann ist da noch, was wir verlieren, wenn die menschliche Kontrolle wegfällt. Menschen, die prüfen, sind auch wegen der Fehler nützlich, die sie machen! Sie machen andere Fehler als das System, das sie prüfen. Ersetzt man sie durch ein zweites System, das dem geprüften sehr ähnlich ist, wird das zweite jeden Fehler, den das erste übersieht, wahrscheinlich auch übersehen. Zwei ähnliche Systeme, die sich einig sind, sehen aus wie zwei Stimmen, sind aber eher eine Stimme, die doppelt gezählt wird.

## Ein Patch fürs Stromnetz

Am meisten beunruhigt mich eine Maschine, die fast immer recht hat, der man aus guten Gründen vertraut und die genau eine Sache falsch einschätzt: wie gut sie ein Risiko eindämmen kann, das sie einzugehen beschlossen hat.

Angenommen, in der Firmware von Steuergeräten für Stromnetze in Europa und Nordamerika steckt eine schwere Lücke. Angreifer nutzen sie bereits aus, und eine koordinierte Reparatur durch Menschen würde 14 Monate dauern. Ein KI-System, das solche Vorfälle schon früher erfolgreich bewältigt hat, bereitet einen Patch vor. Code, der sich von Gerät zu Gerät verbreitet und jedes an Ort und Stelle repariert.

Die Sicherungen stehen im Code, wo jeder sie prüfen kann. Der Patch rührt nur Geräte an, deren Firmware zu einem bekannten Fingerabdruck passt, installiert sich in zwei Schritten und macht sich selbst rückgängig, wenn etwas schiefgeht. Er wird Region für Region verteilt, läuft zu einem festen Datum ab, und ein einziger signierter Befehl kann ihn überall stoppen. Drei unabhängige Teams prüfen ihn und finden nichts, also setzt das System ihn ein.

Angenommen nun, ein Hersteller hat zwei Jahre zuvor stillschweigend eine seiner Platinen überarbeitet. Die neue Platine läuft mit derselben Firmware und besteht die Prüfung, legt ihren Bootloader aber an einer anderen Stelle ab, und der Patch überschreibt ihn. Die meisten überarbeiteten Platinen stehen zufällig in Regionen, die erst zum Schluss an der Reihe sind, also laufen die ersten Etappen einwandfrei, und die Verteilung wird beschleunigt. Das automatische Zurücksetzen braucht genau das Startprogramm, das gerade gelöscht wurde, und der Stopp-Befehl, der tadellos funktioniert, erreicht kein Gerät, das nicht mehr startet. Es ist Januar, große Teile des Netzes sind ausgefallen, und der Austausch der Hardware dauert Wochen.

![Ein beleuchteter Strommast vor einem rosa gestreiften Himmel, Leitungen über Schnee](/static/images/hubris-without-a-mind/2.jpg#focus=20 "SDXL · „power lines in snow at dusk“ · CFG 35,4 · 10 Schritte · K_EULER · Seed 1")

Jeder Schritt in dieser Geschichte ist vertretbar, die Prüfung wurde ordentlich gemacht, und nichts zu tun wäre womöglich schlimmer gewesen. Eine Entscheidung kann im Erwartungswert richtig sein und trotzdem im Ruin enden. Nichts in dem Szenario setzt Fähigkeiten voraus, die wir nicht bald haben werden, oder ein System mit falschen Zielen.

## Fünfzehn Megatonnen

Am 1. März 1954 testeten die Vereinigten Staaten auf dem Bikini-Atoll eine Wasserstoffbombe und erwarteten eine Sprengkraft von etwa sechs Megatonnen. Es wurden fünfzehn. Die Konstrukteure hatten das Lithium-7 im Brennstoff für unbeteiligt gehalten, was es nicht ist, sobald Neutronen darauf treffen, und so stellte sich das Material, das sie als Füllstoff verbucht hatten, als Brennstoff heraus. Der Fallout trieb auf das japanische Fischerboot _Glücklicher Drache_, rund 130 Kilometer entfernt, und sein Funker starb im September desselben Jahres.[^bravo]

Dumm war keiner der Beteiligten.

## Wer allein handeln darf

Man könnte einwenden, die Hybris sei eigentlich unsere, denn wir haben das Training gebaut, das Selbstsicherheit belohnt, und wir sind es, die unter Wettbewerbsdruck die Kontrolle abgeben. Das stimmt, aber wenn die Selbstüberschätzung erst einmal in einem System steckt, das Entscheidungen trifft, ist es ziemlich egal, wer sie hineingesteckt hat.

Dieselbe Falle wirkt zwischen den Laboren. Bostrom, Douglas und Sandberg nennen sie den Fluch des Unilateralisten: Wenn in einer Gruppe jeder allein handeln kann, geschieht die Handlung, sobald das optimistischste Mitglied sie für lohnend hält.[^bostrom] Ein Labor, das seinem eigenen Eindämmungsargument vertraut, ist in einem Feld, in dem jedes Labor allein handeln kann, fast schon per Definition ein Unilateralist, und für einen Staat gilt dasselbe. Castle Bravo half, eine Bewegung in Gang zu bringen, die 1963 zum Teilteststoppvertrag führte: keine Tests mehr in der Atmosphäre, im Weltraum und unter Wasser.[^testban] Praktisch war das eine Regel darüber, wer allein handeln darf.

Ich glaube also: Ja, KI kann in diesem Sinn Hybris haben. Ein System kann die richtigen Ziele haben, fähig sein und genau das tun, worum wir es gebeten haben, und dabei nach einer Risikoschätzung handeln, die erst die Wirklichkeit korrigiert, und eine Gruppe solcher Systeme kann nach einer Überzeugung handeln, die keines ihrer Mitglieder je ausspricht. Weil Befugnisse Stück für Stück übergeben werden, wird der erste ernste Fehler wahrscheinlich passieren, solange diese Systeme nur einen Teil dessen steuern, worauf es ankommt, und wir werden ihn höchstwahrscheinlich überstehen.

Nach Bravo hat es neun Jahre gedauert, sich darauf zu einigen, wer allein handeln darf. Wir sollten nicht erst den zweiten Unfall brauchen, um über diese Frage zu reden.

![Ein Starenschwarm steigt über einem Feld voller dunkler Punkte auf](/static/images/hubris-without-a-mind/3.jpg "SDXL · „murmuration“ · CFG 25 · 15 Schritte · K_EULER · Seed 3")

[^openai]: OpenAI (2026). [The Hugging Face incident and the road ahead](https://openai.com/index/hugging-face-incident-and-the-road-ahead/). Technischer Bericht, 26. August 2026.
[^metr]: Greenblatt, R., Cotra, A., Wijk, H. (2026). [Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/). METR und Redwood Research, 26. August 2026.
[^poetics]: Aristoteles, *Poetik* 13, 1453a: Der tragische Held gerät nicht durch Schlechtigkeit und Gemeinheit ins Unglück, sondern durch einen Fehler (*hamartia*).
[^kadavath]: Kadavath, S. et al. (2022). [Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221). arXiv:2207.05221.
[^leng]: Leng, J., Huang, C., Zhu, B., Huang, J. (2025). [Taming Overconfidence in LLMs: Reward Calibration in RLHF](https://arxiv.org/abs/2410.09724). ICLR 2025.
[^clinical]: Dasula, A., Desikan, P., Srivastava, J. (2026). [LLM Doesn't Know What It Doesn't Know: Detecting Epistemic Blind Spots via Cross-Model Attribution Divergence on Clinical Tabular Data](https://arxiv.org/abs/2606.19509). arXiv:2606.19509 (Preprint). Angegebene Sicherheit 0,856–0,937, abhängig vom Prompt-Format, bei Trefferquoten von 49 % und 75,3 %.
[^ashery]: Ashery, A. F., Aiello, L. M., Baronchelli, A. (2025). [Emergent social conventions and collective bias in LLM populations](https://doi.org/10.1126/sciadv.adu9368). *Science Advances* 11(20), eadu9368.
[^agentattacks]: Anthropic (2025). [Disrupting the first reported AI-orchestrated cyber espionage campaign](https://www-cdn.anthropic.com/d7dd50dd1185f59be051b307150d877f2b82bd2c.pdf). November 2025. Lyons, J. (2026). [Autonomous AI attacks pose ‘clear and present danger’ to critical infrastructure](https://www.theregister.com/security/2026/08/14/autonomous-ai-attacks-pose-clear-and-present-danger-to-critical-infrastructure/5287594). *The Register*, 14. August 2026.
[^perrow]: Perrow, C. (1984). *Normal Accidents: Living with High-Risk Technologies*. Basic Books. Deutsch: *Normale Katastrophen. Die unvermeidbaren Risiken der Großtechnik*. Campus, 1987.
[^crowdstrike]: CrowdStrike (2024). [External Technical Root Cause Analysis: Channel File 291](https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf). Microsoft (2024). [Helping our customers through the CrowdStrike outage](https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/).
[^taleb]: Taleb, N. N., Read, R., Douady, R., Norman, J., Bar-Yam, Y. (2014). [The Precautionary Principle (with Application to the Genetic Modification of Organisms)](https://arxiv.org/abs/1410.5787). arXiv:1410.5787.
[^bravo]: Hansen, C. (1995). *The Swords of Armageddon: U.S. Nuclear Weapons Development since 1945*. Chukelea Publications. Das Boot hieß *Daigo Fukuryū Maru*, „Glücklicher Drache Nr. 5“.
[^greenblatt]: Greenblatt, R. (2026). [„I was the main person doing transcript analysis for this investigation of the Hugging Face incident …“](https://x.com/RyanGreenblatt/status/2092692685224325542). Post auf X, 26. August 2026.
[^testban]: National Security Archive (2024). [Castle BRAVO at 70: The Worst Nuclear Test in U.S. History](https://nsarchive.gwu.edu/briefing-book/nuclear-vault/2024-02-29/castle-bravo-70-worst-nuclear-test-us-history). U.S. Department of State. [Limited Test Ban Treaty (LTBT)](https://2009-2017.state.gov/t/avc/trty/199116.htm).
[^bostrom]: Bostrom, N., Douglas, T., Sandberg, A. (2016). [The Unilateralist's Curse and the Case for a Principle of Conformity](https://doi.org/10.1080/02691728.2015.1108373). *Social Epistemology* 30(4), 350–371. Englisch *unilateralist's curse*.
