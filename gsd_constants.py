"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 3, 12, 10        # bis n = 12 rechnet die App den Myerson-Wert live exakt (2^12 Teilmengen)
SEED_MAX, DEFAULT_SEED = 999999, 35
SWEEP_SEEDS = (11, 22, 33, 44)             # feste Zufalls-Seeds für alle Messreihen: nie ein einzelner Seed als Befund
NETS_PER_SEED = 15                         # Netze je Zufalls-Seed und Zelle in den Experimenten der App
EXPERIMENT_N = 10                          # Betriebe in E1 (Zentralität gegen Wert)
CUT_N = 8                                  # Betriebe in E2 (Verbindung kappen auf Zufallsnetzen)
POSITION_MAX_EDGES = 14                    # Positionswert: 2^Kanten Koalitionen von Kanten; darüber nur Hinweis
EXACT_LIMIT_BUTTON = 20                    # Rechengrenze-Tab: exakt bis n = 20 (2^20 Teilmengen) auf Klick
SAMPLE_N_MAX = 200                         # Stichprobe: größte Zahl Betriebe im Rechengrenze-Tab (Union-Find je Reihenfolge)
SAMPLE_SIZES = (100, 1000, 10000)          # Zahl der Reihenfolgen im Stichprobenvergleich
WEIGHT_CHOICES = (1, 2, 3, 5)              # Fuhrparkgrößen bei "ungleich"

P_THIN, P_DENSE = 0.25, 0.5                # Kantenwahrscheinlichkeit der beiden Zufallsnetze

# Laufzeit am Regler-Maximum: Exakter Weg O(2^n * n), Speicher O(2^n); Stichprobe O(m * n * Grad)

FAMILIES = (
    "Stern", "Pfad", "Ring", "Hantel", "Vollständig",
    "Zufallsnetz dünn", "Zufallsnetz dicht", "Zufallsbaum", "Preferential Attachment",
)

# Basisspiele: (Art, Parameter). Wert einer Gruppe aus der Fuhrpark-Summe x = Σ wᵢ und der Zahl m ihrer Betriebe.
GAMES = {
    "Überlastung (a = 0,5)": ("potenz", 0.5),
    "Leichte Überlastung (a = 0,75)": ("potenz", 0.75),
    "Additiv (a = 1)": ("potenz", 1.0),
    "Skaleneffekt (a = 1,5)": ("potenz", 1.5),
    "Quadratisch (a = 2)": ("potenz", 2.0),
    "Starker Skaleneffekt (a = 3)": ("potenz", 3.0),
    "Sättigung (K = 3)": ("saettigung", 3.0),
    "Schwelle (t = 3)": ("schwelle", 3.0),
    "Fixkosten (c = 0,5)": ("fixkosten", 0.5),
    "Abstimmungsgewinn (c = −1)": ("fixkosten", -1.0),
}
DEFAULT_GAME = "Quadratisch (a = 2)"
EXPONENTS = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0)      # Raster der Exponenten in E1
A_CURVE = tuple(round(0.5 + 0.25 * i, 2) for i in range(11))   # 0,5 bis 3,0 für die Kurve des aktuellen Netzes

WEIGHT_MODES = ("gleich (alle Fuhrparks 1)", "ungleich (1, 2, 3 oder 5 gezogen)")

COLOR_MYERSON = "#2F6B65"
COLOR_SHAPLEY = "#b8b8b8"
COLOR_CUT = "#c0392b"
COLOR_LINE = "#4c78a8"
COLOR_EDGE = "rgba(120,120,120,0.55)"

PRESETS = {
    "Stern: die Nabe verdient": {"family": "Stern", "n": 10, "game": "Quadratisch (a = 2)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
    "Überlastung: die Nabe verliert": {"family": "Stern", "n": 10, "game": "Überlastung (a = 0,5)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
    "Hantel: die Brücke": {"family": "Hantel", "n": 10, "game": "Quadratisch (a = 2)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
    "Ring: keine Wirkung": {"family": "Ring", "n": 10, "game": "Quadratisch (a = 2)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
    "Zufallsnetz": {"family": "Zufallsnetz dünn", "n": 10, "game": "Quadratisch (a = 2)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
    "Ungleiche Fuhrparks": {"family": "Zufallsnetz dünn", "n": 10, "game": "Skaleneffekt (a = 1,5)", "weights": WEIGHT_MODES[1], "seed": DEFAULT_SEED},
    "Gegenbeispiel: Schwelle auf der Hantel": {"family": "Hantel", "n": 10, "game": "Schwelle (t = 3)", "weights": WEIGHT_MODES[0], "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Stern: die Nabe verdient": "Ein Betrieb in der Mitte, neun an Verträgen mit ihm; Skaleneffekt (a = 2). Die Nabe bekommt ein Vielfaches ihres Gleichteils.",
    "Überlastung: die Nabe verliert": "Dasselbe Netz, aber Gruppen werden mit wachsender Größe weniger wert (a = 0,5): die Nabe bekommt weniger als ohne Netz, im Stern sogar ein negatives Ergebnis.",
    "Hantel: die Brücke": "Zwei Fünfergruppen, die nur über einen Vertrag verbunden sind. Die beiden Betriebe an der Brücke verdienen mehr.",
    "Ring: keine Wirkung": "Jeder hat zwei Verträge, alle Fuhrparks sind gleich: der Myerson-Wert ist gleich dem Wert ohne Netz.",
    "Zufallsnetz": "Zufällig gezogenes dünnes Netz (Kantenwahrscheinlichkeit 0,25, Komponenten werden verbunden). Über „Neue Instanz“ lassen sich weitere ziehen.",
    "Ungleiche Fuhrparks": "Fuhrparkgrößen 1, 2, 3 oder 5: Gewicht und Lage im Netz wirken zusammen; Bezug ist der Wert ohne Netz, nicht der Gleichteil.",
    "Gegenbeispiel: Schwelle auf der Hantel": "Eine Gruppe ist erst ab Fuhrpark-Summe 3 etwas wert: die Regel „viel verbunden, viel verdient“ gilt hier nicht.",
}
