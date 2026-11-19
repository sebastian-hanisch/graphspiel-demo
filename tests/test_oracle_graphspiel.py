"""Orakel-Test graphspiel-demo: der Zählweg über 2^n Teilmengen gegen drei unabhängige Rechenwege.

A: Aufzählung aller Reihenfolgen, Teile per networkx (nutzt weder Bitmasken noch die Shapley-Gewichte der Demo).
B: Fairness-Rekursion über Kantenmengen (Myerson 1977: Komponenten-Effizienz + Gleichverlust kennzeichnen den Wert; kein Teilmengen-Code).
C: Harsanyi-Dividenden zusammenhängender Mengen (Möbius-Umkehrung des eingeschränkten Spiels; Dividenden nicht zusammenhängender Mengen sind 0).
Dazu: Stichprobe gegen exakt (4 Standardfehler); die Zentralitäten gegen networkx stehen in test_centrality.py.
Das Orakel wurde vorher an der Handrechnung Pfad aus 3 Betrieben geprüft (11/3, 8/3, 8/3; test_oracle_hand_example)."""

import itertools
import math
from functools import lru_cache

import numpy as np
import pytest

import gsd_games as G
from gsd_games import BaseGame
from gsd_rng import SplitMix64
from gsd_scenario import attachment_edges, barbell_edges, complete_edges, make_edges, random_net_edges, random_tree_edges

nx = pytest.importorskip("networkx")

GAMES = [BaseGame("potenz", 0.5), BaseGame("potenz", 2.0), BaseGame("potenz", 1.5), BaseGame("schwelle", 3.0), BaseGame("saettigung", 3.0),
         BaseGame("fixkosten", 0.5), BaseGame("fixkosten", -1.0)]


def _vfun(weights, game):
    return lambda nodes: float(G.base_value(game, sum(weights[i] for i in nodes), len(nodes)))


def oracle_permutations(n, edges, vfun):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(edges)
    vg = {}
    for mask in range(1 << n):
        members = [i for i in range(n) if mask >> i & 1]
        vg[mask] = sum(vfun(frozenset(c)) for c in nx.connected_components(graph.subgraph(members)))
    phi = [0.0] * n
    for perm in itertools.permutations(range(n)):
        mask = 0
        for i in perm:
            phi[i] += vg[mask | 1 << i] - vg[mask]
            mask |= 1 << i
    return [x / math.factorial(n) for x in phi]


def oracle_fairness(n, edges, vfun):
    """Rekursion: je zusammenhängendem Teil Summe = v(Teil); je Kante gleiche Änderung an beiden Enden beim Entfernen der Kante."""
    all_edges = frozenset(frozenset(e) for e in edges)

    def comps(nodes, es):
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from([tuple(e) for e in es])
        return [frozenset(c) for c in nx.connected_components(graph)]

    @lru_cache(maxsize=None)
    def phi(nodes, es):
        parts = comps(nodes, es)
        if len(parts) > 1:
            out = {}
            for part in parts:
                out.update(phi(part, frozenset(e for e in es if e <= part)))
            return out
        if len(nodes) == 1:
            (i,) = tuple(nodes)
            return {i: vfun(nodes)}
        root = min(nodes)
        order, parent, seen = [root], {}, {root}
        for u in order:
            for e in sorted(es, key=sorted):
                if u in e:
                    (x,) = tuple(e - {u})
                    if x not in seen:
                        seen.add(x)
                        parent[x] = u
                        order.append(x)
        rel = {root: 0.0}
        for x in order[1:]:
            p = parent[x]
            sub = phi(nodes, es - {frozenset((p, x))})
            rel[x] = rel[p] - (sub[p] - sub[x])
        t = (vfun(nodes) - sum(rel.values())) / len(nodes)
        return {x: t + rel[x] for x in nodes}

    result = phi(frozenset(range(n)), all_edges)
    return [result[i] for i in range(n)]


def oracle_dividends(n, edges, vfun):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(edges)
    vg = {}
    for mask in range(1 << n):
        members = [i for i in range(n) if mask >> i & 1]
        vg[mask] = sum(vfun(frozenset(c)) for c in nx.connected_components(graph.subgraph(members)))
    phi = [0.0] * n
    stray = 0
    for t in range(1, 1 << n):
        members = [i for i in range(n) if t >> i & 1]
        div, sub = 0.0, t
        while True:
            div += (-1) ** (len(members) - bin(sub).count("1")) * vg[sub]
            if sub == 0:
                break
            sub = (sub - 1) & t
        if nx.is_connected(graph.subgraph(members)):
            for i in members:
                phi[i] += div / len(members)
        elif abs(div) > 1e-9:
            stray += 1
    return phi, stray


def _instances():
    """60 feste Mini-Instanzen: n = 4 bis 6, sechs Netzfamilien, Gewichte aus {1, 2, 3, 5}, sieben Basisspiele reihum."""
    out = []
    for idx in range(60):
        rng = SplitMix64(1000 + idx)
        n = 4 + idx % 3
        kind = idx % 6
        if kind == 0:
            edges = complete_edges(n)
        elif kind == 1:
            edges = barbell_edges(n)
        elif kind == 2:
            edges = random_tree_edges(n, rng)
        elif kind == 3:
            edges = random_net_edges(n, 0.4, rng)
        elif kind == 4:
            edges = attachment_edges(n, rng)
        else:
            edges = make_edges("Pfad", n, rng)
        weights = tuple((1, 2, 3, 5)[int(rng.uniform() * 4)] for _ in range(n))
        out.append((n, edges, weights, GAMES[idx % len(GAMES)]))
    return out


def test_oracle_hand_example_path_of_three():
    """Das Orakel selbst, an der Handrechnung geprüft: v = |S|², Mitte 11/3, Enden 8/3."""
    vfun = _vfun((1, 1, 1), BaseGame("potenz", 2.0))
    assert oracle_permutations(3, ((0, 1), (0, 2)), vfun) == pytest.approx([11 / 3, 8 / 3, 8 / 3])
    assert oracle_fairness(3, ((0, 1), (0, 2)), vfun) == pytest.approx([11 / 3, 8 / 3, 8 / 3])
    assert oracle_dividends(3, ((0, 1), (0, 2)), vfun)[0] == pytest.approx([11 / 3, 8 / 3, 8 / 3])


def test_counting_way_equals_permutation_oracle_on_60_instances():
    for n, edges, weights, game in _instances():
        mine = G.myerson_exact(n, edges, weights, game)
        assert mine == pytest.approx(oracle_permutations(n, edges, _vfun(weights, game)), abs=1e-9), (n, edges, weights, game)


def test_counting_way_equals_fairness_recursion_on_instances_with_few_edges():
    checked = 0
    for n, edges, weights, game in _instances():
        if len(edges) > 8:
            continue
        mine = G.myerson_exact(n, edges, weights, game)
        assert mine == pytest.approx(oracle_fairness(n, edges, _vfun(weights, game)), abs=1e-9), (n, edges, weights, game)
        checked += 1
    assert checked >= 20


def test_counting_way_equals_harsanyi_dividends_and_stray_dividends_vanish():
    for n, edges, weights, game in _instances():
        phi, stray = oracle_dividends(n, edges, _vfun(weights, game))
        assert G.myerson_exact(n, edges, weights, game) == pytest.approx(phi, abs=1e-9), (n, edges, weights, game)
        assert stray == 0, "Dividenden nicht zusammenhängender Mengen müssen 0 sein"


def test_sample_lies_within_four_standard_errors_of_the_exact_value():
    for idx, (n, edges, weights, game) in enumerate(_instances()[:30]):
        exact = G.myerson_exact(n, edges, weights, game)
        mean, se = G.myerson_sample(n, edges, weights, game, 3000, 500 + idx)
        assert np.all(np.abs(mean - exact) <= 4 * se + 1e-9), (idx, n, edges)


def test_star_formula_matches_the_counting_way_for_many_exponents():
    for k in range(2, 10):
        for a in (0.5, 0.75, 1.5, 2.0, 3.0):
            f = lambda j, a=a: 0.0 if j == 0 else float(j) ** a   # noqa: E731
            star = tuple((0, i) for i in range(1, k + 1))
            assert G.myerson_exact(k + 1, star, (1,) * (k + 1), BaseGame("potenz", a)) == pytest.approx(G.myerson_star(k, f), abs=1e-9)
