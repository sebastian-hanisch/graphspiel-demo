"""Zentralitäten aus eigenen Fassungen (Breitensuche, Brandes) und Rangkorrelation mit mittleren Rängen bei Gleichstand."""

from collections import deque

import numpy as np


def _adj_lists(n: int, edges):
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    return adj


def degree_centrality(n: int, edges) -> list[int]:
    deg = [0] * n
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    return deg


def closeness_centrality(n: int, edges) -> list[float]:
    """(n − 1) / Summe der kürzesten Wege; bei nicht zusammenhängendem Netz zählen nur erreichbare Betriebe, skaliert mit r/(n − 1) (wie networkx)."""
    adj = _adj_lists(n, edges)
    out = []
    for s in range(n):
        dist = {s: 0}
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        total = sum(dist.values())
        reach = len(dist) - 1
        out.append(0.0 if total == 0 or n <= 1 else (reach / total) * (reach / (n - 1)))
    return out


def betweenness_centrality(n: int, edges) -> list[float]:
    """Zwischenzentralität (Brandes), normiert mit (n − 1)(n − 2)/2 Paaren; für n < 3 alle 0."""
    adj = _adj_lists(n, edges)
    cb = [0.0] * n
    for s in range(n):
        stack, pred = [], [[] for _ in range(n)]
        sigma = [0] * n
        sigma[s] = 1
        dist = [-1] * n
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            stack.append(u)
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
                if dist[v] == dist[u] + 1:
                    sigma[v] += sigma[u]
                    pred[v].append(u)
        delta = [0.0] * n
        while stack:
            w = stack.pop()
            for u in pred[w]:
                delta[u] += sigma[u] / sigma[w] * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    if n < 3:
        return [0.0] * n
    scale = 1.0 / ((n - 1) * (n - 2))      # jedes Paar wurde von beiden Seiten gezählt
    return [c * scale for c in cb]


def centralities(n: int, edges) -> dict[str, list[float]]:
    return {
        "Grad": [float(d) for d in degree_centrality(n, edges)],
        "Nähe": closeness_centrality(n, edges),
        "Zwischen": betweenness_centrality(n, edges),
    }


def average_ranks(values) -> np.ndarray:
    """Ränge 1 bis n, bei Gleichstand der Mittelwert der belegten Ränge (Toleranz 1e-12 relativ zur Größe der Werte)."""
    v = np.asarray(values, dtype=float)
    order = np.argsort(v, kind="stable")
    ranks = np.zeros(len(v))
    scale = max(1.0, float(np.abs(v).max())) if len(v) else 1.0
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and abs(v[order[j + 1]] - v[order[i]]) <= 1e-12 * scale:
            j += 1
        ranks[order[i: j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def rank_correlation(a, b):
    """Rangkorrelation (Spearman) mit mittleren Rängen; None, wenn eine Seite konstant ist (dann ist sie nicht definiert)."""
    ra, rb = average_ranks(a), average_ranks(b)
    if len(ra) < 2 or np.ptp(ra) == 0 or np.ptp(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])
