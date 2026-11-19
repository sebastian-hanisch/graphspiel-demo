# Graphspiel: Wert und Verbindungen – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-graphspiel-demo.streamlit.app/)**

Teil der [Linie Koalitionen und Teilen](https://sebastianhanisch.net/konzepte-koalitionen-teilen.html). Vorgänger sind `shapley-demo` und `kern-demo`: Dort darf sich **jede** Gruppe von Betrieben bilden, das Netz der Verträge kommt nicht vor. Hier verbindet ein Netz die Betriebe, und **nur zusammenhängende Gruppen arbeiten zusammen**. Die Verteilungsregel dazu ist der **Myerson-Wert** (Shapley-Wert des auf das Netz eingeschränkten Spiels). Die Kante zu `centrality-demo` ist ein Kontrast: Dort ordnen Grad, Nähe und Zwischen die Betriebe nach der Struktur des Netzes, hier geht es um den Wert, den ein Betrieb **bekommt**, und der hängt am Basisspiel. Vehikel: ein synthetisches Netz von Betrieben (Subunternehmer, Spediteure) mit Fuhrparks; es gibt keine Daten echter Verträge.

**Abgrenzung zu `netzwerkspiel-demo`.** Dort wählt jeder Betrieb eine Aktion (Aufwand), und das Netz koppelt die Nutzen der Nachbarn; gesucht ist das Gleichgewicht eines linear-quadratischen Spiels. Hier gibt es keine Aktionen und kein Gleichgewicht: Eine Gruppe hat einen Wert, das Netz bestimmt, welche Gruppen ihn schaffen dürfen, und gesucht ist die Verteilung. Beide Demos stellen die Frage nach wichtigen Betrieben, aber die Rechnungen sind verschieden: dort der Rückgang der Gesamtaktivität, wenn ein Betrieb ausfällt, hier der Wert, den ein Betrieb bekommt, und was beim Wegfall eines **Vertrags** geschieht. Nachbar auf der Seite der Zuordnung ist `austauschnetz-demo` (Paarungen auf einem Graphen, anderes Modell). In der Linie nennt `machtindex-demo` diese Demo als Nachbarn (dort die Macht, die Stimmen und Sitze in einer Abstimmung verleihen, hier der Wert, den ein Netz von Verträgen verteilt).

## Kernfrage

*Betriebe sind über Verträge verbunden, nur zusammenhängende Gruppen arbeiten zusammen: wer bekommt wie viel, und was ändert sich, wenn eine Verbindung wegfällt?* Die App rechnet den Myerson-Wert exakt über alle Teilmengen (live bis n = 12) und zeigt ihn gegen den Shapley-Wert ohne Netz, dazu die Wirkung eines gekappten Vertrags, die Rangkorrelation mit Grad, Nähe und Zwischen, den Positionswert (Verträge als Spieler) und die Rechengrenze von exakter Rechnung und Stichprobe.

## Befunde und Korrekturen gegenüber dem Plan

Der Einzelplan dieser Demo (mit einer Vormessung durch Wegwerfskripte) nannte neun Hypothesen. Alle Zahlen wurden im Bau mit dem Code und dem Zufallsgenerator dieser Demo neu gemessen; die Abweichungen:

- **Der Hook ist nicht „Myerson ersetzt Zentralität“.** Bei Skaleneffekt (a > 1) folgt der Rang des Myerson-Werts dem Grad in 12 von 12 Zellen (Rangkorrelation 0,83 bis 0,93). Neu ist, dass **Vorzeichen und Größe am Basisspiel hängen** und dass ein Vertrag beide Enden **gleich** trifft. Das stimmt mit dem Plan überein.
- **Die Regel „Vorzeichen folgt dem Exponenten“ gilt für Potenzspiele (8 von 8 und 12 von 12 Zellen) und das Sättigungsspiel, aber nicht für jedes Basisspiel:** Beim Schwellenspiel ist die Rangkorrelation auf der Hantel −1,00; bei den Fixkosten kehrt c → −c das Vorzeichen der Rangkorrelation exakt um, welches Vorzeichen c = 0,5 liefert, hängt von der Netzform ab (−0,74 bis −0,08 in drei Zufallsfamilien, +0,02 im Zufallsbaum, +1,00 auf der Hantel; −0,08 und +0,02 liegen innerhalb der Streuung über Seeds). Wie im Plan als „widerlegt als allgemeine Regel“ geführt und hier als Gegenbeispiel-Preset in der App.
- **„Kappen schadet Dritten nie“ ist falsch, wie im Plan.** Auf einer Nicht-Brücke ändern sich alle Werte zusammen um 0 (Effizienz); der Unterschied liegt darin, **wer** gewinnt (Nachbarn eines Endes). Bei einer **Brücke** gewann unter Skaleneffekt kein Dritter (0 von 2058 Brücken).
- **Positionswert gleich Myerson-Wert auf Bäumen: widerlegt, wie im Plan** (Abstand bis 0,085 von v(N)). Abweichung: Die Rangfolge war auf den 40 Zufallsbäumen mit n = 7 **in 40 von 40** gleich (Plan: mittlere Rangkorrelation 0,980, kleinste 0,912, andere Ziehung der Bäume); der Befund ist ein Befund dieser Netze.
- **Spitzenspieler = Knoten höchsten Grades** in 67 bis 100 % der Netze (Plan: 72 bis 99 %); hier sind die Zufallsnetze mit anderem Generator gezogen (Komponenten werden durch Zusatzkanten verbunden statt zu verwerfen) und es sind 15 statt 40 Netze je Seed.
- **Ungleiche Fuhrparks:** Rangkorrelation des absoluten Myerson-Werts mit dem Grad nur −0,70 / +0,39 / +0,50 (a = 0,5 / 1,5 / 2), im Plan −0,65 / +0,39 / +0,48.
- **Rechengrenze:** exakt bis n = 22 in 0,72 s (Einzelmessung, Spitzenspeicher 336 MB); die App bietet den Messknopf deshalb nur bis n = 20 an (0,16 s, 84 MB), um den Speicher der Cloud-Instanz zu schonen (nicht auf der Cloud gemessen).
- **Plan-Korrektur bestätigt:** Der Bezug aller Verhältnisse ist der Shapley-Wert ohne Netz, nicht der Gleichteil (bei ungleichen Fuhrparks verschieden).
- **Offen und nicht gemessen** (wie im Plan): der Kern des eingeschränkten Spiels (H8) und stabile Netze bei Kosten je Vertrag (H9).

## Modell

Betriebe $1,\dots,n$, Netz $G$ (Verträge), Fuhrparks $w_i$. Basisspiel: Eine Gruppe $S$ mit Fuhrpark-Summe $x$ und $m$ Betrieben ist $v$ wert: Potenz $x^a$ (a < 1 Überlastung, a > 1 Skaleneffekt, a = 1 additiv), Sättigung $x\min(x,K)$ mit K = 3, Schwelle (1, wenn $x \ge t$ mit t = 3, sonst 0) und Fixkosten $x - c$ für Gruppen ab zwei Betrieben mit c = 0,5 oder c = −1 (Abstimmungsgewinn). Eingeschränktes Spiel: $v^G(S)$ ist die Summe der Basiswerte der zusammenhängenden Teile von $S$. Myerson-Wert: Shapley-Wert von $v^G$. Alle Formeln stehen im 📐-Expander der App; Gruppenwerte, Fuhrparks und Netze sind Modellannahmen.

Netzformen: Stern, Pfad, Ring, Hantel (zwei Cliquen, also zwei vollständig verbundene Gruppen aus n/2 und dem Rest, durch eine Brücke verbunden), vollständig, Zufallsnetz dünn (Kantenwahrscheinlichkeit 0,25) und dicht (0,5) mit je einer Zufallskante zwischen den Komponenten, Zufallsbaum (jeder Betrieb hängt sich an einen früheren), Preferential Attachment (zwei Kanten je neuem Betrieb). Zufall: SplitMix64 (`gsd_rng.py`, wörtliche Kopie aus `ab-test-demo`, Kopietest).

## Methodik

Der Myerson-Wert wird exakt über alle $2^n$ Teilmengen gerechnet (`gsd_games.py`): je Teilmenge wird der Wert der zusammenhängenden Teile bestimmt (Breitensuche über Bitmasken, alle Teilmengen vektorisiert), daraus der Shapley-Wert. Für große Netze gibt es eine Stichprobe von Reihenfolgen mit Union-Find. Für den Stern gibt es eine Handformel. Die App hat vier Ansichten, alle mit Verdikt:

1. **Verbindung kappen:** ein Vertrag wird gewählt, die Myerson-Werte mit und ohne ihn werden verglichen (Enden, Nachbarn, übrige Dritte, Brücke oder nicht). Dazu eine Messreihe über alle Kappungen in Zufallsnetzen (E2).
2. **Zentralität gegen Wert:** Rangkorrelation des Myerson-Werts mit Grad, Nähe und Zwischen auf dem aktuellen Netz, eine Kurve über den Exponenten, und eine Messreihe über Netzfamilien und alle zehn Basisspiele (E1).
3. **Kanten als Spieler:** der Positionswert (Definition dieser Demo, siehe unten) gegen den Myerson-Wert, bis 14 Verträge.
4. **Rechengrenze:** Stichprobe gegen exakten Wert (n = 16, m = 100, 1 000 und 10 000 Reihenfolgen), Rechenzeit des exakten Wegs bis n = 20 und eine Stichprobe auf einem Netz mit 200 Betrieben (E3).

Die Messreihen laufen auf Klick und sind unabhängig von den Reglern der Seitenleiste (feste Zufalls-Seeds 11, 22, 33, 44). Der **Positionswert** ist so definiert: Spieler sind die Verträge; die Vertragsmenge $F$ ist so viel wert wie das Netz $(N, F)$ ($r(F)$ = Summe der Basiswerte seiner zusammenhängenden Teile, isolierte Betriebe zählen mit ihrem Einzelwert); jeder Vertrag bekommt seinen Shapley-Wert in $r - r(\emptyset)$, jeder Betrieb die Hälfte der Werte seiner Verträge plus seinen Einzelwert. Ob diese Fassung der Originalarbeit entspricht, ist nicht geprüft.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind in `tests/test_claims.py` nachgerechnet; Tabellen stammen aus `tools/readme_rows.py` (dieselben Funktionen wie in der App) und werden dort Zeile für Zeile gegen diese Datei geprüft. „Seeds“ sind die vier festen Zufalls-Seeds 11, 22, 33, 44; „Läufe“ die Zahl der Netze.

| Frage | Befund (mit Voraussetzung) | Test |
|---|---|---|
| Handbeispiel | Pfad aus 3 Betrieben (Mitte B1), Wert einer Gruppe = (Fuhrparks)², gleiche Fuhrparks: Myerson-Wert 11/3, 8/3, 8/3, ohne Netz 3, 3, 3, Positionswert 4, 2,5, 2,5. Zusätzlich 60 Mini-Instanzen (n = 4 bis 6, sieben Basisspiele): Zählweg = Aufzählung aller Reihenfolgen = Fairness-Rekursion = Harsanyi-Dividenden bis 1e-9; Dividenden nicht zusammenhängender Mengen sind 0 | `test_hand_example_path_of_three_betriebe`, `test_oracle_graphspiel.py` |
| Stern, n = 10, gleiche Fuhrparks | Myerson-Wert der Nabe geteilt durch den Gleichteil v(N)/n: −7,13 (a = 0,5), −1,81 (a = 0,75), 1,00 (a = 1), 3,09 (a = 1,5), 3,40 (a = 2), 2,98 (a = 3); Schwelle t = 3: 8,00. Nicht monoton in a. Das Netz verteilt dabei 81,3 / 28,1 / 0,0 / 20,9 / 24,0 / 19,8 % von v(N) um | `test_star_of_ten_firms_hub_ratio_by_exponent` |
| Preset Hantel, n = 10, a = 2 | Die beiden Brückenbetriebe bekommen 19,33 gegen 7,67 der übrigen acht (1,93-faches des Werts ohne Netz); 18,7 % von v(N) werden umverteilt | `test_hantel_preset_bridge_firms_and_threshold_counterexample` |
| Gegenbeispiel Hantel, Schwelle t = 3 | Die beiden Brückenbetriebe bekommen ein **negatives** Ergebnis (−1,11-faches), die übrigen acht das 1,53-fache; 42,2 % von v(N) umverteilt | derselbe Test |
| Ring und vollständiges Netz | Keine Wirkung in allen zehn Basisspielen bei n = 10 und gleichen Fuhrparks (Abstand unter 1e-9); mit ungleichen Fuhrparks hat der Ring eine Wirkung. Additiv (a = 1): auch keine Wirkung (Rangkorrelation nicht definiert) | `test_ring_and_complete_net_have_no_effect_in_every_basisspiel`, `test_e1_additive_game_is_a_dead_branch_and_reports_no_correlation` |
| Voreinstellungen Zufallsnetz | Zufallsnetz dünn, n = 10, Seed 35, a = 2: die Betriebe mit den meisten Verträgen bekommen das 1,30-fache, 11,1 % von v(N) umverteilt; mit ungleichen Fuhrparks und a = 1,5: 1,13-faches, 7,7 % | `test_default_zufallsnetz_and_unequal_fleets_presets` |
| Vorzeichen folgt dem Exponenten (E1) | Rangkorrelation Myerson ↔ Grad, n = 10, gleiche Fuhrparks, 4 Seeds × 15 Netze = 60 Netze je Zelle: bei a < 1 negativ in 8 von 8 Zellen (−0,94 bis −0,88), bei a > 1 positiv in 12 von 12 (0,83 bis 0,93); vier Zufallsfamilien × zwei bzw. drei Exponenten | `test_e1_sign_follows_the_exponent_in_8_of_8_and_12_of_12_cells` |
| Nabe bei Überlastung (a = 0,5) | Mittel des Verhältnisses der Betriebe mit den meisten Verträgen: −0,36 (Zufallsnetz dünn), −1,56 (Zufallsbaum), −0,27 (Preferential Attachment), −0,31 (Hantel), aber +0,62 im dichten Zufallsnetz (Mittel über Netze, dann über Seeds; negativ ist das Verhältnis in 68 % der dünnen Zufallsnetze, 100 % der Zufallsbäume, 75 % der Preferential-Attachment-Netze und 3 % der dichten Zufallsnetze, in allen Netzen liegt es unter 1) | `test_e1_negative_hub_value_at_overload` |
| Andere Basisspiele (E1) | Sättigung K = 3: Rangkorrelation über 0,9 in den vier Zufallsfamilien, 1,00 auf der Hantel. Schwelle t = 3: 0,56 bis 0,94 in den vier Zufallsfamilien, aber −1,00 auf der Hantel. Fixkosten c = 0,5: negativ in 3 von 4 Zufallsfamilien (−0,74 bis −0,08), +0,02 im Zufallsbaum, +1,00 auf der Hantel; c = −1 ist exakt gespiegelt | `test_e1_other_basisspiele_do_not_follow_the_power_rule` |
| Spitzenspieler | Ein Betrieb mit dem höchsten Myerson-Wert hat auch höchsten Grad (bei Gleichstand großzügig gezählt) in 90 / 87 / 78 % der Zufallsnetze dünn (a = 1,5 / 2 / 3), in allen vier Zufallsfamilien und drei Exponenten 67 bis 100 % | `test_e1_top_player_is_a_node_of_highest_degree_share` |
| Ungleiche Fuhrparks | Zufallsnetz dünn, n = 10, Fuhrparks aus 1, 2, 3, 5, 60 Netze: Rangkorrelation des absoluten Myerson-Werts mit dem Grad −0,70 (a = 0,5), 0,39 (a = 1,5), 0,50 (a = 2) | `test_e1_unequal_fleets_weaken_the_link_to_the_degree` |
| Gleichverlust (E2) | In 3692 Kappungen (Zufallsnetz dünn und Zufallsbaum, n = 8, gleiche Fuhrparks, 60 Netze je Netzform, vier Exponenten) ändern sich beide Enden um denselben Betrag (größte Abweichung unter 1e-9). Bei a = 1,5, 2, 3 verlieren beide Enden in allen Kappungen, bei a = 0,5 gewinnen beide in allen | `test_e2_equal_loss_and_sign_of_the_ends` |
| Brücken (E2) | 266 von 503 Kappungen im Zufallsnetz dünn und alle 420 im Zufallsbaum sind Brücken. Unter Skaleneffekt (a = 1,5, 2, 3) gewann bei 0 von 2058 Brücken ein Dritter, bei a = 0,5 bei allen 686 | `test_e2_bridges_and_third_parties` |
| Nachbarn gegen übrige Dritte (E2) | Auf den 237 Nicht-Brücken des Zufallsnetzes dünn gewinnen Nachbarn eines Endes bei a = 2 im Mittel +0,72 (818 Paare), die übrigen Dritten +0,06 (604 Paare); bei a = 3 +5,73 gegen −0,09 | `test_e2_neighbours_gain_more_than_other_third_parties_on_non_bridges` |
| Effizienz bei Nicht-Brücken | Auf Nicht-Brücken summieren sich alle Änderungen zu 0 (Zufallsnetz dicht, n = 8, a = 2, 20 Netze, über 50 Kappungen) | `test_e2_sum_of_changes_is_zero_on_non_bridges` |
| Stern kappen | Stern n = 10, a = 2, eine Speiche gekappt: Nabe 34 → 27,67, gekapptes Blatt 7,33 → 1 (beide verlieren 6,33), jedes andere Blatt 7,33 → 6,67 | `test_star_cut_by_formula` |
| Positionswert | Nicht gleich dem Myerson-Wert, auch nicht auf Bäumen: 40 Zufallsbäume (n = 7, a = 2, 4 Seeds × 10): Abstand höchstens 0,085, im Mittel 0,057, Rangfolge in 40 von 40 gleich; 40 Zufallsnetze dünn: höchstens 0,075, im Mittel 0,046, Rangkorrelation im Mittel 0,995, kleinste 0,88 | `test_position_value_is_not_the_myerson_value_even_on_trees` |
| Stichprobe (E3) | Zufallsnetz dünn, n = 16, Quadratisch, 4 Seeds: siehe Tabelle 3; Preferential Attachment, n = 200, 1 000 Reihenfolgen, Seed 11: größter Standardfehler 0,12 Gleichteile, die Nabe 4,4 Gleichteile (Bänder im Test) | `test_sample_error_falls_with_the_number_of_orders`, `test_large_net_sample_standard_error_band` |

**Tabelle 1: Rangkorrelation Myerson-Wert ↔ Grad** (n = 10, gleiche Fuhrparks, Zufallsfamilien: Mittel über 4 Seeds × 15 Netze; Hantel: ein Netz; „–“: nicht definiert, weil der Myerson-Wert für alle Betriebe gleich ist).

| Netzform | Überlastung a = 0,5 | Leichte Überlastung a = 0,75 | Additiv a = 1 | Skaleneffekt a = 1,5 | Quadratisch a = 2 | Starker Skaleneffekt a = 3 | Sättigung K = 3 | Schwelle t = 3 | Fixkosten c = 0,5 | Abstimmungsgewinn c = −1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Zufallsnetz dünn | −0,91 | −0,91 | – | 0,89 | 0,87 | 0,85 | 0,91 | 0,72 | −0,08 | 0,08 |
| Zufallsnetz dicht | −0,89 | −0,88 | – | 0,86 | 0,85 | 0,83 | 0,91 | 0,94 | −0,74 | 0,74 |
| Zufallsbaum | −0,92 | −0,92 | – | 0,92 | 0,91 | 0,90 | 0,92 | 0,56 | 0,02 | −0,02 |
| Preferential Attachment | −0,94 | −0,94 | – | 0,93 | 0,93 | 0,92 | 0,94 | 0,92 | −0,60 | 0,60 |
| Hantel | −1,00 | −1,00 | – | 1,00 | 1,00 | 1,00 | 1,00 | −1,00 | 1,00 | −1,00 |

**Tabelle 1b: Verhältnis Myerson-Wert ÷ Wert ohne Netz der Betriebe mit den meisten Verträgen** (gleiche Zellen; Mittel über die Netze, dann über die Seeds; bei Gleichstand im Höchstgrad alle).

| Netzform | Überlastung a = 0,5 | Leichte Überlastung a = 0,75 | Additiv a = 1 | Skaleneffekt a = 1,5 | Quadratisch a = 2 | Starker Skaleneffekt a = 3 | Sättigung K = 3 | Schwelle t = 3 | Fixkosten c = 0,5 | Abstimmungsgewinn c = −1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Zufallsnetz dünn | −0,36 | 0,51 | 1,00 | 1,43 | 1,55 | 1,53 | 1,42 | 1,78 | 1,03 | 0,96 |
| Zufallsnetz dicht | 0,62 | 0,87 | 1,00 | 1,09 | 1,10 | 1,07 | 1,14 | 1,48 | 0,99 | 1,02 |
| Zufallsbaum | −1,56 | 0,07 | 1,00 | 1,79 | 1,99 | 1,91 | 1,79 | 2,47 | 1,04 | 0,93 |
| Preferential Attachment | −0,27 | 0,56 | 1,00 | 1,34 | 1,39 | 1,32 | 1,44 | 2,17 | 0,98 | 1,03 |
| Hantel | −0,31 | 0,46 | 1,00 | 1,64 | 1,93 | 2,08 | 1,13 | −1,11 | 1,18 | 0,70 |

**Tabelle 2: Verbindung kappen** (n = 8, gleiche Fuhrparks, 4 Seeds × 15 Netze je Netzform; gezählt über die Kappungen; Nachbar: mit einem Ende im Netz verbunden, nur bei Nicht-Brücken; Mittel der Änderung, in Klammern die Zahl der Paare).

| Netzform | Basisspiel | Kappungen | beide Enden verlieren | beide Enden gewinnen | Brücken | Brücken mit gewinnendem Dritten | Nachbar im Mittel (Paare) | andere Dritte im Mittel (Paare) |
|---|---|---|---|---|---|---|---|---|
| Zufallsnetz dünn | Überlastung (a = 0,5) | 503 | 0 | 503 | 266 | 266 | −0,07 (818) | −0,01 (604) |
| Zufallsnetz dünn | Skaleneffekt (a = 1,5) | 503 | 503 | 0 | 266 | 0 | 0,20 (818) | 0,02 (604) |
| Zufallsnetz dünn | Quadratisch (a = 2) | 503 | 503 | 0 | 266 | 0 | 0,72 (818) | 0,06 (604) |
| Zufallsnetz dünn | Starker Skaleneffekt (a = 3) | 503 | 503 | 0 | 266 | 0 | 5,73 (818) | −0,09 (604) |
| Zufallsbaum | Überlastung (a = 0,5) | 420 | 0 | 420 | 420 | 420 | – | – |
| Zufallsbaum | Skaleneffekt (a = 1,5) | 420 | 420 | 0 | 420 | 0 | – | – |
| Zufallsbaum | Quadratisch (a = 2) | 420 | 420 | 0 | 420 | 0 | – | – |
| Zufallsbaum | Starker Skaleneffekt (a = 3) | 420 | 420 | 0 | 420 | 0 | – | – |

**Tabelle 3: Stichprobe gegen exakt** (Zufallsnetz dünn, n = 16, Quadratisch, gleiche Fuhrparks, 4 Zufalls-Seeds; Fehler in Vielfachen des Gleichteils v(N)/n; Rangkorrelation Mittel über die Seeds; Spitzenspieler: Anteil der Seeds).

| Reihenfolgen m | größter Fehler (Gleichteile), Mittel ± Streuung | Rangkorrelation | gleicher Spitzenspieler |
|---|---|---|---|
| 100 | 0,285 ± 0,046 | 0,962 | 75 % |
| 1000 | 0,094 ± 0,017 | 0,979 | 100 % |
| 10000 | 0,029 ± 0,003 | 0,995 | 100 % |

**Einzelmessungen dieser README, nicht im Test** (Laufzeiten hängen vom Rechner ab; Windows, Python 3.14, ein Lauf, Zufallsnetz dünn, Quadratisch, gleiche Fuhrparks, Zufalls-Seed 35): exakter Weg n = 18 0,04 s und 21 MB, n = 20 0,16 s und 84 MB, n = 22 0,72 s und 336 MB (Spitzenspeicher aus `tracemalloc`).

## Annahmen, Grenzen und bekannte Probleme

**Annahmen**

- Betriebe sind die Spieler, Verträge sind die Kanten eines Netzes. Eine Gruppe von Betrieben schafft nur Wert, wenn sie über Verträge zusammenhängt; nicht zusammenhängende Teile einer Gruppe zählen einzeln (Myerson 1977).
- Das Basisspiel ist ein Gewinnspiel (größer ist besser) und hängt nur von der Fuhrpark-Summe einer Gruppe ab, bei den Fixkosten zusätzlich von der Zahl ihrer Betriebe. Exponent, Sättigung, Schwelle und Fixkosten sind Modellannahmen, keine Messungen.
- Die Auszahlung ist der Shapley-Wert des eingeschränkten Spiels (Myerson-Wert). Als Bezug dient immer der Shapley-Wert des Basisspiels ohne Netz; bei gleichen Fuhrparks ist das der Gleichteil v(N)/n.
- Das Netz ist zusammenhängend und fest; niemand verhandelt über Verträge, und ein Vertrag hat keine Kosten.
- Die Netze sind synthetisch (Stern, Pfad, Ring, Hantel, vollständig, zwei Zufallsnetze, Zufallsbaum, Preferential Attachment). Es gibt keine Daten echter Verträge.

**Grenzen**

- Die Kern-Frage (kann sich eine Gruppe abspalten und besser stellen?) wird hier nicht gestellt und nicht gemessen; ebenso wenig, welche Verträge Betriebe schließen würden, wenn Verträge Kosten hätten.
- Die Befunde der Experimente gelten für die genannten Netzfamilien, Betriebszahlen, Basisspiele und Zufalls-Seeds, nicht für jedes Netz. Dass der Rang des Myerson-Werts dem Grad folgt, gilt für die geprüften Potenz- und Sättigungsspiele, nicht für alle Basisspiele.
- Der exakte Weg zählt alle 2^n Teilmengen: live bis n = 12, auf Klick gemessen bis n = 20. Größere Netze brauchen die Stichprobe von Reihenfolgen, deren Fehler vom Netz abhängt.
- Der Positionswert ist hier nach der Beschreibung in der Zusammenfassung der Quelle definiert (Kanten als Spieler, Hälfte je Endbetrieb, Einzelwerte addiert); eine Übereinstimmung mit der Originalarbeit ist nicht geprüft. Er wird nur bis 14 Verträge berechnet.
- Keine Rechts-, Vertrags- oder Anlageberatung: Gruppenwerte und Auszahlungen sind Rechenbeispiele.

**Bekannte Probleme und Unsicherheiten**

- Werte, die sich um weniger als 1e-9 unterscheiden, gelten als gleich (Rundung). Die Schwelle der Verdikte (Verhältnis innerhalb 1 ± 0,05 gilt als „etwa gleich“) ist eine Festlegung dieser Demo.
- Die Spitze nach Myerson-Wert gilt bei Gleichstand als Knoten höchsten Grades, wenn ein gleichauf liegender Knoten höchsten Grad hat (großzügige Lesart).
- Die Verbindung, die im Tab „Verbindung kappen“ gewählt wird, steht nicht im Permalink.
- Die Laufzeiten im Tab „Rechengrenze“ sind Messungen auf dem jeweiligen Rechner und schwanken mit dessen Last.
- Die Literaturangaben sind bibliographisch über Suchergebnisse bestätigt; Volltexte wurden nicht gelesen.

## Ehrliche Grenzen

- **Nur Gewinnspiele, nur feste Netze:** Der Kern des eingeschränkten Spiels und die Frage, welche Verträge Betriebe schließen würden, sind nicht gemessen (H8 und H9 des Plans).
- **Die Regel „Vorzeichen folgt dem Exponenten“ gilt für Potenz- und Sättigungsspiele**, nicht für Schwelle und Fixkosten (Tabelle 1). Warum (Deutung, nicht gemessen): Bei den Fixkosten ist der Myerson-Wert bei gleichen Fuhrparks linear in c; deshalb ist die Rangkorrelation bei c und −c exakt gespiegelt (ihr Vorzeichen bei c = 0,5 hängt von der Netzform ab); die Spiegelung ist getestet, die Deutung nicht.
- **Gleiche Fuhrparks sind die Voreinstellung**, damit das Netz allein wirkt; bei ungleichen Fuhrparks ist die Rangkorrelation des absoluten Myerson-Werts mit dem Grad schwächer (−0,70 / 0,39 / 0,50), auch weil der Fuhrpark den Wert mitbestimmt.
- **Synthetische Netze mit festen Parametern, n = 10 (E1) und n = 8 (E2):** Die Quoten gelten für diese Netzfamilien und Zahlen, nicht für echte Betriebe. Die Höhe hängt am Generator (Zufallsnetze mit Zusatzkanten verbunden).
- **Brückenbefund und Dritte:** Dass bei Brücken unter Skaleneffekt kein Dritter gewinnt, ist ein Messbefund an 2058 Brücken, kein Satz.
- **Der Positionswert ist nach der Beschreibung in Zusammenfassungen definiert,** nicht gegen die Originalarbeit geprüft.
- **Literatur:** Alle Angaben beruhen auf Titel und Zusammenfassung, nicht auf Volltexten. Myerson (1977), Gómez u. a. (2003) und Borm, Owen, Tijs (1992) sind bibliographisch über Suchergebnisse bestätigt; die Formeln stützen sich auf die Messungen dieser Demo (drei unabhängige Rechenwege), nicht auf die Aufsätze. Weitere Aufsätze zum Positionswert, zu Zentralitäten in Netzspielen und zu polynomiellen Formeln bei Bäumen wurden nicht geprüft und sind hier nicht zitiert.

## Verifikation

- **Kern:** Basisspiele, Teile, eingeschränktes Spiel, Shapley, Myerson, Stern und Stichprobe gegen Handrechnung auf dem Pfad aus 3 Betrieben (`tests/test_algorithm.py`), Randfälle n = 0, 1, 2, kein Vertrag, Gleichstände, Schwellen inklusive, ungültige Kanten (`tests/test_edge_cases.py`).
- **Orakel (anderer Rechenweg):** Aufzählung aller Reihenfolgen mit networkx, Fairness-Rekursion (Komponenten-Effizienz und Gleichverlust, ohne Teilmengen-Code), Harsanyi-Dividenden zusammenhängender Mengen, Handformel für den Stern, Stichprobe gegen exakt innerhalb von 4 Standardfehlern; 60 Mini-Instanzen im Repo (`tests/test_oracle_graphspiel.py`), Scratch-Lauf außerhalb des Repos (Messung dieser README, nicht im Test): 300 Instanzen (n = 3 bis 7, alle Netzfamilien, sieben Basisspiele, Fuhrparks aus 1, 2, 3, 5), davon 260 mit höchstens 9 Verträgen für die Fairness-Rekursion; größte Abweichung des Zählwegs 1,5e-12 gegen die Aufzählung, 4,3e-14 gegen die Fairness-Rekursion und 2,8e-14 gegen die Dividenden, Dividenden nicht zusammenhängender Mengen in keiner Instanz ungleich 0. Zentralitäten gegen networkx, Rangkorrelation gegen scipy (`tests/test_centrality.py`).
- **Eigenschaftstests:** Effizienz je Komponente, Umbenennen, a = 1 gibt die Fuhrparks selbst, Ring und vollständiges Netz, Gleichverlust auf Zufallsnetzen, Linearität im Basisspiel (`tests/test_eigenschaften_graphspiel.py`).
- **Zweig-Tests:** Additiv, Ring und vollständiges Netz haben keine Wirkung und melden sie so; jedes andere Basisspiel weicht auf dem Stern ab (`tests/test_presets.py`).
- **Verdikte** als reine Funktionen an handgesetzten Werten, jede Schwelle und jedes Preset (`tests/test_verdicts.py`); **Presets, Layout, AppTest** (jeder Knopf, jeder Regler an Minimum und Maximum, jede Auswahl, jeder Vertrag im Kappen-Tab), **Footer**, **Laufzeit-Importe**, **Kopie des Zufallsgenerators**.
- **Behauptungen:** `tests/test_claims.py` rechnet jede Zahl dieser Datei nach (Tabellen Zeile für Zeile).
- **Umfang:** 168 Tests, lokal einmal gemessen rund 31 Sekunden mit `pytest -n 4` (Windows, Python 3.14; hängt von der Last ab). Browser-Durchlauf lokal: drei Presets, alle drei Messreihen, beide Expander, n = 12 mit vollständigem Netz, ohne Konsolenfehler und ohne KaTeX-Fehler. Nicht gelaufen: Mutationstests (nicht mehr Teil des Ablaufs), Prüfung der Cloud-Umgebung und echte Mausklicks im Browser (die App hat nur Hover am Diagramm). **Aussagenprüfung:** Ein unabhängiger Prüfer hat die Aussagen von README und App geprüft (34 Aussagen: 20 belegt, 10 mit Einschränkung, 3 übertrieben, 1 nicht prüfbar). Er fand keinen Rechenfehler; seine eigenen Zählwege auf 240 Zufallsinstanzen wichen höchstens um 9e-13 von der Demo ab. Die Einschränkungen und Übertreibungen sind in README und App eingearbeitet; der Prüfbericht liegt nicht in diesem Repo. Nach der Überarbeitung der Texte ist ein kurzer Zweitlauf der Aussagenprüfung noch nicht erfolgt.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, vier Ansichten, Grenzen, Formeln |
| `gsd_games.py` | Kern: Basisspiel, eingeschränktes Spiel, Shapley- und Myerson-Wert (exakt, Stichprobe, Stern) |
| `gsd_cut.py` | Verbindung kappen, Positionswert |
| `gsd_centrality.py` | Grad, Nähe, Zwischen, Rangkorrelation |
| `gsd_scenario.py` | Netzfamilien, Fuhrparks, Layout |
| `gsd_evaluation.py` | Analyse, Messreihen E1 bis E3, Verdikte (reine Funktionen) |
| `gsd_constants.py` | Regler-Grenzen, Basisspiele, Seeds, Presets |
| `gsd_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `gsd_layout.py` | Fester Kopf (Stylesheet) |
| `gsd_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `gsd_texts.py` | Texte, die in App und README gleich lauten (Annahmen, Erklärtabelle, Literatur) |
| `gsd_rng.py` | SplitMix64, wörtliche Kopie aus `ab-test-demo` |
| `tools/readme_rows.py` | erzeugt die README-Tabellen über dieselben Funktionen wie die App |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `requirements-dev.txt` | Laufzeit plus pytest, networkx und scipy (nur für Gegenproben) |
| `tests/` | Mini-Instanz, Orakel, Eigenschaften, Randfälle, Claims, Verdikte, Presets, Layout, AppTest, Footer, Texte, Kopie, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Kern des eingeschränkten Spiels und Netzbildung mit Kosten je Vertrag** (H8, H9): nicht gemessen; die Frage gehört in eine eigene Messung.
- **PageRank** und weitere Zentralitäten; **Schätzen aus Daten**; **PDF-Export**.
- **Gerichtete Netze**, Gewichte auf Kanten, Spiele mit Verlusten (Kostenspiele): hier nur Gewinnspiele auf ungerichteten, zusammenhängenden Netzen.
- **Exakt über n = 20 im Browser:** größere Netze nur über die Stichprobe.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die CI läuft mit Python 3.12; für die Streamlit Community Cloud ist die Python-Version im Dashboard einzustellen (3.12 empfohlen).

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Koalitionen und Teilen: Macht und Aufteilung](https://sebastianhanisch.net/konzepte-koalitionen-teilen.html).
