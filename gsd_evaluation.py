"""Kennzahlen, Messreihen (feste Zufalls-Seeds) und Verdikte als reine Funktionen `verdict_*(…) -> (Art, Text)`."""

import time
from dataclasses import dataclass

import numpy as np

import gsd_constants as C
from gsd_centrality import centralities, rank_correlation
from gsd_cut import CutEffect, cut_edge, position_value
from gsd_games import BaseGame, myerson_exact, myerson_sample, shapley_plain
from gsd_rng import SplitMix64
from gsd_scenario import degrees, make_edges, make_instance, make_weights

TOL = 1e-9
HUB_BAND = 0.05      # Verhältnis Nabe/ohne Netz innerhalb 1 ± 0,05 gilt als „etwa gleich“


def de(x: float, nd: int = 2) -> str:
    """Zahl mit Dezimalkomma; ein negatives Vorzeichen wird als Minuszeichen geschrieben."""
    s = f"{x:.{nd}f}".replace(".", ",")
    return s.replace("-", "−")


def de_exp(x: float) -> str:
    """Zahl in wissenschaftlicher Schreibweise mit Dezimalkomma (für Rundungsreste)."""
    return f"{x:.1e}".replace(".", ",")


def game_of(name: str) -> BaseGame:
    kind, param = C.GAMES[name]
    return BaseGame(kind, param)


def potenz(a: float) -> BaseGame:
    return BaseGame("potenz", a)


@dataclass(frozen=True)
class Settings:
    family: str = "Stern"
    n: int = C.DEFAULT_N
    game: str = C.DEFAULT_GAME
    weights: str = C.WEIGHT_MODES[0]
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    edges: tuple
    weights: tuple
    game: BaseGame
    myerson: np.ndarray
    shapley: np.ndarray            # Shapley-Wert des Basisspiels ohne Netz (Bezug aller Verhältnisse)
    value_total: float             # v(N), Wert der großen Koalition (gleich v^G(N), das Netz ist zusammenhängend)
    degree: tuple
    cent: dict

    @property
    def n(self) -> int:
        return len(self.weights)

    @property
    def distance(self) -> float:
        """Abstand Myerson zu Shapley ohne Netz: halbe L1-Norm geteilt durch v(N) (Anteil von v(N), der durch das Netz umverteilt wird)."""
        return distance_to_shapley(self.myerson, self.shapley, self.value_total)

    @property
    def top_degree_nodes(self) -> list[int]:
        top = max(self.degree) if self.degree else 0
        return [i for i, d in enumerate(self.degree) if d == top]

    @property
    def equal_degrees(self) -> bool:
        return len(set(self.degree)) <= 1

    @property
    def hub_ratio(self):
        return hub_ratio(self.myerson, self.shapley, self.degree)

    @property
    def ratios(self) -> list:
        return [None if abs(s) < TOL else float(m / s) for m, s in zip(self.myerson, self.shapley)]


def distance_to_shapley(phi, sh, v_total: float) -> float:
    return 0.0 if abs(v_total) < TOL else float(np.abs(np.asarray(phi) - np.asarray(sh)).sum() / 2 / abs(v_total))


def hub_ratio(phi, sh, degree):
    """Mittel von Myerson/Shapley über die Betriebe mit höchstem Grad (bei Gleichstand alle); None, wenn der Bezug 0 ist."""
    if len(degree) == 0:
        return None
    top = [i for i, d in enumerate(degree) if d == max(degree)]
    if any(abs(sh[i]) < TOL for i in top):
        return None
    return float(np.mean([phi[i] / sh[i] for i in top]))


def analyse_instance(edges, weights, game: BaseGame) -> Analysis:
    n = len(weights)
    phi = myerson_exact(n, edges, weights, game)
    sh = shapley_plain(n, weights, game)
    v_total = float(sh.sum())
    return Analysis(tuple(edges), tuple(weights), game, phi, sh, v_total, tuple(degrees(n, edges)), centralities(n, edges))


def analyse(settings: Settings) -> Analysis:
    edges, weights = make_instance(settings.family, settings.n, settings.weights, settings.seed)
    return analyse_instance(edges, weights, game_of(settings.game))


# ---------------------------------------------------------------- Kurve über den Exponenten für das aktuelle Netz

def hub_curve(edges, weights, exponents=C.A_CURVE) -> list[dict]:
    """Verhältnis Nabe/ohne Netz und Abstand für jeden Exponenten a (Potenzspiel) auf dem gegebenen Netz."""
    rows = []
    for a in exponents:
        an = analyse_instance(edges, weights, potenz(a))
        rows.append({"a": a, "hub": an.hub_ratio, "distance": an.distance})
    return rows


# ---------------------------------------------------------------- E1: Zentralität gegen Wert

def net_metrics(an: Analysis) -> dict:
    """Kennzahlen eines Netzes für E1: Rangkorrelation mit dem Grad, Verhältnis der Nabe, Spitze = Knoten höchsten Grades."""
    phi = an.myerson
    best = float(phi.max())
    tied = {i for i in range(an.n) if phi[i] >= best - TOL}
    return {
        "rho": rank_correlation(phi, an.degree),
        "hub": an.hub_ratio,
        "top_ok": float(bool(tied & set(an.top_degree_nodes))),
    }


def sign_cell(family: str, game_name: str, n: int = C.EXPERIMENT_N, seeds=C.SWEEP_SEEDS, nets: int = C.NETS_PER_SEED,
              weight_mode: str = C.WEIGHT_MODES[0]) -> dict:
    """Eine Zelle von E1: Netzfamilie × Basisspiel. Je Zufalls-Seed der Mittelwert über `nets` Netze, dann Mittel und Streuung über die Seeds.
    Feste Familien haben nur ein Netz. Bei ungleichen Fuhrparks werden die Gewichte nach dem Netz aus demselben Zufallsstrom gezogen."""
    game = game_of(game_name)
    fixed = family in ("Stern", "Pfad", "Ring", "Hantel", "Vollständig")
    per_seed, defined, total = [], 0, 0
    for seed in (seeds[:1] if fixed else seeds):
        rng = SplitMix64(seed)
        rows = []
        for _ in range(1 if fixed else nets):
            edges = make_edges(family, n, rng)
            rows.append(net_metrics(analyse_instance(edges, make_weights(weight_mode, n, rng), game)))
        total += len(rows)
        rhos = [r["rho"] for r in rows if r["rho"] is not None]
        defined += len(rhos)
        hubs = [r["hub"] for r in rows if r["hub"] is not None]
        per_seed.append((float(np.mean(rhos)) if rhos else None, float(np.mean(hubs)) if hubs else None,
                         float(np.mean([r["top_ok"] for r in rows]))))
    rho_vals = [p[0] for p in per_seed if p[0] is not None]
    hub_vals = [p[1] for p in per_seed if p[1] is not None]
    return {
        "family": family, "game": game_name, "nets": total, "defined": defined,
        "rho": float(np.mean(rho_vals)) if rho_vals else None,
        "rho_std": float(np.std(rho_vals)) if rho_vals else None,
        "hub": float(np.mean(hub_vals)) if hub_vals else None,
        "top_ok": float(np.mean([p[2] for p in per_seed])),
    }


E1_FAMILIES = ("Zufallsnetz dünn", "Zufallsnetz dicht", "Zufallsbaum", "Preferential Attachment", "Hantel")


def sign_table(families=E1_FAMILIES, games=tuple(C.GAMES), n: int = C.EXPERIMENT_N, seeds=C.SWEEP_SEEDS, nets: int = C.NETS_PER_SEED) -> list[dict]:
    return [sign_cell(f, g, n, seeds, nets) for f in families for g in games]


# ---------------------------------------------------------------- E2: Verbindung kappen auf Zufallsnetzen

def cut_cell(family: str, game_name: str, n: int = C.CUT_N, seeds=C.SWEEP_SEEDS, nets: int = C.NETS_PER_SEED) -> dict:
    """Alle Kappungen aller Netze einer Familie bei einem Basisspiel; gezählt wird über die Kappungen (nicht über die Netze)."""
    game = game_of(game_name)
    cuts = both_lose = both_gain = bridge = bridge_third_gain = nonbridge = 0
    max_dev = 0.0
    near, far = [], []
    for seed in seeds:
        rng = SplitMix64(seed)
        for _ in range(nets):
            edges = make_edges(family, n, rng)
            weights = (1,) * n
            for e in edges:
                eff = cut_edge(n, edges, weights, game, e)
                ci, cj = eff.end_change
                cuts += 1
                max_dev = max(max_dev, abs(ci - cj))
                both_lose += ci < -TOL and cj < -TOL
                both_gain += ci > TOL and cj > TOL
                nr, fr = eff.third_changes(edges)
                if eff.is_bridge:
                    bridge += 1
                    bridge_third_gain += any(x > TOL for x in nr + fr)
                else:
                    nonbridge += 1
                    near += nr
                    far += fr
    return {
        "family": family, "game": game_name, "cuts": cuts, "both_lose": int(both_lose), "both_gain": int(both_gain), "max_dev": max_dev,
        "bridges": bridge, "bridge_third_gain": int(bridge_third_gain), "nonbridges": nonbridge,
        "near_mean": float(np.mean(near)) if near else None, "near_pairs": len(near),
        "far_mean": float(np.mean(far)) if far else None, "far_pairs": len(far),
    }


E2_GAMES = ("Überlastung (a = 0,5)", "Skaleneffekt (a = 1,5)", "Quadratisch (a = 2)", "Starker Skaleneffekt (a = 3)")
E2_FAMILIES = ("Zufallsnetz dünn", "Zufallsbaum")


def cut_table(families=E2_FAMILIES, games=E2_GAMES, n: int = C.CUT_N, seeds=C.SWEEP_SEEDS, nets: int = C.NETS_PER_SEED) -> list[dict]:
    return [cut_cell(f, g, n, seeds, nets) for f in families for g in games]


# ---------------------------------------------------------------- E3: Rechengrenze

def sample_cell(n: int, edges, weights, game: BaseGame, m: int, seeds=C.SWEEP_SEEDS, exact=None) -> dict:
    """Fehler der Stichprobe mit m Reihenfolgen gegen den exakten Wert, je Zufalls-Seed; Fehler in Vielfachen des Gleichteils v(N)/n."""
    if exact is None:
        exact = myerson_exact(n, edges, weights, game)
    share = float(shapley_plain(n, weights, game).sum()) / n
    errs, rhos, tops, secs = [], [], [], []
    for seed in seeds:
        t0 = time.perf_counter()
        mean, _se = myerson_sample(n, edges, weights, game, m, seed)
        secs.append(time.perf_counter() - t0)
        errs.append(float(np.abs(mean - exact).max()) / share)
        r = rank_correlation(mean, exact)
        rhos.append(r if r is not None else float("nan"))
        tops.append(float(int(np.argmax(mean)) == int(np.argmax(exact))))
    return {"m": m, "err_mean": float(np.mean(errs)), "err_std": float(np.std(errs)), "rho": float(np.nanmean(rhos)), "top_ok": float(np.mean(tops)),
            "seconds": float(np.mean(secs))}


def sample_table(n: int = 16, sizes=C.SAMPLE_SIZES, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Stichprobe gegen exakt auf einem festen Zufallsnetz (dünn, Quadratisch, gleiche Fuhrparks)."""
    edges = make_edges("Zufallsnetz dünn", n, SplitMix64(seeds[0]))
    game = potenz(2.0)
    weights = (1,) * n
    exact = myerson_exact(n, edges, weights, game)
    return [sample_cell(n, edges, weights, game, m, seeds, exact) for m in sizes]


def exact_timing(sizes=(14, 16, 18, 20)) -> list[dict]:
    """Rechenzeit des exakten Wegs auf einem Zufallsnetz mit n Betrieben (einmal gemessen; hängt vom Rechner ab)."""
    rows = []
    for n in sizes:
        edges = make_edges("Zufallsnetz dünn", n, SplitMix64(C.DEFAULT_SEED))
        t0 = time.perf_counter()
        myerson_exact(n, edges, (1,) * n, potenz(2.0))
        rows.append({"n": n, "edges": len(edges), "seconds": time.perf_counter() - t0})
    return rows


def large_net_sample(n: int = 200, m: int = 1000, seed: int = C.SWEEP_SEEDS[0]) -> dict:
    """Stichprobe auf einem großen Preferential-Attachment-Netz: größter Standardfehler (Vielfache des Gleichteils) und größter Wert (Nabe)."""
    edges = make_edges("Preferential Attachment", n, SplitMix64(seed))
    weights = (1,) * n
    t0 = time.perf_counter()
    mean, se = myerson_sample(n, edges, weights, potenz(2.0), m, seed)
    share = float(n ** 2) / n
    return {"n": n, "m": m, "seconds": time.perf_counter() - t0, "max_se": float(se.max()) / share, "hub_value": float(mean.max()) / share}


# ---------------------------------------------------------------- Positionswert

@dataclass(frozen=True)
class PositionComparison:
    myerson: tuple
    position: tuple
    distance: float          # halbe L1-Norm geteilt durch v(N)
    rank: object             # Rangkorrelation oder None
    equal: bool


def compare_position(an: Analysis) -> PositionComparison:
    pos = position_value(an.n, an.edges, an.weights, an.game)
    dist = distance_to_shapley(an.myerson, pos, an.value_total)
    return PositionComparison(tuple(float(x) for x in an.myerson), tuple(float(x) for x in pos), dist,
                              rank_correlation(an.myerson, pos), bool(dist < TOL))


# ---------------------------------------------------------------- Verdikte

def verdict_kernfrage(distance: float, hub, equal_degrees: bool) -> tuple[str, str]:
    """Kernfrage: Was ändert das Netz an der Verteilung? `hub` = Verhältnis Myerson/Shapley der Betriebe mit den meisten Verträgen (oder None)."""
    if distance < TOL:
        return "info", "**Keine Wirkung des Netzes:** Der Myerson-Wert ist gleich dem Shapley-Wert ohne Netz (Abstand 0,000). Das Netz als Ganzes ändert die Verteilung nicht; das Wegfallen einzelner Verträge kann sie trotzdem ändern (Reiter „Verbindung kappen“)."
    if equal_degrees or hub is None:
        return "info", (f"Alle Betriebe haben gleich viele Verträge, es gibt keine Nabe. Das Netz verschiebt trotzdem {de(distance * 100, 1)} % von v(N) gegenüber dem Wert ohne Netz "
                        "(Abstand durch die Fuhrparkgrößen und die Lage im Netz).")
    verschoben = f"Das Netz verschiebt {de(distance * 100, 1)} % von v(N) gegenüber dem Wert ohne Netz."
    if hub < 0:
        return "warning", (f"**Die Betriebe mit den meisten Verträgen bekommen ein negatives Ergebnis** (das {de(hub)}-fache ihres Werts ohne Netz): Das Netz schadet ihnen. {verschoben}")
    if hub < 1 - HUB_BAND:
        return "warning", f"**Die Betriebe mit den meisten Verträgen bekommen weniger als ohne Netz** (das {de(hub)}-fache ihres Werts). {verschoben}"
    if hub > 1 + HUB_BAND:
        return "success", f"**Die Betriebe mit den meisten Verträgen bekommen mehr als ohne Netz** (das {de(hub)}-fache ihres Werts). {verschoben}"
    return "info", f"Die Betriebe mit den meisten Verträgen bekommen etwa so viel wie ohne Netz (das {de(hub)}-fache). {verschoben}"


def verdict_cut(end_change: tuple[float, float], is_bridge: bool, near_mean, far_mean) -> tuple[str, str]:
    """Verdikt des Kappens: beide Enden ändern sich gleich (Gleichverlust-Satz); Dritte: bei einer Brücke verliert niemand von ihnen,
    bei einer Nicht-Brücke summieren sich alle Änderungen zu 0."""
    ci, cj = end_change
    if abs(ci) < TOL and abs(cj) < TOL:
        return "info", "**Keine Wirkung:** Ohne diese Verbindung bekommt kein Betrieb etwas anderes (Änderung 0,00 an beiden Enden)."
    richtung = "verlieren" if ci < 0 else "gewinnen"
    kopf = f"**Beide Enden {richtung} gleich viel:** {de(abs(ci))} (Abweichung der beiden Enden {de(abs(ci - cj), 2)}). "
    if is_bridge:
        return "success", kopf + "Die Verbindung ist eine Brücke: ohne sie zerfällt das Netz in zwei Teile."
    text = kopf + "Die Verbindung ist keine Brücke: Das Netz bleibt zusammenhängend, die Summe aller Änderungen ist 0, also gewinnen oder verlieren Dritte in der Summe das Gegenteil der beiden Enden."
    if near_mean is not None and far_mean is not None:
        text += f" Im Mittel ändern sich Nachbarn eines Endes um {de(near_mean)}, alle übrigen Dritten um {de(far_mean)}."
    return "info", text


def verdict_sign(rows: list[dict]) -> tuple[str, str]:
    """Verdikt von E1 über die Potenzspiele der Zufallsfamilien: Vorzeichen der Rangkorrelation mit dem Grad je Exponent."""
    random_fams = [r for r in rows if r["family"] != "Hantel" and C.GAMES[r["game"]][0] == "potenz" and r["rho"] is not None]
    low = [r for r in random_fams if C.GAMES[r["game"]][1] < 1]
    high = [r for r in random_fams if C.GAMES[r["game"]][1] > 1]
    neg = sum(r["rho"] < 0 for r in low)
    pos = sum(r["rho"] > 0 for r in high)
    other = [r for r in rows if C.GAMES[r["game"]][0] != "potenz" and r["rho"] is not None]
    mixed = sorted({(r["family"], r["game"]) for r in other if r["rho"] < 0}, key=str)
    text = (f"Bei Überlastung (a < 1) ist die Rangkorrelation zwischen Myerson-Wert und Grad in **{neg} von {len(low)}** Zellen negativ, "
            f"bei Skaleneffekt (a > 1) in **{pos} von {len(high)}** positiv. ")
    if mixed:
        text += f"Bei den übrigen Basisspielen gilt diese Regel nicht überall: negativ in {len(mixed)} von {len(other)} Zellen."
    else:
        text += "Die übrigen Basisspiele zeigen hier kein negatives Vorzeichen."
    if low and high and neg == len(low) and pos == len(high):
        return "success", text
    return "info", text


def verdict_cutting(rows: list[dict]) -> tuple[str, str]:
    """Verdikt von E2: Gleichverlust in allen Kappungen? Wie verhalten sich die Enden und die Dritten bei Skaleneffekt und bei Überlastung?"""
    total = sum(r["cuts"] for r in rows)
    dev = max((r["max_dev"] for r in rows), default=0.0)
    up = [r for r in rows if C.GAMES[r["game"]][0] == "potenz" and C.GAMES[r["game"]][1] > 1]
    down = [r for r in rows if C.GAMES[r["game"]][0] == "potenz" and C.GAMES[r["game"]][1] < 1]
    text = (f"In {total} Kappungen weichen die Änderungen der beiden Enden höchstens um {de_exp(dev)} voneinander ab{" (Rundungsrest)" if dev < 1e-9 else " (mehr als ein Rundungsrest)"}. "
            f"Bei Skaleneffekt (a > 1) verlieren beide Enden in {sum(r['both_lose'] for r in up)} von {sum(r['cuts'] for r in up)} Kappungen, "
            f"bei Überlastung (a < 1) gewinnen beide in {sum(r['both_gain'] for r in down)} von {sum(r['cuts'] for r in down)}. "
            f"Bei den Brücken unter Skaleneffekt gewann ein Dritter in {sum(r['bridge_third_gain'] for r in up)} von {sum(r['bridges'] for r in up)} Fällen.")
    return ("success" if dev < 1e-9 else "warning"), text


def verdict_curve(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Kurve über den Exponenten auf dem aktuellen Netz: bei wie vielen Exponenten bekommen die Betriebe mit den meisten Verträgen
    weniger, etwa gleich viel oder mehr als ohne Netz (Band 1 ± HUB_BAND)."""
    rs = [r for r in rows if r["hub"] is not None]
    if not rs:
        return "info", "Für dieses Netz ist der Bezug (Wert ohne Netz) bei den Betrieben mit den meisten Verträgen 0: keine Kurve."
    less = [r["a"] for r in rs if r["hub"] < 1 - HUB_BAND]
    same = [r["a"] for r in rs if abs(r["hub"] - 1) <= HUB_BAND]
    more = [r["a"] for r in rs if r["hub"] > 1 + HUB_BAND]
    if len(same) == len(rs):
        return "info", f"**Keine Wirkung auf diesem Netz:** Bei allen {len(rs)} Exponenten bekommen die Betriebe mit den meisten Verträgen etwa so viel wie ohne Netz."
    text = (f"Auf diesem Netz bekommen die Betriebe mit den meisten Verträgen bei {len(less)} von {len(rs)} Exponenten weniger als ohne Netz, "
            f"bei {len(same)} etwa gleich viel und bei {len(more)} mehr.")
    if less and more and max(less) < min(more):
        text += f" Der Wechsel liegt zwischen a = {de(max(less))} und a = {de(min(more))}."
        return "success", text
    return "info", text


def verdict_sample(rows: list[dict]) -> tuple[str, str]:
    """Verdikt von E3: Der Fehler der Stichprobe sinkt mit der Zahl der Reihenfolgen."""
    if not rows:
        return "info", "Noch keine Messung."
    first, last = rows[0], rows[-1]
    text = (f"Mit {first['m']} Reihenfolgen liegt der größte Fehler im Mittel bei {de(first['err_mean'], 3)} Gleichteilen, "
            f"mit {last['m']} bei {de(last['err_mean'], 3)}; der Spitzenspieler stimmt in {de(first['top_ok'] * 100, 0)} % bzw. {de(last['top_ok'] * 100, 0)} % der Zufalls-Seeds.")
    return ("success" if last["err_mean"] < first["err_mean"] else "warning"), text


def verdict_position(cmp: PositionComparison) -> tuple[str, str]:
    """Verdikt des Positionswerts: gleich dem Myerson-Wert oder nicht (Abstand und Rangkorrelation)."""
    if cmp.equal:
        return "info", "Positionswert und Myerson-Wert sind auf diesem Netz gleich (Abstand 0,000)."
    rk = "nicht definiert" if cmp.rank is None else de(cmp.rank, 3)
    return "info", f"Positionswert und Myerson-Wert unterscheiden sich: Abstand {de(cmp.distance, 3)} von v(N), Rangkorrelation {rk}."
