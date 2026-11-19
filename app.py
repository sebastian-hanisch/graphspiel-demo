"""Graphspiel: Wert und Verbindungen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Betriebe sind über Verträge verbunden, nur zusammenhängende Gruppen arbeiten zusammen (Myerson-Wert). Aufbau nach DEMO-PLAYBOOK §2.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import gsd_constants as C
import gsd_cut as K
import gsd_evaluation as E
import gsd_scenario as S
from gsd_evaluation import Settings, analyse, de
from gsd_layout import dunkles_design, kopf_css
from gsd_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from gsd_texts import ASSUMPTIONS_MARKDOWN, EXPLAIN_TABLE, LITERATUR, LITERATUR_HEAD
from gsd_visualization import (
    build_cut,
    build_hub_curve,
    build_network,
    build_payout,
    build_sample_errors,
    build_sign_heatmap,
    labels,
)

st.set_page_config(page_title="Graphspiel – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _curve(edges, weights):
    return E.hub_curve(edges, weights)


@st.cache_data(show_spinner=False)
def _positions(n, edges):
    return S.layout_positions(n, edges)


@st.cache_data(show_spinner=False)
def _position_compare(settings):
    return E.compare_position(_analysis(settings))


@st.cache_data(show_spinner=False)
def _e1():
    t0 = time.perf_counter()
    rows = E.sign_table()
    return rows, time.perf_counter() - t0


@st.cache_data(show_spinner=False)
def _e2():
    t0 = time.perf_counter()
    rows = E.cut_table()
    return rows, time.perf_counter() - t0


@st.cache_data(show_spinner=False)
def _e3():
    t0 = time.perf_counter()
    rows = E.sample_table()
    large = E.large_net_sample()
    timing = E.exact_timing()
    return rows, large, timing, time.perf_counter() - t0


def _start(key):
    st.session_state[key] = True


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gsd_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Graphspiel: Wert und Verbindungen")
st.markdown(
    """
Betriebe sind über **Verträge** verbunden, und nur **zusammenhängende Gruppen** arbeiten zusammen. **Wer bekommt dann wie viel, und was ändert sich, wenn eine Verbindung wegfällt?**
Die Antwort ist der **Myerson-Wert**: der Shapley-Wert eines Spiels, in dem eine Gruppe nur so viel wert ist wie die Summe ihrer zusammenhängenden Teile. Anders als der reine Shapley-Wert (`shapley-demo`) kennt er
das Netz; anders als die Zentralitäten (`centrality-demo`) sagt er, **was ein Betrieb bekommt**, und das hängt am Basisspiel: Bei Skaleneffekt verdient die Nabe, bei Überlastung kann sie verlieren.
Gruppenwerte, Fuhrparks und Netze sind **Modellannahmen**, keine Daten echter Verträge.

Unten: der Abschnitt **❓ Kernfrage**, vier Ansichten (**Verbindung kappen**, **Zentralität gegen Wert**, **Kanten als Spieler**, **Rechengrenze**), **🚧 Wo die Annahmen enden** und die Expander
**⚠️ Annahmen, Grenzen und bekannte Probleme** und **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Myerson-Wert", expanded=True):
    st.markdown(
        """
1. **Basisspiel:** Jede Gruppe von Betrieben hat einen Wert, aus der Summe ihrer Fuhrparks (bei „Fixkosten“ auch aus der Zahl der Betriebe).
2. **Netz:** Von einer Gruppe zählen nur die Teile, die über Verträge zusammenhängen; ihre Werte werden addiert (das **eingeschränkte Spiel**).
3. **Verteilung:** Der Shapley-Wert dieses eingeschränkten Spiels ist der Myerson-Wert. **Warum das ein sinnvoller Wert ist:** Er verteilt jeden zusammenhängenden Teil vollständig auf seine Mitglieder, und fällt ein Vertrag weg, ändert sich der Wert seiner beiden Enden um denselben Betrag (Myerson 1977).
        """
    )
    st.markdown(EXPLAIN_TABLE)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    family = st.selectbox("Netzform", C.FAMILIES, key="family_select", help="Wie die Betriebe über Verträge verbunden sind. Die Zufallsnetze sind immer zusammenhängend.")
    n = st.slider("Betriebe n", *bounds("n_slider"), key="n_slider", help="Bis n = 12 rechnet die App den Myerson-Wert exakt über alle Teilmengen.")
    st.markdown("**Spiel**")
    game = st.selectbox("Basisspiel", tuple(C.GAMES), key="game_select",
                        help="Wert einer Gruppe aus ihrer Fuhrpark-Summe: Potenz (a < 1 Überlastung, a > 1 Skaleneffekt), Sättigung, Schwelle oder Fixkosten.")
    weights_mode = st.selectbox("Fuhrparks", C.WEIGHT_MODES, key="weights_select", help="Gleiche Fuhrparks, oder je Betrieb 1, 2, 3 oder 5 gezogen (Zufalls-Seed).")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Legt bei den Zufallsnetzen das Netz und bei ungleichen Fuhrparks die Gewichte fest; feste Netzformen mit gleichen Fuhrparks hängen nicht vom Seed ab.")
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)

sync_query_params({"family_select": family, "n_slider": int(n), "game_select": game, "weights_select": weights_mode, "seed_input": int(seed)})

settings = Settings(family, int(n), game, weights_mode, int(seed))
a = _analysis(settings)
nn = a.n
pos = _positions(nn, a.edges)
vn = a.value_total

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Wert der großen Koalition v(N)", de(vn))
m2.metric("Verträge im Netz", f"{len(a.edges)}")
m3.metric("Vom Netz umverteilt", f"{de(a.distance * 100, 1)} %", help="Halbe Summe der Abstände Myerson-Wert gegen Shapley-Wert ohne Netz, in Prozent von v(N).")
hub = a.hub_ratio
m4.metric("Nabe: Myerson ÷ ohne Netz", "–" if hub is None else de(hub), help="Mittel über die Betriebe mit den meisten Verträgen; 1 heißt: das Netz ändert nichts.")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(build_network(nn, a.edges, pos, a.ratios), width="stretch", key="net_chart")
    st.caption("Farbe: Myerson-Wert geteilt durch den Shapley-Wert ohne Netz (rot mehr, blau weniger als ohne Netz).")
with c2:
    st.plotly_chart(build_payout(nn, a.myerson, a.shapley), width="stretch", key="payout_chart")
    st.caption("Bezug je Betrieb: der Shapley-Wert des Basisspiels ohne Netz (bei gleichen Fuhrparks der Gleichteil v(N)/n).")

table = []
for i in range(nn):
    ratio = a.ratios[i]
    table.append({
        "Betrieb": f"B{i + 1}", "Fuhrpark": f"{a.weights[i]}", "Verträge": f"{a.degree[i]}",
        "Ohne Netz (Shapley)": de(a.shapley[i], 3), "Mit Netz (Myerson)": de(a.myerson[i], 3), "Verhältnis": "–" if ratio is None else de(ratio, 3),
        "Nähe": de(a.cent["Nähe"][i], 3), "Zwischen": de(a.cent["Zwischen"][i], 3),
    })
st.dataframe(table, hide_index=True, width="stretch")
st.caption("Nähe und Zwischen sind die üblichen Zentralitäten des Netzes (eigene Fassungen, normiert); sie hängen nicht vom Basisspiel ab, der Myerson-Wert schon.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wer bekommt wie viel, wenn nur Zusammenhängendes zählt?")
kind, text = E.verdict_kernfrage(a.distance, hub, a.equal_degrees)
getattr(st, kind)(text)

st.markdown("---")

# --- Ansichten -----------------------------------------------------------------------------------------------------------------------------

tab_cut, tab_cen, tab_pos, tab_limit = st.tabs(["✂️ Verbindung kappen", "📈 Zentralität gegen Wert", "🧪 Kanten als Spieler", "⏱️ Rechengrenze"])

with tab_cut:
    st.subheader("🔬 Experiment: Was verlieren die beiden Enden, wenn ein Vertrag wegfällt?")
    edge_list = list(a.edges)
    if st.session_state.get("cut_edge") not in range(len(edge_list)):
        st.session_state["cut_edge"] = 0
    k = st.selectbox("Vertrag, der wegfällt", range(len(edge_list)), key="cut_edge", format_func=lambda idx: f"B{edge_list[idx][0] + 1} – B{edge_list[idx][1] + 1}")
    edge = edge_list[k]
    effect = K.cut_edge(nn, a.edges, a.weights, a.game, edge)
    near, far = effect.third_changes(a.edges)
    near_mean = sum(near) / len(near) if near else None
    far_mean = sum(far) / len(far) if far else None
    kind, text = E.verdict_cut(effect.end_change, effect.is_bridge, near_mean, far_mean)
    getattr(st, kind)(text)
    cc1, cc2 = st.columns(2)
    with cc1:
        st.plotly_chart(build_network(nn, a.edges, pos, a.ratios, highlight=edge), width="stretch", key="cut_net_chart")
    with cc2:
        st.plotly_chart(build_cut(nn, effect.change, edge), width="stretch", key="cut_change_chart")
    st.caption("Rot gestrichelt: der Vertrag, der wegfällt. Rechts: Änderung des Myerson-Werts je Betrieb (nachher minus vorher). Eine Brücke ist ein Vertrag, ohne den das Netz in zwei Teile zerfällt.")

    st.subheader("🔬 Experiment: Gilt das auf vielen Zufallsnetzen?")
    st.caption(f"Alle Kappungen in {len(C.SWEEP_SEEDS) * C.NETS_PER_SEED} Zufallsnetzen je Netzform ({len(C.SWEEP_SEEDS)} feste Zufalls-Seeds mit je {C.NETS_PER_SEED} Netzen, n = {C.CUT_N}, gleiche Fuhrparks): "
               "Zufallsnetz dünn und Zufallsbaum, vier Basisspiele. Gezählt wird über die Kappungen, nicht über die Netze.")
    st.button("Messreihe starten (dauert einige Sekunden)", key="e2_start", on_click=_start, args=("e2_on",))
    if st.session_state.get("e2_on"):
        with st.spinner("Rechne alle Kappungen …"):
            rows2, secs2 = _e2()
        kind, text = E.verdict_cutting(rows2)
        getattr(st, kind)(text)
        st.dataframe([{
            "Netzform": r["family"], "Basisspiel": r["game"], "Kappungen": r["cuts"], "beide Enden verlieren": r["both_lose"], "beide Enden gewinnen": r["both_gain"],
            "Brücken": r["bridges"], "Brücken mit gewinnendem Dritten": r["bridge_third_gain"], "Nicht-Brücken": r["nonbridges"],
            "Nachbar im Mittel": "–" if r["near_mean"] is None else de(r["near_mean"], 3), "andere Dritte im Mittel": "–" if r["far_mean"] is None else de(r["far_mean"], 3),
        } for r in rows2], hide_index=True, width="stretch")
        st.caption(f"Rechenzeit dieser Messreihe: {de(secs2, 1)} s auf diesem Rechner. Nachbar: Betrieb, der im Netz mit mindestens einem Ende der gekappten Verbindung verbunden ist (nur bei Nicht-Brücken).")

with tab_cen:
    st.subheader("🔬 Experiment: Folgt der Wert dem Grad? Das Vorzeichen hängt am Basisspiel")
    corr = []
    for name_c in ("Grad", "Nähe", "Zwischen"):
        r = E.rank_correlation(a.myerson, a.cent[name_c])
        corr.append("nicht definiert" if r is None else de(r, 2))
    cm = st.columns(3)
    for col, name_c, val in zip(cm, ("Grad", "Nähe", "Zwischen"), corr):
        col.metric(f"Rangkorrelation Myerson ↔ {name_c}", val, help="Rangkorrelation (Spearman) über die Betriebe dieses Netzes; nicht definiert, wenn eine Seite konstant ist.")
    curve = _curve(a.edges, a.weights)
    kind, text = E.verdict_curve(curve)
    getattr(st, kind)(text)
    st.plotly_chart(build_hub_curve(curve), width="stretch", key="curve_chart")
    st.caption("Dieses Netz und diese Fuhrparks, Potenzspiele mit Exponenten von 0,5 bis 3. Unter der Linie 1 bekommen die Betriebe mit den meisten Verträgen weniger als ohne Netz.")

    st.markdown("**Auf vielen Netzen und mit anderen Basisspielen**")
    st.caption(f"Rangkorrelation Myerson-Wert gegen Grad, n = {C.EXPERIMENT_N}, gleiche Fuhrparks. Zufallsnetze und Zufallsbaum: Mittel über {len(C.SWEEP_SEEDS)} feste Zufalls-Seeds mit je {C.NETS_PER_SEED} Netzen; "
               "Hantel: ein Netz. Leere Zellen: Korrelation nicht definiert (der Myerson-Wert ist für alle Betriebe gleich).")
    st.button("Messreihe starten (dauert einige Sekunden)", key="e1_start", on_click=_start, args=("e1_on",))
    if st.session_state.get("e1_on"):
        with st.spinner("Rechne Netze und Basisspiele …"):
            rows1, secs1 = _e1()
        kind, text = E.verdict_sign(rows1)
        getattr(st, kind)(text)
        st.plotly_chart(build_sign_heatmap(rows1, E.E1_FAMILIES, tuple(C.GAMES)), width="stretch", key="sign_chart")
        st.dataframe([{
            "Netzform": r["family"], "Basisspiel": r["game"], "Netze": r["nets"], "Korrelation definiert": r["defined"],
            "Rangkorrelation": "–" if r["rho"] is None else de(r["rho"], 3), "Streuung über Seeds": "–" if r["rho_std"] is None else de(r["rho_std"], 3),
            "Meiste Verträge ÷ ohne Netz": "–" if r["hub"] is None else de(r["hub"], 2), "Spitze = höchster Grad": de(r["top_ok"] * 100, 0) + " %",
        } for r in rows1], hide_index=True, width="stretch")
        st.caption(f"Rechenzeit dieser Messreihe: {de(secs1, 1)} s auf diesem Rechner. Spitze = höchster Grad: Anteil der Netze, in denen ein Betrieb mit dem höchsten Myerson-Wert auch höchsten Grad hat (bei Gleichstand großzügig gezählt).")

with tab_pos:
    st.subheader("🔬 Experiment: Kanten als Spieler (Positionswert)")
    if len(a.edges) > C.POSITION_MAX_EDGES:
        st.info(f"Dieses Netz hat {len(a.edges)} Verträge; der Positionswert zählt alle 2^Verträge Mengen von Verträgen und wird nur bis {C.POSITION_MAX_EDGES} Verträge berechnet. "
                "Ein Netz mit weniger Verträgen (zum Beispiel Stern, Pfad, Ring oder ein Zufallsbaum) wählen.")
    else:
        cmp = _position_compare(settings)
        kind, text = E.verdict_position(cmp)
        getattr(st, kind)(text)
        st.dataframe([{"Betrieb": f"B{i + 1}", "Myerson-Wert": de(cmp.myerson[i], 3), "Positionswert": de(cmp.position[i], 3)} for i in range(nn)], hide_index=True, width="stretch")
    st.caption("Beim Positionswert sind nicht die Betriebe, sondern die Verträge die Spieler: Jeder Vertrag bekommt seinen Shapley-Wert, jeder Betrieb die Hälfte der Werte seiner Verträge plus seinen Einzelwert. "
               "Die Definition steht unter 📐; ob sie der Originalarbeit entspricht, ist nicht geprüft.")

with tab_limit:
    st.subheader("🔬 Experiment: Wo reicht der exakte Weg, und was leistet die Stichprobe?")
    st.caption(f"Exakt: alle 2^n Teilmengen. Stichprobe: m zufällige Reihenfolgen. Gemessen wird auf einem festen Zufallsnetz mit n = 16 (Quadratisch, gleiche Fuhrparks, {len(C.SWEEP_SEEDS)} Zufalls-Seeds), "
               "dazu die Rechenzeit des exakten Wegs bis n = 20 und eine Stichprobe auf einem Netz mit 200 Betrieben. Die Messung braucht einige Sekunden; die gemessene Zeit steht danach unter den Tabellen.")
    st.button("Messreihe starten (dauert einige Sekunden)", key="e3_start", on_click=_start, args=("e3_on",))
    if st.session_state.get("e3_on"):
        with st.spinner("Rechne Stichproben und exakte Läufe …"):
            rows3, large, timing, secs3 = _e3()
        kind, text = E.verdict_sample(rows3)
        getattr(st, kind)(text)
        st.plotly_chart(build_sample_errors(rows3), width="stretch", key="sample_chart")
        st.dataframe([{"Reihenfolgen m": r["m"], "größter Fehler (Gleichteile)": de(r["err_mean"], 3), "Streuung über Seeds": de(r["err_std"], 3),
                       "Rangkorrelation": de(r["rho"], 3), "gleicher Spitzenspieler": de(r["top_ok"] * 100, 0) + " %", "Sekunden je Lauf": de(r["seconds"], 2)} for r in rows3],
                     hide_index=True, width="stretch")
        st.dataframe([{"Betriebe n": r["n"], "Verträge": r["edges"], "Sekunden exakt": de(r["seconds"], 3)} for r in timing], hide_index=True, width="stretch")
        st.info(f"Auf einem Preferential-Attachment-Netz mit {large['n']} Betrieben und {large['m']} Reihenfolgen ({de(large['seconds'], 1)} s) liegt der größte Standardfehler bei "
                f"{de(large['max_se'], 3)} Gleichteilen, der größte Wert (die Nabe) bei {de(large['hub_value'], 2)} Gleichteilen.")
        st.caption(f"Gesamte Rechenzeit: {de(secs3, 1)} s auf diesem Rechner; die Zeiten hängen von dessen Last ab.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Das Basisspiel ist gegeben** (Potenz, Sättigung, Schwelle, Fixkosten) | Das Vorzeichen der Wirkung hängt am Basisspiel (Experiment „Folgt der Wert dem Grad?“): Bei Überlastung kann eine Nabe verlieren; bei den Fixkosten ändert sich ihr Wert in den Zufallsnetzen kaum (0,93 bis 1,04), auf der Hantel mit c = −1 sinkt er auf das 0,70-fache. | die Experimente in dieser Demo; echte Gruppenwerte liefert diese Demo nicht |
| **Das Netz ist fest und kostenlos** | Wer Verträge schließt oder kappt, ändert das Spiel selbst; das Kappen im Tab ist nur ein Vergleich zweier fester Netze. | hier nicht behandelt |
| **Keine Abspaltung** | Ob sich eine zusammenhängende Gruppe auf eigene Faust besserstellt (Kern), wird hier nicht gefragt. | `kern-demo` (ohne Netz); mit Netz hier nicht gemessen |
| **Die Betriebe handeln nicht strategisch** | Der Myerson-Wert ist eine Verteilungsregel, kein Gleichgewicht: Welche Aktion jeder wählt, steht nicht im Modell. | `netzwerkspiel-demo` (Gleichgewicht eines Spiels auf dem Netz) |
| **Zusammenarbeit heißt Wert einer Gruppe** | Kooperation als Paarung auf einem Graphen (jeder Betrieb mit höchstens einem Partner) ist ein anderes Modell. | `austauschnetz-demo` |
| **Das Netz wird nur durch Grad, Nähe und Zwischen beschrieben** | Andere Maße (zum Beispiel Constraint und effektive Größe am Ego-Netz) liefern andere Rangfolgen. | `centrality-demo`, `strukturelle-loecher-demo` |
"""
)

st.markdown("---")

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(ASSUMPTIONS_MARKDOWN)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind $n$ Betriebe $N=\{1,\dots,n\}$, ein Netz $G$ (Menge von Verträgen $ij$) und Fuhrparks $w_i$. Gesucht ist für jeden Betrieb sein Anteil am Gesamtwert.

| Symbol | Bedeutung |
|---|---|
| $N$, $n$ | Menge und Zahl der Betriebe |
| $w_i$ | Fuhrpark des Betriebs $i$ |
| $x(S)$ | Fuhrpark-Summe der Gruppe $S$ |
| $v(S)$ | Wert der Gruppe $S$ im Basisspiel |
| $G[S]$ | Netz $G$ eingeschränkt auf die Gruppe $S$ |
| $S/G$ | Menge der zusammenhängenden Teile von $S$ im Netz $G$ |
| $v^G(S)$ | Wert der Gruppe $S$ im eingeschränkten Spiel |
| $\varphi^{Sh}_i$, $\varphi^{M}_i$ | Shapley-Wert und Myerson-Wert des Betriebs $i$ |
| $a$, $K$, $t$, $c$ | Exponent, Sättigung, Schwelle und Fixkosten des Basisspiels |

**Basisspiele** (Wert einer Gruppe aus ihrer Fuhrpark-Summe $x$ und der Zahl $m$ ihrer Betriebe).

$$v_{\text{Potenz}}(x) = x^{a}$$

$$v_{\text{Sättigung}}(x) = x \cdot \min(x, K)$$

$$v_{\text{Schwelle}}(x) = \begin{cases} 1 & x \ge t \\ 0 & x < t \end{cases}$$

$$v_{\text{Fixkosten}}(x, m) = \begin{cases} x - c & m \ge 2 \\ x & m = 1 \end{cases}$$

**Eingeschränktes Spiel.** Von einer Gruppe zählen nur die zusammenhängenden Teile:

$$v^{G}(S) = \sum_{C \in S/G} v(C)$$

**Myerson-Wert** = Shapley-Wert des eingeschränkten Spiels:

$$\varphi^{M}_i(v, G) = \varphi^{Sh}_i(v^{G}) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!\,(n - |S| - 1)!}{n!} \left( v^{G}(S \cup \{i\}) - v^{G}(S) \right)$$

**Eigenschaften** (Myerson 1977; in dieser Demo an Zufallsnetzen geprüft): Jeder zusammenhängende Teil $C$ des Netzes verteilt genau seinen Wert,

$$\sum_{i \in C} \varphi^{M}_i(v, G) = v(C)$$

und fällt ein Vertrag $ij$ weg, ändert sich der Wert beider Enden um denselben Betrag (Gleichverlust):

$$\varphi^{M}_i(v, G) - \varphi^{M}_i(v, G \setminus ij) = \varphi^{M}_j(v, G) - \varphi^{M}_j(v, G \setminus ij)$$

**Stern** mit Nabe und $k$ Blättern, gleiche Fuhrparks, $f(j)$ = Wert einer Gruppe aus $j$ Betrieben (Handformel, gegen den Zählweg getestet): Die Nabe tritt an einer gleichverteilten Stelle $j = 0, \dots, k$ ein und bringt $f(j+1) - j\,f(1)$.

$$\varphi^{M}_{\text{Nabe}} = \frac{1}{k+1} \sum_{j=0}^{k} \left( f(j+1) - j\,f(1) \right)$$

$$\varphi^{M}_{\text{Blatt}} = \frac{f(k+1) - \varphi^{M}_{\text{Nabe}}}{k}$$

**Kennzahlen der App.** Bezug ist der Shapley-Wert ohne Netz $\varphi^{Sh}_i(v)$; der Anteil, den das Netz umverteilt, ist

$$D = \frac{1}{2\,v(N)} \sum_{i \in N} \left| \varphi^{M}_i(v, G) - \varphi^{Sh}_i(v) \right|$$

**Stichprobe.** Für $m$ zufällige Reihenfolgen $\pi_1, \dots, \pi_m$ der Betriebe und $P_i^{k}$ die Betriebe vor $i$ in $\pi_k$:

$$\hat{\varphi}_i = \frac{1}{m} \sum_{k=1}^{m} \left( v^{G}(P_i^{k} \cup \{i\}) - v^{G}(P_i^{k}) \right)$$

Der Standardfehler ist die Standardabweichung der Summanden geteilt durch $\sqrt{m}$.

**Positionswert** (Kanten als Spieler, Definition dieser Demo). $r(F)$ ist der Wert des Netzes mit der Vertragsmenge $F$, $E$ die Menge der Verträge, $\varphi^{Sh}_e$ der Shapley-Wert des Vertrags $e$ im Spiel $r - r(\emptyset)$:

$$r(F) = \sum_{C \in N/F} v(C)$$

$$\pi_i = v(\{i\}) + \frac{1}{2} \sum_{e \in E,\; i \in e} \varphi^{Sh}_e(r - r(\emptyset))$$

Das Modell ist vollständig für die in der Demo gerechneten Größen (Basisspiele, eingeschränktes Spiel, Myerson-Wert, Stichprobe); Netzfamilien und Zufallsziehungen sind in der README beschrieben.
        """
    )
    st.markdown(LITERATUR_HEAD)
    st.markdown("\n".join(LITERATUR))

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Koalitionen und Teilen: Macht und Aufteilung](https://sebastianhanisch.net/konzepte-koalitionen-teilen.html)."
)
