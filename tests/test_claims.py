"""Jede Zahl der README wird hier nachgerechnet (mit Bedingung: Basisspiel, Exponent, Netzfamilie, n, Zufalls-Seeds, Zahl der Läufe).

Die Tabellen der README stammen aus tools/readme_rows.py (dieselben Funktionen wie in der App); diese Datei prüft Zeile für Zeile, dass sie in der README stehen.
Messungen mit Rundungsresten (Optimierer gibt es nicht; nur Summationsreihenfolgen) stehen mit Bändern, nicht exakt. Nicht im Test (Messung dieser README):
Laufzeiten und Speicher des exakten Wegs."""

import sys
from pathlib import Path

import numpy as np
import pytest

import gsd_constants as C
import gsd_cut as K
import gsd_evaluation as ev
import gsd_games as G
import gsd_scenario as S
from gsd_centrality import rank_correlation
from gsd_rng import SplitMix64

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import readme_rows as RR  # noqa: E402

README = (ROOT / "README.md").read_text(encoding="utf-8")
SQ = ev.potenz(2.0)


@pytest.fixture(scope="module")
def e1():
    return {(r["family"], r["game"]): r for r in ev.sign_table()}, ev.sign_table()


@pytest.fixture(scope="module")
def e2():
    return ev.cut_table()


@pytest.fixture(scope="module")
def e3():
    return ev.sample_table()


def _at(cell, key, nd):
    return round(cell[key], nd)


# ---------------------------------------------------------------- Handbeispiel und Stern

def test_hand_example_path_of_three_betriebe():
    """Pfad aus 3 Betrieben, Wert einer Gruppe = (Fuhrparks)², gleiche Fuhrparks: Myerson 11/3, 8/3, 8/3; ohne Netz 3, 3, 3; Positionswert 4, 2,5, 2,5."""
    edges = ((0, 1), (0, 2))
    assert G.myerson_exact(3, edges, (1, 1, 1), SQ) == pytest.approx([11 / 3, 8 / 3, 8 / 3])
    assert G.shapley_plain(3, (1, 1, 1), SQ) == pytest.approx([3, 3, 3])
    assert K.position_value(3, edges, (1, 1, 1), SQ) == pytest.approx([4.0, 2.5, 2.5])


def test_star_of_ten_firms_hub_ratio_by_exponent():
    """Stern, n = 10 (eine Nabe, neun Blätter), gleiche Fuhrparks: Myerson-Wert der Nabe geteilt durch den Gleichteil v(N)/n und Anteil D, den das Netz umverteilt."""
    expected = {0.5: (-7.1252, 0.8125), 0.75: (-1.8055, 0.2805), 1.0: (1.0, 0.0), 1.5: (3.0887, 0.2089), 2.0: (3.4, 0.24), 3.0: (2.98, 0.198)}
    for a, (ratio, dist) in expected.items():
        an = ev.analyse_instance(S.star_edges(10), (1,) * 10, ev.potenz(a))
        assert an.hub_ratio == pytest.approx(ratio, abs=1e-3), a
        assert an.distance == pytest.approx(dist, abs=1e-3), a
    assert ev.analyse_instance(S.star_edges(10), (1,) * 10, ev.game_of("Schwelle (t = 3)")).hub_ratio == pytest.approx(8.0)
    # nicht monoton in a: der Höchstwert liegt bei a = 2
    ratios = [ev.analyse_instance(S.star_edges(10), (1,) * 10, ev.potenz(a)).hub_ratio for a in (1.5, 2.0, 3.0)]
    assert max(ratios) == ratios[1]


def test_star_quadratic_exact_values():
    phi = G.myerson_exact(10, S.star_edges(10), (1,) * 10, SQ)
    assert phi[0] == pytest.approx(34.0) and phi[1] == pytest.approx(22 / 3)


def test_hantel_preset_bridge_firms_and_threshold_counterexample():
    """Hantel n = 10 (zwei Fünfer-Cliquen, eine Brücke), gleiche Fuhrparks."""
    an = ev.analyse(ev.Settings("Hantel", 10, "Quadratisch (a = 2)", C.WEIGHT_MODES[0], 35))
    assert an.top_degree_nodes == [4, 5]
    assert an.myerson[4] == pytest.approx(58 / 3) and an.myerson[0] == pytest.approx(23 / 3)      # 19,33 gegen 7,67
    assert an.hub_ratio == pytest.approx(1.9333, abs=1e-3) and an.distance == pytest.approx(0.1867, abs=1e-3)
    th = ev.analyse(ev.Settings("Hantel", 10, "Schwelle (t = 3)", C.WEIGHT_MODES[0], 35))
    assert th.hub_ratio == pytest.approx(-1.1111, abs=1e-3)                                      # beide Brückenbetriebe negativ
    assert th.ratios[0] == pytest.approx(1.5278, abs=1e-3) and th.distance == pytest.approx(0.4222, abs=1e-3)
    assert th.myerson[4] < 0 and th.myerson[5] < 0 and min(th.myerson[:4]) > 0


def test_ring_and_complete_net_have_no_effect_in_every_basisspiel():
    for family in ("Ring", "Vollständig"):
        for game in C.GAMES:
            assert ev.analyse(ev.Settings(family, 10, game, C.WEIGHT_MODES[0], 35)).distance < 1e-9, (family, game)
    assert ev.analyse(ev.Settings("Ring", 10, "Quadratisch (a = 2)", C.WEIGHT_MODES[1], 35)).distance > 1e-3       # ungleiche Fuhrparks: Wirkung


def test_default_zufallsnetz_and_unequal_fleets_presets():
    z = ev.analyse(ev.Settings("Zufallsnetz dünn", 10, "Quadratisch (a = 2)", C.WEIGHT_MODES[0], 35))
    assert z.hub_ratio == pytest.approx(1.2988, abs=1e-3) and z.distance == pytest.approx(0.111, abs=1e-3)
    u = ev.analyse(ev.Settings("Zufallsnetz dünn", 10, "Skaleneffekt (a = 1,5)", C.WEIGHT_MODES[1], 35))
    assert u.hub_ratio == pytest.approx(1.1286, abs=1e-3) and u.distance == pytest.approx(0.0772, abs=1e-3)


# ---------------------------------------------------------------- E1: Zentralität gegen Wert

def test_e1_sign_follows_the_exponent_in_8_of_8_and_12_of_12_cells(e1):
    """Vier Zufallsfamilien (Zufallsnetz dünn und dicht, Zufallsbaum, Preferential Attachment), n = 10, gleiche Fuhrparks, 4 Zufalls-Seeds × 15 Netze je Zelle."""
    cells, _rows = e1
    random_fams = ("Zufallsnetz dünn", "Zufallsnetz dicht", "Zufallsbaum", "Preferential Attachment")
    low = [cells[(f, g)]["rho"] for f in random_fams for g in ("Überlastung (a = 0,5)", "Leichte Überlastung (a = 0,75)")]
    high = [cells[(f, g)]["rho"] for f in random_fams for g in ("Skaleneffekt (a = 1,5)", "Quadratisch (a = 2)", "Starker Skaleneffekt (a = 3)")]
    assert len(low) == 8 and all(r < 0 for r in low) and len(high) == 12 and all(r > 0 for r in high)
    assert (round(min(low), 2), round(max(low), 2)) == (-0.94, -0.88)
    assert (round(min(high), 2), round(max(high), 2)) == (0.83, 0.93)
    for f in random_fams:
        for g in C.GAMES:
            assert cells[(f, g)]["nets"] == 60


def test_e1_additive_game_is_a_dead_branch_and_reports_no_correlation(e1):
    cells, _ = e1
    for f in ev.E1_FAMILIES:
        c = cells[(f, "Additiv (a = 1)")]
        assert c["defined"] == 0 and c["rho"] is None and c["hub"] == pytest.approx(1.0)


def test_e1_negative_hub_value_at_overload(e1):
    """a = 0,5: Mittel (über Netze, dann über Seeds) des Verhältnisses der Betriebe mit den meisten Verträgen: negativ in 3 von 4 Zufallsfamilien und auf der Hantel, nicht im dichten Zufallsnetz."""
    cells, _ = e1
    hubs = {f: cells[(f, "Überlastung (a = 0,5)")]["hub"] for f in ev.E1_FAMILIES}
    assert [f for f, h in hubs.items() if h < 0] == ["Zufallsnetz dünn", "Zufallsbaum", "Preferential Attachment", "Hantel"]
    assert round(hubs["Zufallsnetz dünn"], 2) == -0.36 and round(hubs["Zufallsnetz dicht"], 2) == 0.62
    assert round(hubs["Zufallsbaum"], 2) == -1.56 and round(hubs["Preferential Attachment"], 2) == -0.27


def test_e1_other_basisspiele_do_not_follow_the_power_rule(e1):
    cells, _ = e1
    four = ("Zufallsnetz dünn", "Zufallsnetz dicht", "Zufallsbaum", "Preferential Attachment")
    assert all(cells[(f, "Sättigung (K = 3)")]["rho"] > 0.9 for f in four) and cells[("Hantel", "Sättigung (K = 3)")]["rho"] == pytest.approx(1.0)
    assert all(cells[(f, "Schwelle (t = 3)")]["rho"] > 0.5 for f in four) and cells[("Hantel", "Schwelle (t = 3)")]["rho"] == pytest.approx(-1.0)
    thr = [cells[(f, "Schwelle (t = 3)")]["rho"] for f in four]
    assert (round(min(thr), 2), round(max(thr), 2)) == (0.56, 0.94)
    fix = [cells[(f, "Fixkosten (c = 0,5)")]["rho"] for f in four]
    assert [r < 0 for r in fix] == [True, True, False, True]                   # nur der Zufallsbaum ist positiv (+0,02)
    assert (round(min(r for r in fix if r < 0), 2), round(max(r for r in fix if r < 0), 2)) == (-0.74, -0.08) and round(fix[2], 2) == 0.02
    assert cells[("Hantel", "Fixkosten (c = 0,5)")]["rho"] == pytest.approx(1.0)
    for f in ev.E1_FAMILIES:           # exakte Spiegelung: v = x − c für Gruppen ab 2, bei gleichen Fuhrparks ist der Myerson-Wert linear in c
        assert cells[(f, "Abstimmungsgewinn (c = −1)")]["rho"] == pytest.approx(-cells[(f, "Fixkosten (c = 0,5)")]["rho"], abs=1e-9)


def test_e1_top_player_is_a_node_of_highest_degree_share(e1):
    cells, _ = e1
    dünn = [round(cells[("Zufallsnetz dünn", g)]["top_ok"], 2) for g in ("Skaleneffekt (a = 1,5)", "Quadratisch (a = 2)", "Starker Skaleneffekt (a = 3)")]
    assert dünn == [0.90, 0.87, 0.78]
    shares = [cells[(f, g)]["top_ok"] for f in ("Zufallsnetz dünn", "Zufallsnetz dicht", "Zufallsbaum", "Preferential Attachment")
              for g in ("Skaleneffekt (a = 1,5)", "Quadratisch (a = 2)", "Starker Skaleneffekt (a = 3)")]
    assert (round(min(shares), 2), round(max(shares), 2)) == (0.67, 1.0)


def test_e1_unequal_fleets_weaken_the_link_to_the_degree():
    """Zufallsnetz dünn, n = 10, Fuhrparks aus {1, 2, 3, 5}, 4 Zufalls-Seeds × 15 Netze; absoluter Myerson-Wert gegen Grad."""
    vals = {g: ev.sign_cell("Zufallsnetz dünn", g, weight_mode=C.WEIGHT_MODES[1]) for g in ("Überlastung (a = 0,5)", "Skaleneffekt (a = 1,5)", "Quadratisch (a = 2)")}
    assert [round(vals[g]["rho"], 2) for g in vals] == [-0.70, 0.39, 0.50]
    assert all(abs(v["rho"]) < 0.8 for v in vals.values())


def test_readme_tables_for_e1_match_the_computation(e1):
    _cells, rows = e1
    for line in RR.rho_header() + RR.rho_rows(rows) + RR.hub_rows(rows):
        assert line in README, line


# ---------------------------------------------------------------- E2: Verbindung kappen

def test_e2_equal_loss_and_sign_of_the_ends(e2):
    """Zufallsnetz dünn und Zufallsbaum, n = 8, gleiche Fuhrparks, 4 Zufalls-Seeds × 15 Netze, alle Kappungen (3692 insgesamt)."""
    assert sum(r["cuts"] for r in e2) == 3692
    assert max(r["max_dev"] for r in e2) < 1e-9
    for r in e2:
        a = C.GAMES[r["game"]][1]
        assert (r["both_lose"] == r["cuts"]) if a > 1 else (r["both_gain"] == r["cuts"]), r


def test_e2_bridges_and_third_parties(e2):
    assert [(r["family"], r["bridges"], r["cuts"]) for r in e2[:1]] == [("Zufallsnetz dünn", 266, 503)]
    assert e2[0]["nonbridges"] == 237
    assert [r["bridges"] for r in e2 if r["family"] == "Zufallsbaum"] == [420] * 4
    up = [r for r in e2 if C.GAMES[r["game"]][1] > 1]
    assert sum(r["bridges"] for r in up) == 3 * (266 + 420) and sum(r["bridge_third_gain"] for r in up) == 0
    down = [r for r in e2 if C.GAMES[r["game"]][1] < 1]
    assert sum(r["bridge_third_gain"] for r in down) == sum(r["bridges"] for r in down) == 266 + 420


def test_e2_neighbours_gain_more_than_other_third_parties_on_non_bridges(e2):
    d = {r["game"]: r for r in e2 if r["family"] == "Zufallsnetz dünn"}
    assert (d["Quadratisch (a = 2)"]["near_pairs"], d["Quadratisch (a = 2)"]["far_pairs"]) == (818, 604)
    assert round(d["Quadratisch (a = 2)"]["near_mean"], 2) == 0.72 and round(d["Quadratisch (a = 2)"]["far_mean"], 2) == 0.06
    assert round(d["Starker Skaleneffekt (a = 3)"]["near_mean"], 2) == 5.73 and d["Starker Skaleneffekt (a = 3)"]["far_mean"] < 0     # bei a = 3 verlieren die übrigen Dritten im Mittel (−0,09)
    assert round(d["Starker Skaleneffekt (a = 3)"]["far_mean"], 2) == -0.09
    assert d["Überlastung (a = 0,5)"]["near_mean"] < 0 and d["Überlastung (a = 0,5)"]["far_mean"] < 0


def test_e2_sum_of_changes_is_zero_on_non_bridges():
    """Effizienz: Auf einer Nicht-Brücke bleibt der Wert der großen Koalition, die Änderungen summieren sich zu 0, also gewinnt (oder verliert) mindestens ein Dritter, wenn die Enden es tun."""
    count = 0
    for seed in C.SWEEP_SEEDS:
        rng = SplitMix64(seed)
        for _ in range(5):
            edges = S.make_edges("Zufallsnetz dicht", 8, rng)
            for e in edges:
                eff = K.cut_edge(8, edges, (1,) * 8, SQ, e)
                if not eff.is_bridge:
                    assert eff.change.sum() == pytest.approx(0.0, abs=1e-9)
                    near, far = eff.third_changes(edges)
                    assert sum(near) + sum(far) == pytest.approx(-sum(eff.end_change), abs=1e-9)
                    count += 1
    assert count > 50


def test_star_cut_by_formula():
    """Stern n = 10, a = 2, eine Speiche gekappt: Nabe 34 → 27,667, gekapptes Blatt 7,333 → 1, übrige Blätter 7,333 → 6,667."""
    eff = K.cut_edge(10, S.star_edges(10), (1,) * 10, SQ, (0, 1))
    assert eff.before[0] == pytest.approx(34.0) and eff.after[0] == pytest.approx(83 / 3)
    assert eff.before[1] == pytest.approx(22 / 3) and eff.after[1] == pytest.approx(1.0)
    assert eff.end_change == pytest.approx((-19 / 3, -19 / 3))
    assert eff.change[2] == pytest.approx(-2 / 3)
    assert eff.after[2] == pytest.approx(20 / 3)


def test_readme_table_for_e2_matches_the_computation(e2):
    for line in RR.cut_header() + RR.cut_rows(e2):
        assert line in README, line


# ---------------------------------------------------------------- Positionswert

def _position_sweep(family):
    dists, ranks = [], []
    for seed in C.SWEEP_SEEDS:
        rng = SplitMix64(seed)
        for _ in range(10):
            an = ev.analyse_instance(S.make_edges(family, 7, rng), (1,) * 7, SQ)
            cmp = ev.compare_position(an)
            dists.append(cmp.distance)
            ranks.append(cmp.rank)
    return dists, ranks


def test_position_value_is_not_the_myerson_value_even_on_trees():
    """Quadratisch, n = 7, gleiche Fuhrparks, 4 Zufalls-Seeds × 10 Netze: Zufallsbäume und Zufallsnetz dünn."""
    d, r = _position_sweep("Zufallsbaum")
    assert len(d) == 40 and all(x > 0.01 for x in d)
    assert round(max(d), 3) == 0.085 and round(float(np.mean(d)), 3) == 0.057
    assert min(r) > 0.999                                           # gleiche Rangfolge in 40 von 40 Bäumen
    d2, r2 = _position_sweep("Zufallsnetz dünn")
    assert round(max(d2), 3) == 0.075 and round(float(np.mean(d2)), 3) == 0.046
    assert round(min(r2), 2) == 0.88 and round(float(np.mean(r2)), 3) == 0.995


# ---------------------------------------------------------------- Rechengrenze

def test_sample_error_falls_with_the_number_of_orders(e3):
    """Zufallsnetz dünn, n = 16 (exakt gerechnet), Quadratisch, gleiche Fuhrparks, 4 Zufalls-Seeds."""
    errs = [r["err_mean"] for r in e3]
    assert [r["m"] for r in e3] == [100, 1000, 10000] and errs[0] > errs[1] > errs[2]
    assert [round(e, 3) for e in errs] == [0.285, 0.094, 0.029]
    assert [round(r["rho"], 3) for r in e3] == [0.962, 0.979, 0.995]
    assert [r["top_ok"] for r in e3] == [0.75, 1.0, 1.0]


def test_readme_table_for_the_sample_matches_the_computation(e3):
    for line in RR.sample_header() + RR.sample_rows(e3):
        assert line in README, line


def test_large_net_sample_standard_error_band():
    """Preferential Attachment, n = 200, 1000 Reihenfolgen, Zufalls-Seed 11: größter Standardfehler rund 0,12 Gleichteile (Band 0,05 bis 0,25), Nabe etwa 4,4 Gleichteile (Band 3 bis 6)."""
    big = ev.large_net_sample()
    assert 0.05 < big["max_se"] < 0.25 and 3.0 < big["hub_value"] < 6.0
    assert round(big["max_se"], 2) == 0.12 and round(big["hub_value"], 1) == 4.4


def test_exact_way_agrees_with_the_sample_at_n_twelve_and_runs_at_the_slider_maximum():
    """Worst-Case am Regler-Maximum (n = 12, alle Netzformen): rechnet ohne Fehler; Effizienz bleibt."""
    for family in C.FAMILIES:
        an = ev.analyse(ev.Settings(family, C.N_MAX, "Quadratisch (a = 2)", C.WEIGHT_MODES[0], 35))
        assert an.myerson.sum() == pytest.approx(144.0)


def test_rank_correlation_helper_matches_a_hand_value():
    assert rank_correlation([1, 2, 3], [1, 3, 2]) == pytest.approx(0.5)
