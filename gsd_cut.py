"""Verbindung kappen und Kanten als Spieler (Positionswert)."""

from dataclasses import dataclass

import numpy as np

from gsd_games import BaseGame, base_value, myerson_exact, shapley_vector
from gsd_scenario import connected_components


@dataclass(frozen=True)
class CutEffect:
    edge: tuple[int, int]
    before: tuple[float, ...]     # Myerson-Wert mit der Verbindung
    after: tuple[float, ...]      # Myerson-Wert ohne die Verbindung
    is_bridge: bool               # zerfällt das Netz (genauer: die Komponente der Kante) ohne die Verbindung?

    @property
    def change(self) -> np.ndarray:
        """Änderung je Betrieb (nachher minus vorher)."""
        return np.array(self.after) - np.array(self.before)

    @property
    def end_change(self) -> tuple[float, float]:
        i, j = self.edge
        ch = self.change
        return float(ch[i]), float(ch[j])

    def third_changes(self, edges) -> tuple[list[float], list[float]]:
        """Änderungen der Dritten (nicht Endpunkte): (Nachbarn eines Endes im Netz mit der Verbindung, alle übrigen)."""
        i, j = self.edge
        nbrs = set()
        for a, b in edges:
            for u, v in ((a, b), (b, a)):
                if u in (i, j) and v not in (i, j):
                    nbrs.add(v)
        ch = self.change
        near = [float(ch[k]) for k in range(len(ch)) if k not in (i, j) and k in nbrs]
        far = [float(ch[k]) for k in range(len(ch)) if k not in (i, j) and k not in nbrs]
        return near, far


def cut_edge(n: int, edges, weights, game: BaseGame, edge: tuple[int, int]) -> CutEffect:
    """Myerson-Werte mit und ohne die Verbindung `edge` (muss im Netz liegen)."""
    edges = tuple(edges)
    if edge not in edges:
        raise ValueError(f"Kante {edge} liegt nicht im Netz")
    rest = tuple(e for e in edges if e != edge)
    before = myerson_exact(n, edges, weights, game)
    after = myerson_exact(n, rest, weights, game)
    comp_before = len(connected_components(n, edges))
    comp_after = len(connected_components(n, rest))
    return CutEffect(edge, tuple(float(x) for x in before), tuple(float(x) for x in after), comp_after > comp_before)


def position_value(n: int, edges, weights, game: BaseGame) -> np.ndarray:
    """Positionswert (Kanten als Spieler, so definiert in dieser Demo): Spieler sind die Verträge; eine Kantenmenge F ist so viel wert wie das
    Netz (N, F), nämlich r(F) = Σ v(C) über seine Teile (isolierte Betriebe zählen mit ihrem Einzelwert). Jeder Vertrag bekommt seinen
    Shapley-Wert in r − r(∅), jeder Betrieb die Hälfte der Werte seiner Verträge plus seinen Einzelwert v({i}). Höchstens 2^|E| Koalitionen."""
    edges = tuple(edges)
    m = len(edges)
    single = np.asarray(base_value(game, np.asarray(weights, dtype=float), np.ones(n, dtype=int)), dtype=float)
    out = single.copy()
    if m == 0:
        return out
    r = np.zeros(1 << m)
    for mask in range(1 << m):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for e in range(m):
            if mask >> e & 1:
                a, b = find(edges[e][0]), find(edges[e][1])
                if a != b:
                    parent[a] = b
        wsum, size = {}, {}
        for i in range(n):
            root = find(i)
            wsum[root] = wsum.get(root, 0.0) + weights[i]
            size[root] = size.get(root, 0) + 1
        r[mask] = sum(float(base_value(game, wsum[k], size[k])) for k in wsum)
    sh = shapley_vector(m, r - r[0])
    for e, (i, j) in enumerate(edges):
        out[i] += sh[e] / 2
        out[j] += sh[e] / 2
    return out
