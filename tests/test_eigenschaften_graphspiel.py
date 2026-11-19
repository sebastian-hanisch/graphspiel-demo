"""Eigenschaftstests (metamorph, ORACLE-PLAYBOOK §5.2): Aussagen über den Myerson-Wert, die ohne Kenntnis des richtigen Ergebnisses gelten müssen."""

import numpy as np
import pytest

import gsd_games as G
from gsd_cut import cut_edge
from gsd_games import BaseGame
from gsd_rng import SplitMix64
from gsd_scenario import complete_edges, connected_components, make_edges, random_net_edges, ring_edges

GAMES = [BaseGame("potenz", 0.5), BaseGame("potenz", 2.0), BaseGame("saettigung", 3.0), BaseGame("schwelle", 3.0), BaseGame("fixkosten", 0.5)]


def _nets(count=25, n_lo=4, n_hi=8):
    for idx in range(count):
        rng = SplitMix64(2000 + idx)
        n = n_lo + idx % (n_hi - n_lo + 1)
        edges = random_net_edges(n, 0.3, rng)
        weights = tuple((1, 2, 3, 5)[int(rng.uniform() * 4)] for _ in range(n))
        yield n, edges, weights


def test_efficiency_in_every_component_of_a_disconnected_net():
    """Netz ohne Verbindung zwischen zwei Teilen: jeder Teil verteilt genau seinen Basiswert (Komponenten-Effizienz)."""
    for idx in range(20):
        rng = SplitMix64(3000 + idx)
        left = random_net_edges(4, 0.5, rng)
        right = tuple((i + 4, j + 4) for i, j in random_net_edges(3, 0.6, rng))
        edges, weights = left + right, tuple((1, 2, 3, 5)[int(rng.uniform() * 4)] for _ in range(7))
        for game in GAMES:
            phi = G.myerson_exact(7, edges, weights, game)
            for comp in connected_components(7, edges):
                value = float(G.base_value(game, sum(weights[i] for i in comp), len(comp)))
                assert sum(phi[i] for i in comp) == pytest.approx(value, abs=1e-9), (idx, game, comp)


def test_efficiency_of_the_connected_net_is_the_value_of_the_grand_coalition():
    for n, edges, weights in _nets():
        for game in GAMES:
            total = float(G.base_value(game, sum(weights), n))
            assert G.myerson_exact(n, edges, weights, game).sum() == pytest.approx(total, abs=1e-9)


def test_renaming_the_firms_only_renames_the_values():
    for n, edges, weights in _nets(15):
        perm = list(np.random.default_rng(n).permutation(n))        # Umnummerierung; die Werte selbst kommen aus der Demo
        edges2 = tuple((perm[i], perm[j]) for i, j in edges)
        weights2 = [0] * n
        for i in range(n):
            weights2[perm[i]] = weights[i]
        for game in GAMES:
            before = G.myerson_exact(n, edges, weights, game)
            after = G.myerson_exact(n, edges2, tuple(weights2), game)
            assert [after[perm[i]] for i in range(n)] == pytest.approx(list(before), abs=1e-9)


def test_additive_base_game_gives_every_firm_its_own_fleet():
    for n, edges, weights in _nets():
        assert G.myerson_exact(n, edges, weights, BaseGame("potenz", 1.0)) == pytest.approx([float(w) for w in weights], abs=1e-9)


def test_ring_and_complete_net_with_equal_fleets_give_equal_shares():
    for n in (3, 4, 7, 10):
        for game in GAMES:
            total = float(G.base_value(game, n, n))
            for edges in (ring_edges(n), complete_edges(n)):
                assert G.myerson_exact(n, edges, (1,) * n, game) == pytest.approx([total / n] * n, abs=1e-9)


def test_complete_net_equals_shapley_without_net_for_any_fleets():
    for n, _edges, weights in _nets(12):
        for game in GAMES:
            assert G.myerson_exact(n, complete_edges(n), weights, game) == pytest.approx(G.shapley_plain(n, weights, game), abs=1e-9)


def test_leaves_of_a_star_are_symmetric():
    phi = G.myerson_exact(8, tuple((0, i) for i in range(1, 8)), (1,) * 8, BaseGame("potenz", 2.0))
    assert phi[1:] == pytest.approx([phi[1]] * 7)


def test_equal_loss_of_both_ends_on_random_nets():
    """Gleichverlust (Fairness): beim Kappen einer Verbindung ändern sich beide Enden um denselben Betrag, für jedes Basisspiel."""
    count = 0
    for n, edges, weights in _nets(20):
        for game in GAMES:
            for e in edges:
                eff = cut_edge(n, edges, weights, game, e)
                ci, cj = eff.end_change
                assert ci == pytest.approx(cj, abs=1e-9), (n, edges, e, game)
                count += 1
    assert count > 300


def test_scaling_the_base_game_scales_the_values():
    """Der Myerson-Wert ist linear im Basisspiel: ein Potenzspiel mit Faktor 2 bekommt doppelte Werte (über die Gewichte nachgebildet: x^a mit a fest, Gewichte gleich)."""
    for n, edges, weights in _nets(10):
        base = G.myerson_exact(n, edges, weights, BaseGame("potenz", 2.0))
        wsum = G.base_vector(n, weights, BaseGame("potenz", 2.0))
        adj = G.adjacency_masks(n, edges)
        doubled = G.shapley_vector(n, G.restricted_vector(n, adj, 2.0 * wsum))
        assert doubled == pytest.approx(2.0 * base, abs=1e-9)


def test_net_families_connected_and_value_totals_for_all_families():
    from gsd_constants import FAMILIES
    for family in FAMILIES:
        edges = make_edges(family, 7, SplitMix64(5))
        assert len(connected_components(7, edges)) == 1, family
