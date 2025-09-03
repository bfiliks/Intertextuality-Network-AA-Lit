#!/usr/bin/env python3
"""
Build an interactive timeline–network of intertextual influence from a CSV.

CSV schema (edges.csv):
- source_title (str)
- source_year (int)
- target_title (str)
- target_year (int)
- weight (int: 1–3)
- themes (str: semicolon-separated, e.g., "freedom; abolition")
- note (str: optional hover text)

Outputs:
- assets/interactive.html (Plotly interactive with theme filters)
"""

import sys
import csv
from pathlib import Path
import networkx as nx
import plotly.graph_objects as go

REPO_ROOT = Path(__file__).resolve().parent
ASSETS = REPO_ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def normalize_theme(t: str) -> str:
    return t.strip().lower()

def load_edges(csv_path: Path):
    edges = []
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row["source_title"].strip()
            sy = int(row["source_year"])
            tgt = row["target_title"].strip()
            ty = int(row["target_year"])
            w = int(row["weight"])
            themes = [normalize_theme(t) for t in row.get("themes","").split(";") if t.strip()]
            note = row.get("note","").strip()
            edges.append((src, sy, tgt, ty, w, themes, note))
    return edges

def build_graph(edges):
    G = nx.Graph()
    for src, sy, tgt, ty, w, themes, note in edges:
        # Add nodes with year attribute
        G.add_node(src, year=sy)
        G.add_node(tgt, year=ty)
        # Add edge with attributes
        G.add_edge(src, tgt, weight=w, themes=themes, note=note)
    return G

def positions(G):
    # timeline positions: x=year, y=index to reduce overlap
    nodes_sorted = sorted(G.nodes(), key=lambda n: G.nodes[n]["year"])
    y_positions = {n: i for i, n in enumerate(nodes_sorted)}
    return {n: (G.nodes[n]["year"], y_positions[n]) for n in G.nodes()}

def make_edge_trace(G, pos, filter_func, weight=None, name_suffix=""):
    x, y, texts = [], [], []
    for (u, v, data) in G.edges(data=True):
        if not filter_func(u, v, data):
            continue
        if weight is not None and data["weight"] != weight:
            continue
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        x += [x0, x1, None]
        y += [y0, y1, None]
        texts.append(f"{u} → {v}<br>"
                     f"Themes: {', '.join(data.get('themes', [])) or '—'}<br>"
                     f"Influence: {data.get('weight', '?')} / 3<br>"
                     f"{data.get('note','')}")
    if not x:
        # Return an invisible trace to keep button states stable
        return go.Scatter(x=[None], y=[None], mode="lines", line=dict(width=1), hoverinfo="text", text="", visible=False, name=f"edges{name_suffix}")
    width = 2.5 * (weight if weight is not None else 1.5)
    return go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(width=width),
        hoverinfo="text",
        text="<br>".join(texts),
        opacity=0.6,
        name=f"Edges{name_suffix}" + (f" (w={weight})" if weight else ""),
    )

def main():
    csv_path = REPO_ROOT / "edges.csv"
    if not csv_path.exists():
        print(f"CSV not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    edges = load_edges(csv_path)
    if not edges:
        print("No edges found in CSV.", file=sys.stderr)
        sys.exit(1)

    G = build_graph(edges)
    pos = positions(G)

    # collect all themes
    all_themes = sorted({t for _,_,_,_,_,ts,_ in edges for t in ts})

    # traces: all (by weight 2 & 3) + per-theme (by weight) + nodes
    traces = []
    # "All themes" view
    traces.append(make_edge_trace(G, pos, lambda u,v,d: True, weight=2, name_suffix="_all_w2"))
    traces.append(make_edge_trace(G, pos, lambda u,v,d: True, weight=3, name_suffix="_all_w3"))

    # Per-theme views
    theme_traces = []
    for theme in all_themes:
        tr_w2 = make_edge_trace(G, pos, lambda u,v,d, th=theme: th in d.get("themes", []), weight=2, name_suffix=f"_{theme}_w2")
        tr_w3 = make_edge_trace(G, pos, lambda u,v,d, th=theme: th in d.get("themes", []), weight=3, name_suffix=f"_{theme}_w3")
        theme_traces.append((theme, tr_w2, tr_w3))
        traces.extend([tr_w2, tr_w3])

    # nodes
    cent = nx.degree_centrality(G)
    node_trace = go.Scatter(
        x=[pos[n][0] for n in G.nodes()],
        y=[pos[n][1] for n in G.nodes()],
        mode="markers+text",
        text=[f"{n}<br>Year≈{G.nodes[n]['year']}" for n in G.nodes()],
        hovertext=[f"{n}<br>Approx. year: {G.nodes[n]['year']}<br>Degree centrality: {cent[n]:.2f}" for n in G.nodes()],
        hoverinfo="text",
        textposition="top center",
        marker=dict(size=[18 + 40*cent[n] for n in G.nodes()], line=dict(width=1)),
        name="Works",
    )
    traces.append(node_trace)

    fig = go.Figure(traces)

    # visibility helpers
    num_traces = len(traces)
    node_idx = num_traces - 1

    def vis_all():
        vis = [False]*num_traces
        vis[0] = True  # all w2
        vis[1] = True  # all w3
        vis[node_idx] = True
        return vis

    def vis_for_theme(theme):
        vis = [False]*num_traces
        theme_names = [t for t,_,_ in theme_traces]
        t_idx = theme_names.index(theme)
        base = 2 + t_idx*2
        vis[base] = True   # w2
        vis[base+1] = True # w3
        vis[node_idx] = True
        return vis

    buttons = [dict(label="All themes", method="update", args=[{"visible": vis_all()}])]
    for theme, _, _ in theme_traces:
        buttons.append(dict(label=theme, method="update", args=[{"visible": vis_for_theme(theme)}]))

    # layout
    fig.update_layout(
        title="Interactive Timeline–Network with Theme Filters (Book-Level)",
        xaxis=dict(title="Approximate Year", showgrid=True, zeroline=False),
        yaxis=dict(visible=False),
        hovermode="closest",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        updatemenus=[dict(type="dropdown", direction="down", buttons=buttons, x=0.02, y=1.12, xanchor="left", yanchor="top")]
    )

    out_html = ASSETS / "interactive.html"
    fig.write_html(out_html, include_plotlyjs="cdn")
    print(f"Wrote {out_html}")

if __name__ == "__main__":
    main()
