"""Zentralitäten und Rangkorrelation gegen networkx und scipy; Handwerte an kleinen Netzen."""

import numpy as np
import pytest

import gsd_centrality as Z
from gsd_constants import FAMILIES
from gsd_rng import SplitMix64
from gsd_scenario import make_edges, path_edges, star_edges

nx = pytest.importorskip("networkx")


def test_star_by_hand():
    """Stern mit 3 Betrieben (Mitte 0): Grad 2, 1, 1; Nähe der Mitte 1, der Enden 2/3; Zwischen der Mitte 1 (der eine Weg zwischen den Enden)."""
    edges = star_edges(3)
    assert Z.degree_centrality(3, edges) == [2, 1, 1]
    assert Z.closeness_centrality(3, edges) == pytest.approx([1.0, 2 / 3, 2 / 3])
    assert Z.betweenness_centrality(3, edges) == pytest.approx([1.0, 0.0, 0.0])


def test_path_of_four_by_hand():
    """Pfad 0-1-2-3: Zwischen der inneren Betriebe je 2 von 3 Paaren (0,2), (0,3) bzw. (0,3), (1,3), normiert 2/3."""
    assert Z.betweenness_centrality(4, path_edges(4)) == pytest.approx([0.0, 2 / 3, 2 / 3, 0.0])


def test_against_networkx_on_all_families_and_sizes():
    for family in FAMILIES:
        for n in (3, 5, 8, 12):
            edges = make_edges(family, n, SplitMix64(n))
            graph = nx.Graph()
            graph.add_nodes_from(range(n))
            graph.add_edges_from(edges)
            clo, bet = nx.closeness_centrality(graph), nx.betweenness_centrality(graph)
            assert Z.closeness_centrality(n, edges) == pytest.approx([clo[i] for i in range(n)]), (family, n)
            assert Z.betweenness_centrality(n, edges) == pytest.approx([bet[i] for i in range(n)]), (family, n)
            assert Z.degree_centrality(n, edges) == [graph.degree(i) for i in range(n)]


def test_rank_correlation_against_scipy_with_ties():
    stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(3)
    for _ in range(30):
        a, b = rng.integers(0, 5, 9), rng.integers(0, 5, 9)
        expected = stats.spearmanr(a, b).statistic
        if np.isnan(expected):
            assert Z.rank_correlation(a, b) is None
        else:
            assert Z.rank_correlation(a, b) == pytest.approx(expected, abs=1e-12)


def test_average_ranks_by_hand():
    assert list(Z.average_ranks([10, 20, 20, 5])) == [2.0, 3.5, 3.5, 1.0]


def test_rank_correlation_undefined_for_constant_side_and_tiny_input():
    assert Z.rank_correlation([1, 1, 1], [1, 2, 3]) is None
    assert Z.rank_correlation([1.0], [2.0]) is None
    assert Z.rank_correlation([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)
