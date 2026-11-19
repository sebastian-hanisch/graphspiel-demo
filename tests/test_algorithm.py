"""Kern gegen Handrechnung auf den Mini-Instanzen: jede Einheit einzeln (Basisspiel, Teile, eingeschränktes Spiel, Shapley, Myerson, Stern, Stichprobe)."""

import math

import numpy as np
import pytest

import gsd_games as G
from gsd_games import BaseGame

SQ = BaseGame("potenz", 2.0)


def test_base_value_potenz_saettigung_schwelle_fixkosten():
    assert G.base_value(SQ, 3.0, 3) == pytest.approx(9.0)
    assert G.base_value(BaseGame("potenz", 0.5), 4.0, 2) == pytest.approx(2.0)
    assert G.base_value(BaseGame("saettigung", 3.0), 2.0, 2) == pytest.approx(4.0)      # 2 · min(2, 3)
    assert G.base_value(BaseGame("saettigung", 3.0), 5.0, 5) == pytest.approx(15.0)     # 5 · min(5, 3)
    assert G.base_value(BaseGame("schwelle", 3.0), 2.0, 2) == 0.0
    assert G.base_value(BaseGame("schwelle", 3.0), 3.0, 3) == 1.0                       # Schwelle inklusive
    assert G.base_value(BaseGame("fixkosten", 0.5), 1.0, 1) == pytest.approx(1.0)       # ein Betrieb zahlt keine Fixkosten
    assert G.base_value(BaseGame("fixkosten", 0.5), 3.0, 3) == pytest.approx(2.5)
    assert G.base_value(BaseGame("fixkosten", -1.0), 2.0, 2) == pytest.approx(3.0)      # Abstimmungsgewinn


def test_empty_group_is_worth_zero_for_every_game():
    for g in (SQ, BaseGame("saettigung", 3.0), BaseGame("schwelle", 3.0), BaseGame("fixkosten", -1.0), BaseGame("potenz", 0.5)):
        assert G.base_value(g, 0.0, 0) == 0.0


def test_unknown_game_and_nonpositive_exponent_raise():
    with pytest.raises(ValueError):
        BaseGame("unbekannt", 1.0)
    with pytest.raises(ValueError):
        BaseGame("potenz", 0.0)


def test_components_of_splits_a_group_at_missing_contracts(path3):
    n, edges, _w = path3
    adj = G.adjacency_masks(n, edges)
    assert G.components_of(adj, 0b111) == [0b111]
    assert G.components_of(adj, 0b110) == [0b010, 0b100]       # ohne die Mitte sind die Enden getrennt
    assert G.components_of(adj, 0b011) == [0b011]
    assert G.components_of(adj, 0) == []


def test_restricted_value_by_hand(path3):
    n, edges, w = path3
    adj = G.adjacency_masks(n, edges)
    assert G.restricted_value(adj, w, SQ, 0b111) == pytest.approx(9.0)
    assert G.restricted_value(adj, w, SQ, 0b011) == pytest.approx(4.0)
    assert G.restricted_value(adj, w, SQ, 0b110) == pytest.approx(2.0)      # zwei getrennte Einzelne: 1 + 1 statt 4
    assert G.restricted_value(adj, w, SQ, 0) == 0.0


def test_restricted_vector_equals_the_single_value_function_on_all_masks(path3):
    n, edges, w = path3
    adj = G.adjacency_masks(n, edges)
    vec = G.restricted_vector(n, adj, G.base_vector(n, w, SQ))
    assert [float(x) for x in vec] == pytest.approx([G.restricted_value(adj, w, SQ, m) for m in range(1 << n)])


def test_shapley_of_a_unanimity_game_is_one_over_n():
    values = np.zeros(1 << 4)
    values[-1] = 1.0
    assert G.shapley_vector(4, values) == pytest.approx([0.25] * 4)


def test_myerson_value_of_the_path_by_hand(path3):
    n, edges, w = path3
    assert G.myerson_exact(n, edges, w, SQ) == pytest.approx([11 / 3, 8 / 3, 8 / 3])
    assert G.shapley_plain(n, w, SQ) == pytest.approx([3.0, 3.0, 3.0])


def test_myerson_value_of_the_path_with_square_root_by_hand(path3):
    """v = √|S|: die Mitte tritt an Stelle 1, 2 oder 3 ein und bringt f(1) bzw. f(2) − f(1) bzw. f(3) − 2 f(1)."""
    n, edges, w = path3
    mid = (1.0 + (math.sqrt(2) - 1.0) + (math.sqrt(3) - 2.0)) / 3
    leaf = (math.sqrt(3) - mid) / 2
    assert G.myerson_exact(n, edges, w, BaseGame("potenz", 0.5)) == pytest.approx([mid, leaf, leaf])


def test_star_formula_equals_the_counting_way():
    for k in (2, 5, 9):
        for a in (0.5, 2.0):
            f = lambda j, a=a: 0.0 if j == 0 else float(j) ** a   # noqa: E731
            edges = tuple((0, i) for i in range(1, k + 1))
            assert G.myerson_exact(k + 1, edges, (1,) * (k + 1), BaseGame("potenz", a)) == pytest.approx(G.myerson_star(k, f))


def test_star_with_ten_firms_and_square_by_hand():
    """Nabe: (1/10) Σ_{j=0}^{9} ((j+1)² − j) = (1/10)(Σ (j+1)² − Σ j) = (385 − 45)/10 = 34, jedes Blatt (100 − 34)/9 = 22/3."""
    star = tuple((0, i) for i in range(1, 10))
    phi = G.myerson_exact(10, star, (1,) * 10, SQ)
    assert phi[0] == pytest.approx(34.0)
    assert phi[1:] == pytest.approx([22 / 3] * 9)


def test_sample_is_close_to_the_exact_value(path3):
    n, edges, w = path3
    mean, se = G.myerson_sample(n, edges, w, SQ, 20000, 5)
    assert np.all(np.abs(mean - np.array([11 / 3, 8 / 3, 8 / 3])) <= 4 * se + 1e-12)


def test_sample_is_deterministic_for_one_seed_and_differs_between_seeds(path3):
    n, edges, w = path3
    a1, _ = G.myerson_sample(n, edges, w, SQ, 50, 1)
    a2, _ = G.myerson_sample(n, edges, w, SQ, 50, 1)
    b, _ = G.myerson_sample(n, edges, w, SQ, 50, 2)
    assert np.array_equal(a1, a2) and not np.array_equal(a1, b)


def test_sample_needs_at_least_one_order(path3):
    n, edges, w = path3
    with pytest.raises(ValueError):
        G.myerson_sample(n, edges, w, SQ, 0, 1)


def test_invalid_edges_raise():
    with pytest.raises(ValueError):
        G.adjacency_masks(3, ((0, 3),))
    with pytest.raises(ValueError):
        G.adjacency_masks(3, ((1, 1),))
