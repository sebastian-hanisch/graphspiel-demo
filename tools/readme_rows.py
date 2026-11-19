"""Erzeugt die Tabellen der README über dieselben Funktionen wie die App (Werkzeug, kein Test).

Aufruf: python tools/readme_rows.py    (gibt die Markdown-Zeilen aus; tests/test_claims.py prüft, dass jede Zeile in der README steht)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gsd_constants as C  # noqa: E402
import gsd_evaluation as ev  # noqa: E402


def _short(game: str) -> str:
    return game.replace(" (", " ").replace(")", "")


def _fmt(x, nd=2):
    return "–" if x is None else ev.de(x, nd)


def rho_header() -> list[str]:
    games = list(C.GAMES)
    return ["| Netzform | " + " | ".join(_short(g) for g in games) + " |", "|---|" + "---|" * len(games)]


def rho_rows(rows) -> list[str]:
    """Eine Zeile je Netzform: Rangkorrelation Myerson-Wert gegen Grad je Basisspiel."""
    lookup = {(r["family"], r["game"]): r for r in rows}
    out = []
    for family in ev.E1_FAMILIES:
        out.append(f"| {family} | " + " | ".join(_fmt(lookup[(family, g)]["rho"]) for g in C.GAMES) + " |")
    return out


def hub_rows(rows) -> list[str]:
    """Eine Zeile je Netzform: Verhältnis Myerson-Wert ÷ Wert ohne Netz der Betriebe mit den meisten Verträgen je Basisspiel."""
    lookup = {(r["family"], r["game"]): r for r in rows}
    out = []
    for family in ev.E1_FAMILIES:
        out.append(f"| {family} | " + " | ".join(_fmt(lookup[(family, g)]["hub"]) for g in C.GAMES) + " |")
    return out


def cut_header() -> list[str]:
    return ["| Netzform | Basisspiel | Kappungen | beide Enden verlieren | beide Enden gewinnen | Brücken | Brücken mit gewinnendem Dritten | Nachbar im Mittel (Paare) | andere Dritte im Mittel (Paare) |",
            "|---|---|---|---|---|---|---|---|---|"]


def cut_rows(rows) -> list[str]:
    out = []
    for r in rows:
        near = "–" if r["near_mean"] is None else f"{_fmt(r['near_mean'])} ({r['near_pairs']})"
        far = "–" if r["far_mean"] is None else f"{_fmt(r['far_mean'])} ({r['far_pairs']})"
        out.append(f"| {r['family']} | {r['game']} | {r['cuts']} | {r['both_lose']} | {r['both_gain']} | {r['bridges']} | {r['bridge_third_gain']} | {near} | {far} |")
    return out


def sample_header() -> list[str]:
    return ["| Reihenfolgen m | größter Fehler (Gleichteile), Mittel ± Streuung | Rangkorrelation | gleicher Spitzenspieler |", "|---|---|---|---|"]


def sample_rows(rows) -> list[str]:
    return [f"| {r['m']} | {_fmt(r['err_mean'], 3)} ± {_fmt(r['err_std'], 3)} | {_fmt(r['rho'], 3)} | {_fmt(r['top_ok'] * 100, 0)} % |" for r in rows]


if __name__ == "__main__":
    print("\n".join(rho_header() + rho_rows(ev.sign_table())))
    print()
    print("\n".join(rho_header() + hub_rows(ev.sign_table())))
    print()
    print("\n".join(cut_header() + cut_rows(ev.cut_table())))
    print()
    print("\n".join(sample_header() + sample_rows(ev.sample_table())))
