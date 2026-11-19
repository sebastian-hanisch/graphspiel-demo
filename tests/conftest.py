"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gsd_games import BaseGame  # noqa: E402


@pytest.fixture
def path3():
    """Pfad aus 3 Betrieben mit der Mitte 0 (Verträge 0-1 und 0-2), gleiche Fuhrparks.

    Handrechnung mit v(S) = |S|² über alle 6 Reihenfolgen (Eintritt der Mitte an Stelle 1, 2 oder 3, je mit Wahrscheinlichkeit 1/3):
    Mitte (1 + 3 + 5) / 3 = 3, hier eingeschränkt: Mitte (1 + (4 - 1) + (9 - 2)) / 3 = 11/3, jedes Ende (9 - 11/3) / 2 = 8/3."""
    return 3, ((0, 1), (0, 2)), (1, 1, 1)


@pytest.fixture
def square():
    return BaseGame("potenz", 2.0)
