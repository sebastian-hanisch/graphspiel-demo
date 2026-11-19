"""Kern: Basisspiel, eingeschränktes Spiel auf dem Netz und Myerson-Wert (numpy, Standardbibliothek).

Spieler sind die Betriebe 0 bis n-1, ein Netz ist eine Kantenliste (i, j) mit i < j, Gewichte sind die Fuhrparkgrößen wᵢ.
Basisspiel: Eine Gruppe S mit Fuhrpark-Summe x = Σ wᵢ und m = |S| Betrieben ist `base_value(game, x, m)` wert.
Eingeschränktes Spiel (Myerson 1977): v^G(S) = Σ v(C) über die zusammenhängenden Teile C des Netzes auf S.
Myerson-Wert = Shapley-Wert des eingeschränkten Spiels.

Jede Regel ist eine eigene Funktion (DEMO-PLAYBOOK §1b): `base_value` (Wert einer Gruppe), `components_of` (Teile per Breitensuche),
`restricted_value` (Wert einer Teilmenge im Netz), `restricted_vector` (alle Teilmengen auf einmal), `shapley_vector`,
`myerson_exact` (Zählweg über alle 2^n Teilmengen), `myerson_sample` (Stichprobe von Reihenfolgen, Union-Find), `myerson_star`
(Handformel für den Stern)."""

import math
from dataclasses import dataclass

import numpy as np

from gsd_rng import SplitMix64


@dataclass(frozen=True)
class BaseGame:
    kind: str       # "potenz" | "saettigung" | "schwelle" | "fixkosten"
    param: float    # Exponent a, Sättigung K, Schwelle t, Fixkosten c

    def __post_init__(self):
        if self.kind not in ("potenz", "saettigung", "schwelle", "fixkosten"):
            raise ValueError(f"unbekanntes Basisspiel: {self.kind}")
        if self.kind == "potenz" and self.param <= 0:
            raise ValueError("der Exponent muss positiv sein")


def base_value(game: BaseGame, x, m):
    """Wert einer Gruppe aus Fuhrpark-Summe x und Zahl m der Betriebe (Skalar oder Array); die leere Gruppe ist 0 wert.

    potenz: x^a (a > 1 Skaleneffekt, a < 1 Überlastung, a = 1 additiv); saettigung: x·min(x, K); schwelle: 1, wenn x ≥ t, sonst 0;
    fixkosten: x − c für Gruppen mit mindestens 2 Betrieben (c < 0: Abstimmungsgewinn), ein einzelner Betrieb ist x wert."""
    x = np.asarray(x, dtype=float)
    m = np.asarray(m)
    if game.kind == "potenz":
        out = np.power(x, game.param)
    elif game.kind == "saettigung":
        out = x * np.minimum(x, game.param)
    elif game.kind == "schwelle":
        out = np.where(x >= game.param - 1e-12, 1.0, 0.0)
    else:
        out = np.where(m >= 2, x - game.param, x)
    return np.where(m == 0, 0.0, out)


def adjacency_masks(n: int, edges) -> list[int]:
    """Nachbarn jedes Betriebs als Bitmaske."""
    adj = [0] * n
    for i, j in edges:
        if i == j or not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"ungültige Kante ({i}, {j}) bei n = {n}")
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj


def components_of(adj: list[int], mask: int) -> list[int]:
    """Zusammenhängende Teile der Betriebe in `mask` (Breitensuche über Bitmasken), nach kleinstem Betrieb geordnet."""
    parts = []
    rest = mask
    while rest:
        comp = rest & -rest
        frontier = comp
        while frontier:
            low = frontier & -frontier
            frontier ^= low
            new = adj[low.bit_length() - 1] & rest & ~comp
            comp |= new
            frontier |= new
        parts.append(comp)
        rest &= ~comp
    return parts


def _sum_and_size(n: int, weights):
    """Fuhrpark-Summe und Gruppengröße für alle 2^n Masken (Verdopplung: Maske = alte Maske plus ein Betrieb)."""
    sums = np.zeros(1 << n)
    size = np.zeros(1 << n, dtype=np.int16)
    for b in range(n):
        sums[1 << b: 1 << (b + 1)] = sums[: 1 << b] + weights[b]
        size[1 << b: 1 << (b + 1)] = size[: 1 << b] + 1
    return sums, size


def base_vector(n: int, weights, game: BaseGame) -> np.ndarray:
    """Basiswert v(S) aller 2^n Gruppen, Index = Bitmaske."""
    sums, size = _sum_and_size(n, weights)
    return np.asarray(base_value(game, sums, size), dtype=float)


def restricted_value(adj: list[int], weights, game: BaseGame, mask: int) -> float:
    """v^G(S) einer einzelnen Teilmenge: Summe der Basiswerte ihrer zusammenhängenden Teile (Handweg, ohne Tabellen)."""
    total = 0.0
    for comp in components_of(adj, mask):
        members = [i for i in range(len(adj)) if comp >> i & 1]
        total += float(base_value(game, sum(weights[i] for i in members), len(members)))
    return total


def restricted_vector(n: int, adj: list[int], vbase: np.ndarray) -> np.ndarray:
    """v^G(S) für alle 2^n Teilmengen auf einmal: je Runde wird aus jeder Maske der Teil des kleinsten Betriebs herausgelöst."""
    count = 1 << n
    nb = np.zeros(count, dtype=np.int64)
    for b in range(n):
        nb[1 << b: 1 << (b + 1)] = nb[: 1 << b] | adj[b]
    rest = np.arange(count, dtype=np.int64)
    total = np.zeros(count)
    active = np.nonzero(rest)[0]
    while active.size:
        r = rest[active]
        comp = r & -r
        while True:
            grown = (comp | nb[comp]) & r
            if np.array_equal(grown, comp):
                break
            comp = grown
        total[active] += vbase[comp]
        rest[active] = r & ~comp
        active = active[rest[active] != 0]
    return total


def shapley_vector(players: int, values: np.ndarray) -> np.ndarray:
    """Shapley-Wert aus dem Wertevektor über alle 2^players Koalitionen (Gewicht |S|!(p-|S|-1)!/p!)."""
    if players == 0:
        return np.zeros(0)
    pc = np.zeros(1 << players, dtype=np.int16)
    for b in range(players):
        pc[1 << b: 1 << (b + 1)] = pc[: 1 << b] + 1
    wt = np.array([math.factorial(s) * math.factorial(players - s - 1) / math.factorial(players) for s in range(players)])
    phi = np.zeros(players)
    for i in range(players):
        v2 = values.reshape(-1, 2, 1 << i)
        p2 = pc.reshape(-1, 2, 1 << i)
        phi[i] = float((wt[p2[:, 0, :]] * (v2[:, 1, :] - v2[:, 0, :])).sum())
    return phi


def myerson_exact(n: int, edges, weights, game: BaseGame) -> np.ndarray:
    """Myerson-Wert: Shapley-Wert des eingeschränkten Spiels, Zählweg über alle 2^n Teilmengen."""
    if n == 0:
        return np.zeros(0)
    adj = adjacency_masks(n, edges)
    vg = restricted_vector(n, adj, base_vector(n, weights, game))
    return shapley_vector(n, vg)


def shapley_plain(n: int, weights, game: BaseGame) -> np.ndarray:
    """Shapley-Wert des Basisspiels ohne Netz: jede Gruppe darf sich bilden."""
    if n == 0:
        return np.zeros(0)
    return shapley_vector(n, base_vector(n, weights, game))


def myerson_sample(n: int, edges, weights, game: BaseGame, m: int, seed: int):
    """Stichprobe von m zufälligen Reihenfolgen (SplitMix64, Fisher-Yates); der Grenzbeitrag eines eintretenden Betriebs ist der Wert der
    verschmolzenen Gruppe minus die Werte der bisherigen Gruppen, die er verbindet (Union-Find). Liefert (Mittel, Standardfehler) je Betrieb."""
    if m < 1:
        raise ValueError("m muss mindestens 1 sein")
    nbrs = [[] for _ in range(n)]
    for i, j in edges:
        nbrs[i].append(j)
        nbrs[j].append(i)
    rng = SplitMix64(seed)
    acc = np.zeros(n)
    acc2 = np.zeros(n)
    order = list(range(n))
    val = lambda x, k: float(base_value(game, x, k))   # noqa: E731
    for _ in range(m):
        for i in range(n - 1, 0, -1):
            j = int(rng.uniform() * (i + 1))
            order[i], order[j] = order[j], order[i]
        parent = list(range(n))
        wsum = [float(w) for w in weights]
        size = [1] * n
        present = [False] * n
        for i in order:
            present[i] = True
            roots = set()
            for j in nbrs[i]:
                if present[j]:
                    r = j
                    while parent[r] != r:
                        parent[r] = parent[parent[r]]
                        r = parent[r]
                    roots.add(r)
            old = 0.0
            tot_w, tot_s = float(weights[i]), 1
            for r in roots:
                old += val(wsum[r], size[r])
                tot_w += wsum[r]
                tot_s += size[r]
                parent[r] = i
            wsum[i], size[i] = tot_w, tot_s
            marg = val(tot_w, tot_s) - old
            acc[i] += marg
            acc2[i] += marg * marg
    mean = acc / m
    var = np.maximum(acc2 / m - mean * mean, 0.0)
    return mean, np.sqrt(var / m)


def myerson_star(k: int, f) -> list[float]:
    """Handformel für den Stern (Nabe 0, k Blätter, gleiche Fuhrparks): f(j) = Wert einer Gruppe mit j Betrieben, f(0) = 0.
    Die Nabe tritt an gleichverteilter Stelle j = 0, …, k ein und bringt f(j + 1) − j·f(1); jedes Blatt bekommt den gleichen Rest von f(k + 1)."""
    phi_c = sum(f(j + 1) - j * f(1) for j in range(k + 1)) / (k + 1)
    leaf = (f(k + 1) - phi_c) / k
    return [phi_c] + [leaf] * k
