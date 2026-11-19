"""End-to-end Smoke-Test via Streamlits AppTest: Standard, jeder Button (Presets, Zufalls-Seed, Messreihen), jeder Regler an Minimum und Maximum,
jede Auswahl in jeder Stellung, jedes Preset, Kombination aller Extreme, die Ansicht „Verbindung kappen“ für jeden Vertrag."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import gsd_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))
AUTOPLAY_MARKER = "▶"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    assert sum("Messreihe starten" in lab for lab in labels) == 3          # jede der drei Messreihen hat ihren Knopf
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_measurement_shows_a_verdict_after_the_click():
    at = _fresh_app()
    for key in ("e1_start", "e2_start", "e3_start"):
        at.button(key=key).click().run(timeout=TIMEOUT)
        assert not at.exception, (key, [str(e) for e in at.exception])
    texts = " ".join(s.value for s in at.success) + " " + " ".join(s.value for s in at.info) + " " + " ".join(s.value for s in at.warning)
    assert "Rangkorrelation" in texts and "Kappungen" in texts and "Reihenfolgen" in texts


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("key,options", [("family_select", C.FAMILIES), ("game_select", tuple(C.GAMES)), ("weights_select", C.WEIGHT_MODES)])
def test_every_option_of_every_selection_does_not_raise(key, options):
    for option in options:
        at = _fresh_app()
        at.sidebar.selectbox(key=key).set_value(option).run(timeout=TIMEOUT)
        assert not at.exception, (key, option, [str(e) for e in at.exception])


def test_all_minima_and_all_maxima_together_do_not_raise():
    for n in (C.N_MIN, C.N_MAX):
        for family in ("Vollständig", "Preferential Attachment"):
            at = _fresh_app()
            at.sidebar.slider(key="n_slider").set_value(n)
            at.sidebar.selectbox(key="family_select").set_value(family)
            at.sidebar.selectbox(key="game_select").set_value("Abstimmungsgewinn (c = −1)")
            at.sidebar.selectbox(key="weights_select").set_value(C.WEIGHT_MODES[1])
            at.sidebar.number_input(key="seed_input").set_value(C.SEED_MAX).run(timeout=TIMEOUT)
            assert not at.exception, (n, family, [str(e) for e in at.exception])


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_loads_and_shows_a_kernfrage_verdict(name):
    at = _fresh_app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception, (name, [str(e) for e in at.exception])
    shown = " ".join(e.value for kind in (at.success, at.info, at.warning) for e in kind)
    assert ("Keine Wirkung des Netzes" in shown) == (name == "Ring: keine Wirkung")


def test_cutting_every_contract_of_the_default_net_does_not_raise():
    at = _fresh_app()
    for k in range(9):
        at.selectbox(key="cut_edge").set_value(k).run(timeout=TIMEOUT)
        assert not at.exception, (k, [str(e) for e in at.exception])


def test_cut_selection_survives_a_smaller_net():
    at = _fresh_app()
    at.selectbox(key="cut_edge").set_value(8).run(timeout=TIMEOUT)
    at.sidebar.selectbox(key="family_select").set_value("Pfad").run(timeout=TIMEOUT)
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN).run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
