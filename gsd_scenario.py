"""Szenario: Netze (Kantenlisten), Fuhrparkgewichte, Layout. Alle Zufallsziehungen laufen über SplitMix64 (gsd_rng)."""

import math

import numpy as np

import gsd_constants as C
from gsd_rng import SplitMix64


def _norm(edges) -> tuple:
    """Kanten als sortierte, duplikatfreie Paare (i, j) mit i < j."""
    return tuple(sorted({(min(i, j), max(i, j)) for i, j in edges if i != j}))


def star_edges(n: int) -> tuple:
    return _norm((0, i) for i in range(1, n))


def path_edges(n: int) -> tuple:
    return _norm((i, i + 1) for i in range(n - 1))


def ring_edges(n: int) -> tuple:
    return _norm((i, (i + 1) % n) for i in range(n)) if n >= 3 else path_edges(n)


def complete_edges(n: int) -> tuple:
    return _norm((i, j) for i in range(n) for j in range(i + 1, n))


def barbell_edges(n: int) -> tuple:
    """Zwei Cliquen (n // 2 und der Rest), durch eine Brücke zwischen dem letzten Betrieb der ersten und dem ersten der zweiten Clique verbunden."""
    a = n // 2
    first = [(i, j) for i in range(a) for j in range(i + 1, a)]
    second = [(i, j) for i in range(a, n) for j in range(i + 1, n)]
    bridge = [(a - 1, a)] if 0 < a < n else []
    return _norm(first + second + bridge)


def connected_components(n: int, edges) -> list[list[int]]:
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    seen = [False] * n
    out = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp, stack = [], [s]
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        out.append(sorted(comp))
    return out


def random_net_edges(n: int, p: float, rng: SplitMix64) -> tuple:
    """Zufallsnetz G(n, p); die Komponenten werden durch je eine Zufallskante zur nächsten verbunden (immer zusammenhängend)."""
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.uniform() < p]
    comps = connected_components(n, edges)
    for c1, c2 in zip(comps, comps[1:]):
        edges.append((c1[int(rng.uniform() * len(c1))], c2[int(rng.uniform() * len(c2))]))
    return _norm(edges)


def random_tree_edges(n: int, rng: SplitMix64) -> tuple:
    """Zufallsbaum: Betrieb i hängt sich an einen gleichverteilt gezogenen früheren Betrieb."""
    return _norm((int(rng.uniform() * i), i) for i in range(1, n))


def attachment_edges(n: int, rng: SplitMix64, m: int = 2) -> tuple:
    """Preferential Attachment: jeder neue Betrieb verbindet sich mit bis zu m früheren, gezogen proportional zum Grad."""
    if n < 2:
        return ()
    edges, ends = [(0, 1)], [0, 1]
    for v in range(2, n):
        targets = set()
        while len(targets) < min(m, v):
            targets.add(ends[int(rng.uniform() * len(ends))])
        for t in sorted(targets):
            edges.append((t, v))
            ends += [t, v]
    return _norm(edges)


def make_edges(family: str, n: int, rng: SplitMix64) -> tuple:
    """Netz einer Familie; feste Familien verbrauchen keinen Zufall."""
    if family == "Stern":
        return star_edges(n)
    if family == "Pfad":
        return path_edges(n)
    if family == "Ring":
        return ring_edges(n)
    if family == "Hantel":
        return barbell_edges(n)
    if family == "Vollständig":
        return complete_edges(n)
    if family == "Zufallsnetz dünn":
        return random_net_edges(n, C.P_THIN, rng)
    if family == "Zufallsnetz dicht":
        return random_net_edges(n, C.P_DENSE, rng)
    if family == "Zufallsbaum":
        return random_tree_edges(n, rng)
    if family == "Preferential Attachment":
        return attachment_edges(n, rng)
    raise ValueError(f"unbekannte Netzfamilie: {family}")


def make_weights(mode: str, n: int, rng: SplitMix64) -> tuple:
    """Fuhrparkgrößen: alle 1 oder je Betrieb gleichverteilt aus WEIGHT_CHOICES."""
    if mode == C.WEIGHT_MODES[0]:
        return (1,) * n
    if mode == C.WEIGHT_MODES[1]:
        return tuple(C.WEIGHT_CHOICES[int(rng.uniform() * len(C.WEIGHT_CHOICES))] for _ in range(n))
    raise ValueError(f"unbekannte Gewichtsart: {mode}")


def make_instance(family: str, n: int, weight_mode: str, seed: int):
    """Netz und Gewichte aus (Familie, n, Gewichtsart, Zufalls-Seed): getrennte Zufallsströme, damit ein Wechsel der Gewichtsart das Netz nicht ändert."""
    edges = make_edges(family, n, SplitMix64(seed))
    weights = make_weights(weight_mode, n, SplitMix64(seed + 7919))
    return edges, weights


def degrees(n: int, edges) -> list[int]:
    deg = [0] * n
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    return deg


def layout_positions(n: int, edges, iterations: int = 120) -> np.ndarray:
    """Deterministische Knotenpositionen (Fruchterman-Reingold, Start auf dem Kreis), Form (n, 2), in [-1, 1]."""
    if n == 0:
        return np.zeros((0, 2))
    ang = 2 * math.pi * np.arange(n) / n
    pos = np.column_stack([np.cos(ang), np.sin(ang)])
    if n == 1:
        return np.zeros((1, 2))
    k = 1.0 / math.sqrt(n)
    e = np.array(edges, dtype=int).reshape(-1, 2)
    t = 0.1
    for _ in range(iterations):
        d = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(d, axis=2) + np.eye(n)
        disp = (d / dist[:, :, None] * (k * k / dist)[:, :, None]).sum(axis=1)
        if len(e):
            ed = pos[e[:, 0]] - pos[e[:, 1]]
            el = np.linalg.norm(ed, axis=1) + 1e-9
            f = (ed / el[:, None]) * (el * el / k)[:, None]
            np.add.at(disp, e[:, 0], -f)
            np.add.at(disp, e[:, 1], f)
        length = np.linalg.norm(disp, axis=1) + 1e-9
        pos = pos + disp / length[:, None] * np.minimum(length, t)[:, None]
        t *= 0.97
    pos = pos - pos.mean(axis=0)
    scale = np.abs(pos).max()
    return pos / scale if scale > 0 else pos
