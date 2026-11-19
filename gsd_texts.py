"""Feste Texte der App, die auch in der README stehen (ein Test vergleicht sie): Annahmen, Grenzen, bekannte Probleme.

Zahlen stehen hier nur, wenn sie Einstellungen sind (Regler, Raster, Schwellen); Messzahlen kommen per f-String aus der Rechnung
oder stehen in der README mit Testverweis."""

ASSUMPTIONS_MARKDOWN = """\
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
"""

EXPLAIN_TABLE = """\
| Begriff | Was er bedeutet | Beispielspur: Pfad B2–B1–B3 (Mitte B1), Wert einer Gruppe = (Fuhrparks)² |
|---|---|---|
| **Basisspiel** | Was eine Gruppe wert wäre, wenn sie sich frei bilden dürfte. | Gruppe aus 1, 2 oder 3 Betrieben: 1, 4 oder 9. |
| **Zusammenhängende Teile (Komponenten)** | Teile einer Gruppe, die über Verträge verbunden sind. Nur sie arbeiten zusammen. | Die Gruppe {B2, B3} ohne die Mitte besteht aus zwei Teilen: Wert 1 + 1 = 2 statt 4. |
| **Eingeschränktes Spiel** | Wert einer Gruppe = Summe der Basiswerte ihrer zusammenhängenden Teile. | Wert von {B1, B2} = 4, von {B2, B3} = 2, von allen drei = 9. |
| **Shapley-Wert** | Mittlerer Beitrag eines Betriebs über alle Reihenfolgen, in denen die Gruppe wachsen kann. | Ohne Netz bekommt jeder der drei 3. |
| **Myerson-Wert** | Shapley-Wert des eingeschränkten Spiels: derselbe Mittelwert, aber nur zusammenhängende Gruppen schaffen Wert. | Mitte 11/3, jedes Ende 8/3: die Mitte verdient mehr. |
| **Gleichverlust (Fairness)** | Fällt ein Vertrag weg, ändert sich der Myerson-Wert seiner beiden Enden um denselben Betrag (Myerson 1977). | Ohne den Vertrag B1–B2 verlieren B1 und B2 je 5/3, B3 verliert 2/3. |
| **Gleichteil** | v(N)/n: der Anteil, den jeder bei gleichen Fuhrparks ohne Netz bekäme. Bei ungleichen Fuhrparks ist der Bezug der Shapley-Wert ohne Netz. | Hier 9/3 = 3 je Betrieb. |
"""

LITERATUR_HEAD = "**Literatur** (Titel, Zeitschrift und Seiten über Suchergebnisse bestätigt; Volltexte nicht gelesen)"
LITERATUR = [
    "- Myerson, R. B. (1977): Graphs and Cooperation in Games. Mathematics of Operations Research 2(3), 225–229. Zusammenfassung gelesen: Auszahlungsregeln für Spiele mit einer Kooperationsstruktur aus einem Graphen.",
    "- Gómez, D., González-Arangüena, E., Manuel, C., Owen, G., del Pozo, M., Tejada, J. (2003): Centrality and power in social networks: a game theoretic approach. Mathematical Social Sciences 46(1), 27–54. Zusammenfassung gelesen: Zentralität als Unterschied der Shapley-Macht im eingeschränkten und im ursprünglichen Spiel.",
    "- Borm, P., Owen, G., Tijs, S. (1992): On the position value for communication situations. SIAM Journal on Discrete Mathematics 5(3), 305–320. Nur über Zusammenfassungen anderer Arbeiten bestätigt (Kanten als Spieler, Hälfte je Endknoten).",
]
