"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Schwelle und jede Zahl im Text. Jedes Verdikt ist eine reine Funktion (Art, Text)."""

import pytest

import gsd_constants as C
import gsd_evaluation as ev


def test_de_formats_with_comma_and_minus_sign():
    assert ev.de(3.14159, 2) == "3,14" and ev.de(-7.5, 2) == "−7,50"
    assert ev.de(0.5, 3) == "0,500" and ev.de(12.0, 0) == "12"


def test_kernfrage_no_effect_below_tolerance():
    kind, text = ev.verdict_kernfrage(0.0, 1.0, False)
    assert kind == "info" and "Keine Wirkung des Netzes" in text and "Abstand 0,000" in text
    assert ev.verdict_kernfrage(1e-10, 1.5, False)[0] == "info"          # unterhalb von 1e-9 gilt als gleich
    assert "Keine Wirkung" not in ev.verdict_kernfrage(2e-9, 1.5, False)[1]


def test_kernfrage_equal_degrees_has_no_hub():
    kind, text = ev.verdict_kernfrage(0.123, 1.2, True)
    assert kind == "info" and "keine Nabe" in text and "12,3 %" in text


def test_kernfrage_without_reference_has_no_hub_statement():
    kind, text = ev.verdict_kernfrage(0.2, None, False)
    assert kind == "info" and "keine Nabe" in text


def test_kernfrage_hub_wins_loses_negative_and_about_equal():
    kind, text = ev.verdict_kernfrage(0.25, 3.4, False)
    assert kind == "success" and "mehr als ohne Netz" in text and "3,40-fache" in text and "25,0 %" in text
    kind, text = ev.verdict_kernfrage(0.25, 0.5, False)
    assert kind == "warning" and "weniger als ohne Netz" in text and "0,50-fache" in text
    kind, text = ev.verdict_kernfrage(0.4, -7.5, False)
    assert kind == "warning" and "negatives Ergebnis" in text and "−7,50" in text
    kind, text = ev.verdict_kernfrage(0.01, 1.02, False)
    assert kind == "info" and "etwa so viel" in text


def test_kernfrage_band_edges_are_inclusive_for_about_equal():
    assert ev.verdict_kernfrage(0.1, 1.05, False)[0] == "info"           # genau 1 + 0,05
    assert ev.verdict_kernfrage(0.1, 0.95, False)[0] == "info"           # genau 1 − 0,05
    assert ev.verdict_kernfrage(0.1, 1.0501, False)[0] == "success"
    assert ev.verdict_kernfrage(0.1, 0.9499, False)[0] == "warning"


def test_cut_verdict_no_effect_bridge_and_non_bridge():
    kind, text = ev.verdict_cut((0.0, 0.0), True, None, None)
    assert kind == "info" and "Keine Wirkung" in text
    kind, text = ev.verdict_cut((-1.6667, -1.6667), True, None, None)
    assert kind == "success" and "verlieren gleich viel" in text and "1,67" in text and "Brücke" in text
    kind, text = ev.verdict_cut((0.5, 0.5), False, 0.25, -0.5)
    assert kind == "info" and "gewinnen gleich viel" in text and "keine Brücke" in text and "Nachbarn eines Endes um 0,25" in text and "−0,50" in text


def test_cut_verdict_mentions_unequal_ends_as_deviation():
    assert "Abweichung der beiden Enden 0,50" in ev.verdict_cut((-1.0, -0.5), True, None, None)[1]


def _cell(family, game, rho):
    return {"family": family, "game": game, "rho": rho}


def test_sign_verdict_counts_cells_and_names_exceptions():
    rows = [_cell("Zufallsbaum", "Überlastung (a = 0,5)", -0.9), _cell("Zufallsbaum", "Leichte Überlastung (a = 0,75)", -0.8),
            _cell("Zufallsbaum", "Skaleneffekt (a = 1,5)", 0.9), _cell("Zufallsbaum", "Quadratisch (a = 2)", 0.8),
            _cell("Zufallsbaum", "Schwelle (t = 3)", 0.5), _cell("Hantel", "Schwelle (t = 3)", -1.0)]
    kind, text = ev.verdict_sign(rows)
    assert kind == "success" and "**2 von 2** Zellen negativ" in text and "**2 von 2** positiv" in text and "negativ in 1 von 2 Zellen" in text


def test_sign_verdict_is_only_success_when_the_rule_holds_everywhere():
    rows = [_cell("Zufallsbaum", "Überlastung (a = 0,5)", 0.1), _cell("Zufallsbaum", "Quadratisch (a = 2)", 0.8)]
    kind, text = ev.verdict_sign(rows)
    assert kind == "info" and "**0 von 1** Zellen negativ" in text and "kein negatives Vorzeichen" in text


def test_sign_verdict_ignores_undefined_cells_and_the_hantel_for_the_power_rule():
    rows = [_cell("Zufallsbaum", "Additiv (a = 1)", None), _cell("Hantel", "Überlastung (a = 0,5)", -1.0), _cell("Zufallsbaum", "Quadratisch (a = 2)", 0.7)]
    kind, text = ev.verdict_sign(rows)
    assert "**0 von 0** Zellen negativ" in text and "**1 von 1** positiv" in text and kind == "info"


def _cutrow(game, cuts, lose, gain, bridges, third, dev=1e-15):
    return {"game": game, "cuts": cuts, "both_lose": lose, "both_gain": gain, "bridges": bridges, "bridge_third_gain": third, "max_dev": dev}


def test_cutting_verdict_counts_per_regime():
    rows = [_cutrow("Überlastung (a = 0,5)", 10, 0, 10, 4, 4), _cutrow("Quadratisch (a = 2)", 10, 10, 0, 4, 0), _cutrow("Starker Skaleneffekt (a = 3)", 6, 5, 0, 2, 1)]
    kind, text = ev.verdict_cutting(rows)
    assert kind == "success" and "In 26 Kappungen" in text
    assert "Bei Skaleneffekt (a > 1) verlieren beide Enden in 15 von 16" in text and "bei Überlastung (a < 1) gewinnen beide in 10 von 10" in text
    assert "gewann ein Dritter in 1 von 6 Fällen" in text


def test_cutting_verdict_warns_when_the_ends_differ():
    kind, text = ev.verdict_cutting([_cutrow("Quadratisch (a = 2)", 5, 5, 0, 1, 0, dev=0.3)])
    assert kind == "warning" and "3,0e-01" in text


def test_curve_verdict_no_effect_and_change_between_exponents():
    rows = [{"a": a, "hub": 1.0, "distance": 0.0} for a in (0.5, 1.0, 2.0)]
    kind, text = ev.verdict_curve(rows)
    assert kind == "info" and "Keine Wirkung auf diesem Netz" in text and "allen 3 Exponenten" in text
    rows = [{"a": 0.5, "hub": -3.0, "distance": 0.4}, {"a": 1.0, "hub": 1.0, "distance": 0.0}, {"a": 1.5, "hub": 2.0, "distance": 0.2}]
    kind, text = ev.verdict_curve(rows)
    assert kind == "success" and "bei 1 von 3 Exponenten weniger" in text and "bei 1 etwa gleich viel und bei 1 mehr" in text and "zwischen a = 0,50 und a = 1,50" in text


def test_curve_verdict_does_not_claim_a_switch_when_the_curve_is_not_monotone_and_handles_no_reference():
    rows = [{"a": 0.5, "hub": 2.0, "distance": 0.1}, {"a": 1.5, "hub": 0.5, "distance": 0.1}]
    kind, text = ev.verdict_curve(rows)
    assert kind == "info" and "Wechsel" not in text
    assert ev.verdict_curve([{"a": 1.0, "hub": None, "distance": 0.0}])[0] == "info"


def test_sample_verdict_names_first_and_last_size():
    rows = [{"m": 100, "err_mean": 0.3, "top_ok": 0.75}, {"m": 10000, "err_mean": 0.03, "top_ok": 1.0}]
    kind, text = ev.verdict_sample(rows)
    assert kind == "success" and "Mit 100 Reihenfolgen" in text and "0,300 Gleichteilen" in text and "mit 10000 bei 0,030" in text and "75 % bzw. 100 %" in text
    assert ev.verdict_sample([{"m": 1, "err_mean": 0.1, "top_ok": 1.0}, {"m": 2, "err_mean": 0.2, "top_ok": 1.0}])[0] == "warning"
    assert ev.verdict_sample([])[0] == "info"


def test_position_verdict_equal_and_different():
    eq = ev.PositionComparison((1.0,), (1.0,), 0.0, None, True)
    assert "gleich (Abstand 0,000)" in ev.verdict_position(eq)[1]
    ne = ev.PositionComparison((1.0, 2.0), (1.5, 1.5), 0.0850, 0.5, False)
    assert "Abstand 0,085" in ev.verdict_position(ne)[1] and "Rangkorrelation 0,500" in ev.verdict_position(ne)[1]
    assert "nicht definiert" in ev.verdict_position(ev.PositionComparison((1.0,), (2.0,), 0.1, None, False))[1]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_runs_through_the_kernfrage_verdict(name):
    """Jedes Preset durchläuft das Verdikt; das Preset „Ring: keine Wirkung“ meldet keine Wirkung, alle übrigen melden eine."""
    p = C.PRESETS[name]
    an = ev.analyse(ev.Settings(p["family"], p["n"], p["game"], p["weights"], p["seed"]))
    kind, text = ev.verdict_kernfrage(an.distance, an.hub_ratio, an.equal_degrees)
    assert (name == "Ring: keine Wirkung") == ("Keine Wirkung des Netzes" in text), (name, text)
