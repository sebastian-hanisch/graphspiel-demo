"""Randfälle: n = 1, n = 2, kein Vertrag, Gleichstände, inklusive Grenzen, Bezug 0."""

import numpy as np
import pytest

import gsd_constants as C
import gsd_evaluation as ev
import gsd_games as G
from gsd_games import BaseGame
from gsd_rng import SplitMix64
from gsd_scenario import make_edges

SQ = BaseGame("potenz", 2.0)


def test_exactly_two_firms():
    """n = 2 mit einem Vertrag: der Wert ist v({1, 2}) = 4, gleich verteilt (Symmetrie); ohne Vertrag bekommt jeder v({i}) = 1."""
    assert G.myerson_exact(2, ((0, 1),), (1, 1), SQ) == pytest.approx([2.0, 2.0])
    assert G.myerson_exact(2, (), (1, 1), SQ) == pytest.approx([1.0, 1.0])
    assert G.myerson_exact(2, ((0, 1),), (1, 3), SQ) == pytest.approx([(1 + (16 - 9)) / 2 + 0.0, (9 + (16 - 1)) / 2], abs=1e-9)


def test_single_firm_and_no_firm():
    assert G.myerson_exact(1, (), (2,), SQ) == pytest.approx([4.0])
    assert len(G.myerson_exact(0, (), (), SQ)) == 0 and len(G.shapley_plain(0, (), SQ)) == 0


def test_no_contract_means_every_firm_gets_its_single_value():
    for game in (SQ, BaseGame("saettigung", 3.0), BaseGame("schwelle", 3.0), BaseGame("fixkosten", 0.5)):
        w = (1, 2, 3, 5)
        expected = [float(G.base_value(game, x, 1)) for x in w]
        assert G.myerson_exact(4, (), w, game) == pytest.approx(expected)


def test_ties_hub_ratio_counts_all_firms_with_the_highest_degree():
    """Gleichstand im Höchstgrad: das Verhältnis ist das Mittel über alle Gleichgradigen (Ring: alle)."""
    phi, sh = [1.0, 2.0, 3.0, 4.0], [2.0, 2.0, 2.0, 2.0]
    assert ev.hub_ratio(phi, sh, [3, 3, 1, 1]) == pytest.approx((0.5 + 1.0) / 2)
    assert ev.hub_ratio(phi, sh, [2, 2, 2, 2]) == pytest.approx(10.0 / 8.0)


def test_hub_ratio_is_none_when_the_reference_is_zero_or_the_net_is_empty():
    assert ev.hub_ratio([1.0, 1.0], [0.0, 1.0], [2, 1]) is None
    assert ev.hub_ratio([], [], []) is None


def test_distance_is_zero_without_value():
    assert ev.distance_to_shapley([0.0, 0.0], [0.0, 0.0], 0.0) == 0.0


def test_slider_bounds_are_inclusive_and_exact_for_the_extremes():
    for n in (C.N_MIN, C.N_MAX):
        an = ev.analyse(ev.Settings(n=n))
        assert an.n == n and an.myerson.sum() == pytest.approx(float(n) ** 2)
    assert C.N_MIN >= 3 and C.N_MAX <= C.EXACT_LIMIT_BUTTON


def test_every_family_at_both_slider_bounds_analyses_without_error():
    for family in C.FAMILIES:
        for n in (C.N_MIN, C.N_MAX):
            for game in C.GAMES:
                an = ev.analyse(ev.Settings(family, n, game, C.WEIGHT_MODES[1], 999999))
                assert np.isfinite(an.myerson).all()


def test_regular_net_with_unequal_fleets_has_no_single_hub():
    an = ev.analyse(ev.Settings("Ring", 10, "Quadratisch (a = 2)", C.WEIGHT_MODES[1], 3))
    assert an.equal_degrees and len(an.top_degree_nodes) == 10


def test_net_metrics_top_ok_counts_a_tied_top_firm():
    """Alle Betriebe im Ring liegen gleichauf und haben gleichen Grad: die Spitze ist ein Betrieb höchsten Grades."""
    an = ev.analyse(ev.Settings("Ring", 6, "Quadratisch (a = 2)", C.WEIGHT_MODES[0], 1))
    assert ev.net_metrics(an)["top_ok"] == 1.0 and ev.net_metrics(an)["rho"] is None


def test_sample_with_large_net_runs_and_is_finite():
    edges = make_edges("Preferential Attachment", 60, SplitMix64(9))
    mean, se = G.myerson_sample(60, edges, (1,) * 60, SQ, 20, 9)
    assert np.isfinite(mean).all() and (se >= 0).all()
