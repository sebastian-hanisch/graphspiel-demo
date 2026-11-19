"""Netzfamilien, Gewichte, Layout: Kantenzahlen von Hand, Zusammenhang, Determinismus."""

import numpy as np
import pytest

import gsd_constants as C
from gsd_rng import SplitMix64
from gsd_scenario import (
    barbell_edges,
    complete_edges,
    connected_components,
    degrees,
    layout_positions,
    make_edges,
    make_instance,
    make_weights,
    path_edges,
    ring_edges,
    star_edges,
)


def test_edge_counts_of_the_fixed_families_by_hand():
    n = 10
    assert len(star_edges(n)) == 9 and len(path_edges(n)) == 9 and len(ring_edges(n)) == 10
    assert len(complete_edges(n)) == 45                      # 10 · 9 / 2
    assert len(barbell_edges(n)) == 2 * 10 + 1               # zwei Fünfer-Cliquen mit je 10 Kanten plus Brücke


def test_barbell_has_one_bridge_between_the_two_cliques():
    edges = barbell_edges(10)
    assert (4, 5) in edges
    assert sum(1 for i, j in edges if i < 5 <= j) == 1


def test_degrees_of_the_star_and_the_ring():
    assert degrees(5, star_edges(5)) == [4, 1, 1, 1, 1]
    assert degrees(6, ring_edges(6)) == [2] * 6


def test_every_family_is_connected_for_many_sizes_and_seeds():
    for family in C.FAMILIES:
        for n in range(C.N_MIN, C.N_MAX + 1):
            for seed in (0, 1, 35, 999999):
                edges = make_edges(family, n, SplitMix64(seed))
                assert len(connected_components(n, edges)) == 1, (family, n, seed)
                assert all(0 <= i < j < n for i, j in edges) and len(set(edges)) == len(edges)


def test_trees_and_preferential_attachment_edge_counts():
    for seed in range(10):
        assert len(make_edges("Zufallsbaum", 9, SplitMix64(seed))) == 8
        assert len(make_edges("Preferential Attachment", 9, SplitMix64(seed))) == 1 + 2 * 7       # erste Kante plus zwei je neuem Betrieb ab Betrieb 3


def test_same_seed_same_net_other_seed_other_net():
    a = make_instance("Zufallsnetz dünn", 10, C.WEIGHT_MODES[1], 7)
    assert a == make_instance("Zufallsnetz dünn", 10, C.WEIGHT_MODES[1], 7)
    nets = {make_instance("Zufallsnetz dünn", 10, C.WEIGHT_MODES[0], s)[0] for s in range(10)}
    assert len(nets) > 5


def test_weights_change_with_the_mode_but_not_the_net():
    e1, w1 = make_instance("Zufallsnetz dicht", 10, C.WEIGHT_MODES[0], 5)
    e2, w2 = make_instance("Zufallsnetz dicht", 10, C.WEIGHT_MODES[1], 5)
    assert e1 == e2 and w1 == (1,) * 10 and set(w2) <= set(C.WEIGHT_CHOICES) and len(set(w2)) > 1


def test_unknown_family_and_weight_mode_raise():
    with pytest.raises(ValueError):
        make_edges("Gitter", 5, SplitMix64(1))
    with pytest.raises(ValueError):
        make_weights("irgendwie", 5, SplitMix64(1))


def test_layout_is_deterministic_finite_and_inside_the_unit_square():
    edges = make_edges("Hantel", 10, SplitMix64(1))
    p1, p2 = layout_positions(10, edges), layout_positions(10, edges)
    assert np.array_equal(p1, p2) and np.isfinite(p1).all() and np.abs(p1).max() <= 1.0 + 1e-12
    assert layout_positions(1, ()).shape == (1, 2) and layout_positions(0, ()).shape == (0, 2)
