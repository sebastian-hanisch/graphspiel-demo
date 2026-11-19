"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import gsd_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def labels(n: int) -> list[str]:
    return [f"B{i + 1}" for i in range(n)]


def build_network(n, edges, pos, ratios, highlight=None):
    """Netz mit Betrieben als Knoten; Farbe = Myerson-Wert geteilt durch den Shapley-Wert ohne Netz (1 = unverändert, rot = mehr, blau = weniger);
    die gekappte Verbindung ist rot gestrichelt. Beschriftungen als Text (B1 …), die Karte behält gleichen Maßstab (scaleanchor mit autorange)."""
    fig = go.Figure()
    ex, ey = [], []
    for i, j in edges:
        if (i, j) == highlight:
            continue
        ex += [pos[i][0], pos[j][0], None]
        ey += [pos[i][1], pos[j][1], None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color=C.COLOR_EDGE, width=2), hoverinfo="skip", showlegend=False))
    if highlight is not None:
        i, j = highlight
        fig.add_trace(go.Scatter(x=[pos[i][0], pos[j][0]], y=[pos[i][1], pos[j][1]], mode="lines",
                                 line=dict(color=C.COLOR_CUT, width=4, dash="dash"), hoverinfo="skip", showlegend=False))
    colors = [1.0 if r is None else float(r) for r in ratios]
    shown = np.clip(colors, 0.0, 2.0)          # die Farbskala endet bei 0 und 2; die Zahl im Hover bleibt ungekürzt
    fig.add_trace(go.Scatter(
        x=[p[0] for p in pos], y=[p[1] for p in pos], mode="markers+text", text=labels(n), textposition="middle center",
        marker=dict(size=34, color=shown, colorscale="RdBu_r", cmin=0.0, cmax=2.0, cmid=1.0, line=dict(color="#444", width=1),
                    colorbar=dict(title=dict(text="Myerson ÷ ohne Netz", side="top"), tickvals=[0, 1, 2], ticktext=["≤ 0", "1", "≥ 2"], len=0.8)),
        customdata=[["–" if r is None else f"{r:.2f}".replace(".", ",")] for r in ratios],
        hovertemplate="%{text}: Verhältnis %{customdata[0]}<extra></extra>", showlegend=False))
    fig.add_trace(go.Scatter(x=[-1.25, 1.25], y=[-1.25, 1.25], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=420)
    return _base(fig, 420)


def build_payout(n, myerson, shapley):
    """Auszahlung je Betrieb: Shapley-Wert ohne Netz (grau) gegen Myerson-Wert (grün)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels(n), y=[float(x) for x in shapley], name="Shapley ohne Netz", marker_color=C.COLOR_SHAPLEY,
                         hovertemplate="%{x}: %{y:.2f}<extra>ohne Netz</extra>"))
    fig.add_trace(go.Bar(x=labels(n), y=[float(x) for x in myerson], name="Myerson-Wert mit Netz", marker_color=C.COLOR_MYERSON,
                         hovertemplate="%{x}: %{y:.2f}<extra>mit Netz</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Auszahlung (Einheiten von v)")
    return _base(fig)


def build_hub_curve(rows):
    """Verhältnis Nabe ÷ Wert ohne Netz über den Exponenten a des aktuellen Netzes; die Linie 1 trennt „Nabe gewinnt“ von „Nabe verliert“."""
    pts = [(r["a"], r["hub"]) for r in rows if r["hub"] is not None]
    fig = go.Figure()
    fig.add_hline(y=1.0, line=dict(color="#888", dash="dot"))
    fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3),
                             hovertemplate="a = %{x}: %{y:.2f}<extra></extra>", name="Betriebe mit den meisten Verträgen"))
    fig.update_xaxes(title_text="Exponent a (a < 1 Überlastung, a > 1 Skaleneffekt)")
    fig.update_yaxes(title_text="Myerson ÷ Wert ohne Netz")
    return _base(fig, 320)


def build_cut(n, change, edge):
    """Änderung des Myerson-Werts je Betrieb nach dem Kappen; die beiden Enden der Verbindung sind rot."""
    colors = [C.COLOR_CUT if i in edge else C.COLOR_SHAPLEY for i in range(n)]
    fig = go.Figure(go.Bar(x=labels(n), y=[float(x) for x in change], marker_color=colors, hovertemplate="%{x}: %{y:.3f}<extra></extra>"))
    fig.update_yaxes(title_text="Änderung (nachher minus vorher)")
    return _base(fig, 300)


def build_sign_heatmap(rows, family_order, game_order):
    """Rangkorrelation Myerson-Wert gegen Grad je Netzfamilie (Zeilen) und Basisspiel (Spalten); leere Zellen: Korrelation nicht definiert."""
    lookup = {(r["family"], r["game"]): r["rho"] for r in rows}
    z = [[np.nan if lookup.get((f, g)) is None else lookup[(f, g)] for g in game_order] for f in family_order]
    text = [["–" if np.isnan(v) else f"{v:.2f}".replace(".", ",").replace("-", "−") for v in row] for row in z]
    fig = go.Figure(go.Heatmap(z=z, x=[g.split(" (")[0] + (" (" + g.split(" (")[1] if " (" in g else "") for g in game_order], y=list(family_order),
                               zmin=-1, zmax=1, colorscale="RdBu_r", text=text, texttemplate="%{text}", hoverinfo="skip",
                               colorbar=dict(title=dict(text="Rangkorrelation", side="top"), tickvals=[-1, 0, 1], len=0.8)))
    fig.update_xaxes(tickangle=-35)
    return _base(fig, 380)


def build_sample_errors(rows):
    """Größter Fehler der Stichprobe je Zahl der Reihenfolgen (Mittel über die Zufalls-Seeds, Balken = Streuung)."""
    fig = go.Figure(go.Bar(x=[str(r["m"]) for r in rows], y=[r["err_mean"] for r in rows], error_y=dict(type="data", array=[r["err_std"] for r in rows]),
                           marker_color=C.COLOR_LINE, hovertemplate="m = %{x}: %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Reihenfolgen m", type="category")
    fig.update_yaxes(title_text="größter Fehler (Vielfache des Gleichteils)")
    return _base(fig, 300)
