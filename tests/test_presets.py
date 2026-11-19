"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink rastet ein; Zweig-Tests der Basisspiele."""

import gsd_constants as C
import gsd_evaluation as ev
import gsd_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_valid_choices_and_inside_the_slider_bounds():
    for preset in C.PRESETS.values():
        assert preset["family"] in C.FAMILIES and preset["game"] in C.GAMES and preset["weights"] in C.WEIGHT_MODES
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX


def test_first_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(first["family"], first["n"], first["game"], first["weights"], first["seed"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_clamp_value_limits_numbers_and_snaps_choices():
    n_spec, f_spec = P.SETTING_SPECS["n_slider"], P.SETTING_SPECS["family_select"]
    assert P.clamp_value(n_spec, 500) == C.N_MAX and P.clamp_value(n_spec, -4) == C.N_MIN and P.clamp_value(n_spec, 7) == 7
    assert P.clamp_value(f_spec, "Ring") == "Ring" and P.clamp_value(f_spec, "Gitter") == f_spec.default


def test_games_dictionary_covers_all_four_kinds_with_valid_parameters():
    kinds = {kind for kind, _ in C.GAMES.values()}
    assert kinds == {"potenz", "saettigung", "schwelle", "fixkosten"}
    assert C.DEFAULT_GAME in C.GAMES
    for name in C.GAMES:
        ev.game_of(name)          # keine Ausnahme


def test_branch_test_games_and_nets_differ_on_at_least_one_instance():
    """Zweig-Test (Nullspalten-Regel): jede Variante weicht auf einer Instanz von den Nachbarn ab. Additiv und Ring/Vollständig haben dagegen KEINEN Effekt."""
    def dist(family, game, weights=C.WEIGHT_MODES[0]):
        return ev.analyse(ev.Settings(family, 8, game, weights, 5)).distance

    for game in C.GAMES:
        if game != "Additiv (a = 1)":
            assert dist("Stern", game) > 1e-6, game
    assert dist("Stern", "Additiv (a = 1)") < 1e-9
    for family in ("Ring", "Vollständig"):
        for game in C.GAMES:
            assert dist(family, game) < 1e-9, (family, game)
    assert dist("Ring", "Quadratisch (a = 2)", C.WEIGHT_MODES[1]) > 1e-6          # ungleiche Fuhrparks bringen den Effekt zurück
    pairs = [("Überlastung (a = 0,5)", "Quadratisch (a = 2)"), ("Sättigung (K = 3)", "Schwelle (t = 3)"), ("Fixkosten (c = 0,5)", "Abstimmungsgewinn (c = −1)")]
    for g1, g2 in pairs:
        r1, r2 = (ev.analyse(ev.Settings("Zufallsnetz dünn", 8, g, C.WEIGHT_MODES[0], 5)) for g in (g1, g2))
        assert abs(r1.hub_ratio - r2.hub_ratio) > 1e-3, (g1, g2)
