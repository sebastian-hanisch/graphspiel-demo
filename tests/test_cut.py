"""Verbindung kappen und Positionswert gegen Handrechnung (Pfad aus 3 Betrieben, v = |S|²)."""

import pytest

import gsd_cut as K
import gsd_games as G
from gsd_games import BaseGame

SQ = BaseGame("potenz", 2.0)


def test_cut_of_the_path_by_hand(path3):
    """Ohne den Vertrag 0-1: Teile {0, 2} (Wert 4) und {1} (Wert 1). Werte nachher: Mitte 2, B2 1, B3 2; vorher 11/3, 8/3, 8/3; Verluste 5/3, 5/3, 2/3."""
    n, edges, w = path3
    eff = K.cut_edge(n, edges, w, SQ, (0, 1))
    assert eff.after == pytest.approx((2.0, 1.0, 2.0))
    assert list(eff.change) == pytest.approx([-5 / 3, -5 / 3, -2 / 3])
    assert eff.end_change == pytest.approx((-5 / 3, -5 / 3)) and eff.is_bridge


def test_cut_in_a_ring_is_not_a_bridge_and_the_changes_sum_to_zero():
    from gsd_scenario import ring_edges
    edges = ring_edges(6)
    eff = K.cut_edge(6, edges, (1,) * 6, SQ, edges[0])
    assert not eff.is_bridge
    assert eff.change.sum() == pytest.approx(0.0, abs=1e-12)       # Effizienz: der Wert der großen Koalition bleibt


def test_third_party_changes_split_into_neighbours_and_others():
    from gsd_scenario import path_edges
    edges = path_edges(5)                                              # 0-1-2-3-4, Vertrag 1-2 fällt weg
    eff = K.cut_edge(5, edges, (1,) * 5, SQ, (1, 2))
    near, far = eff.third_changes(edges)
    assert len(near) == 2 and len(far) == 1                            # Nachbarn: 0 und 3; übrig: 4


def test_cut_of_a_missing_edge_raises(path3):
    n, edges, w = path3
    with pytest.raises(ValueError):
        K.cut_edge(n, edges, w, SQ, (1, 2))


def test_position_value_of_the_path_by_hand(path3):
    """Verträge als Spieler: r(∅) = 3, r({e1}) = r({e2}) = 5, r(beide) = 9; je Vertrag 3. Mitte 1 + 3 = 4, Enden 1 + 1,5 = 2,5."""
    n, edges, w = path3
    assert K.position_value(n, edges, w, SQ) == pytest.approx([4.0, 2.5, 2.5])


def test_position_value_is_efficient_and_differs_from_the_myerson_value(path3):
    n, edges, w = path3
    pos = K.position_value(n, edges, w, SQ)
    assert pos.sum() == pytest.approx(9.0)
    assert not pos == pytest.approx(G.myerson_exact(n, edges, w, SQ))      # 4 gegen 11/3: nicht gleich, auch nicht auf Bäumen


def test_position_value_without_edges_is_the_single_values():
    assert K.position_value(3, (), (1, 2, 3), SQ) == pytest.approx([1.0, 4.0, 9.0])
