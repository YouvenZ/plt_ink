"""
Clustered Correlation Matrix
Correlation heatmap reordered by average-linkage hierarchical clustering, with
the dendrogram, significance markers and cluster blocks outlined. Clustering
and dendrogram are implemented in numpy, so no scipy is required.
requires_data: true
data_columns: (any wide numeric table)
sample_data: omics_matrix.csv
tags: statistics, correlation, clustering, heatmap, omics
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
SAMPLE = 'omics_matrix.csv'
DROP_COLUMNS = ('sample_id', 'group')      # identifiers, not measurements
METHOD = 'pearson'
N_CLUSTERS = 4             # blocks to outline; None disables
ALPHA = 0.05               # significance threshold for the markers


def _opt(name, default):
    value = globals().get(name)
    return default if value is None else value


def _sample_dir():
    """Folder holding the bundled example data.

    The extension injects `_sample_data_dir`; the `__file__` branch only
    matters when the template is run straight from the bank folder. Looked up
    lazily because `__file__` is undefined when the code is exec'd inline.
    """
    root = globals().get('_sample_data_dir')
    if root:
        return root
    here = globals().get('__file__')
    if here:
        return os.path.join(os.path.dirname(os.path.abspath(here)),
                            '..', '..', 'sample_data')
    return 'sample_data'


def _load(sample):
    frame = globals().get('data')
    if frame is None:
        frame = pd.read_csv(os.path.join(_sample_dir(), sample))
    return frame.copy()


df = _load(SAMPLE)
numeric = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns],
                  errors='ignore').select_dtypes(include=[np.number])
corr = numeric.corr(method=METHOD)
labels = list(corr.columns)
matrix = corr.to_numpy(float)
n_vars = len(labels)
n_obs = len(numeric)


def average_linkage(distance):
    """Agglomerative average-linkage clustering (UPGMA).

    Returns the merge list [(left, right, height, size)] with cluster ids
    numbered n, n+1, ... as they are created — the same convention scipy uses,
    so the dendrogram code below reads like the familiar one.
    """
    n = distance.shape[0]
    active = {i: [i] for i in range(n)}
    d = distance.astype(float).copy()
    np.fill_diagonal(d, np.inf)
    merges = []
    ids = {i: i for i in range(n)}
    next_id = n
    while len(active) > 1:
        keys = list(active)
        sub = d[np.ix_(keys, keys)]
        flat = int(np.argmin(sub))
        i, j = np.unravel_index(flat, sub.shape)
        a, b = keys[i], keys[j]
        height = float(sub[i, j])
        merged = active[a] + active[b]
        merges.append((ids[a], ids[b], height, len(merged)))
        # Average linkage: the new distance is the size-weighted mean.
        for k in active:
            if k in (a, b):
                continue
            d[a, k] = d[k, a] = (
                (d[a, k] * len(active[a]) + d[b, k] * len(active[b]))
                / (len(active[a]) + len(active[b])))
        active[a] = merged
        ids[a] = next_id
        next_id += 1
        del active[b]
        d[b, :] = np.inf
        d[:, b] = np.inf
    return merges


def leaf_order(merges, n):
    """Depth-first leaf order — the permutation that makes the blocks contiguous."""
    children = {n + k: (m[0], m[1]) for k, m in enumerate(merges)}

    def walk(node):
        if node < n:
            return [node]
        left, right = children[node]
        return walk(left) + walk(right)

    return walk(n + len(merges) - 1) if merges else list(range(n))


def cut_tree(merges, n, k):
    """Cluster assignment obtained by cutting the tree into k groups."""
    parent = {}
    members = {i: [i] for i in range(n)}
    for idx, (a, b, _, _) in enumerate(merges[:max(n - k, 0)]):
        node = n + idx
        members[node] = members[a] + members[b]
        parent[a] = parent[b] = node
    roots = [node for node in members if node not in parent]
    assignment = np.zeros(n, dtype=int)
    for label, root in enumerate(roots):
        for leaf in members[root]:
            assignment[leaf] = label
    return assignment


# Correlation distance: variables that move together end up adjacent.
distance = 1.0 - np.abs(matrix)
merges = average_linkage(distance)
order = leaf_order(merges, n_vars)
ordered = matrix[np.ix_(order, order)]
ordered_labels = [labels[i] for i in order]

# ── Significance of each correlation ─────────────────────────────────────────
def erf(x):
    """Abramowitz & Stegun 7.1.26 — accurate to ~1e-7, and no scipy."""
    sign = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t
                 - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x))
    return sign * y


with np.errstate(divide='ignore', invalid='ignore'):
    t_stat = (ordered * np.sqrt(max(n_obs - 2, 1))
              / np.sqrt(np.clip(1 - ordered ** 2, 1e-12, None)))
# Two-sided tail: P(|Z| > z) = 1 - erf(z / sqrt(2)). The normal approximation
# to t is ample at these sample sizes.
p_values = np.clip(1.0 - erf(np.abs(t_stat) / np.sqrt(2.0)), 0.0, 1.0)

W = _opt('_fig_width', 10.0)
H = _opt('_fig_height', 9.0)
# Keep the heatmap cells near-square regardless of the configured figure size.
H = max(H, W * 0.92)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 4.2], height_ratios=[1.0, 4.2],
                      hspace=0.02, wspace=0.02)
ax = fig.add_subplot(gs[1, 1])
ax_top = fig.add_subplot(gs[0, 1], sharex=ax)
ax_left = fig.add_subplot(gs[1, 0], sharey=ax)

# aspect='auto', not 'equal': an equal-aspect imshow shrinks its own axes box,
# which breaks alignment with the shared-axis dendrograms beside it. The figure
# is sized instead so the cells come out close to square.
im = ax.imshow(ordered, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label(f'{METHOD.title()} correlation')

# Significance markers rather than printed p-values — readable at this density.
for i in range(n_vars):
    for j in range(n_vars):
        if i == j or p_values[i, j] >= ALPHA:
            continue
        if abs(ordered[i, j]) > 0.45:
            ax.text(j, i, '*', ha='center', va='center', fontsize=7,
                    color='white' if abs(ordered[i, j]) > 0.6 else '#333333')

ax.set_xticks(range(n_vars))
ax.set_yticks(range(n_vars))
ax.set_xticklabels(ordered_labels, rotation=60, ha='right', fontsize=8)
ax.set_yticklabels(ordered_labels, fontsize=8)
ax.grid(False)


def draw_dendrogram(dend_ax, merges, n, order, horizontal):
    """Draw the tree with leaves at their positions in `order`."""
    coords = {leaf: idx for idx, leaf in enumerate(order)}
    heights = {leaf: 0.0 for leaf in range(n)}
    for idx, (a, b, height, _) in enumerate(merges):
        xa, xb = coords[a], coords[b]
        ya, yb = heights[a], heights[b]
        if horizontal:
            dend_ax.plot([ya, height, height, yb], [xa, xa, xb, xb],
                         color='#555555', linewidth=1.0)
        else:
            dend_ax.plot([xa, xa, xb, xb], [ya, height, height, yb],
                         color='#555555', linewidth=1.0)
        node = n + idx
        coords[node] = (xa + xb) / 2
        heights[node] = height


draw_dendrogram(ax_top, merges, n_vars, order, horizontal=False)
draw_dendrogram(ax_left, merges, n_vars, order, horizontal=True)

ax_top.set_xlim(-0.5, n_vars - 0.5)
ax_top.set_axis_off()
ax_left.set_ylim(n_vars - 0.5, -0.5)
ax_left.invert_xaxis()
ax_left.set_axis_off()

# Outline the clusters so the blocks the dendrogram implies are visible.
if N_CLUSTERS:
    assignment = cut_tree(merges, n_vars, N_CLUSTERS)[order]
    start = 0
    for i in range(1, n_vars + 1):
        if i == n_vars or assignment[i] != assignment[start]:
            ax.add_patch(plt.Rectangle((start - 0.5, start - 0.5),
                                       i - start, i - start, fill=False,
                                       edgecolor='#111111', linewidth=1.8,
                                       zorder=6))
            start = i

ax_top.set_title(f'Clustered correlation of {n_vars} variables '
                 f'(n = {n_obs} samples, average linkage on 1 - |r|)',
                 fontsize=10.5, loc='left', fontweight='bold')
ax.text(0.0, -0.16, f'* marks |r| > 0.45 with p < {ALPHA:g}.  '
                    f'Outlines are the {N_CLUSTERS} clusters from cutting the tree.',
        transform=ax.transAxes, fontsize=7.5, color='#666666', va='top')
