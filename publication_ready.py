"""
Research Figure: Neural Network Training Dynamics
A publication-quality matplotlib illustration with outstanding annotations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator
from scipy.ndimage import gaussian_filter1d

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ── Color palette (Nature/Cell style + modern accents) ────────────────────────
COLORS = {
    "train":    "#1B4F72",   # deep navy
    "val":      "#E74C3C",   # vivid red
    "baseline": "#95A5A6",   # muted grey
    "accent":   "#F39C12",   # amber
    "bg":       "#FAFAFA",
    "panel_bg": "#FFFFFF",
    "grid":     "#E8E8E8",
    "text":     "#1A1A2E",
    "subtext":  "#555577",
}

# ── Synthetic training data ──────────────────────────────────────────────────
epochs = np.arange(1, 101)

def make_curve(final, noise_scale=0.015, smooth=6):
    raw = final + (1 - final) * np.exp(-epochs / 18) + np.random.randn(100) * noise_scale
    return gaussian_filter1d(raw, smooth)

train_acc = make_curve(0.963, 0.018, 5)
val_acc   = make_curve(0.942, 0.022, 5)
baseline  = np.full(100, 0.891)

train_loss = gaussian_filter1d(1.8 * np.exp(-epochs / 15) + 0.08 + np.random.randn(100) * 0.02, 5)
val_loss   = gaussian_filter1d(2.0 * np.exp(-epochs / 14) + 0.13 + np.random.randn(100) * 0.025, 5)

lr_schedule = np.where(epochs < 30, 1e-3,
              np.where(epochs < 60, 3e-4,
              np.where(epochs < 80, 1e-4, 3e-5)))

# ── Layout ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 9), facecolor=COLORS["bg"])
fig.patch.set_facecolor(COLORS["bg"])

gs = GridSpec(2, 3, figure=fig,
              left=0.08, right=0.97,
              top=0.88,  bottom=0.10,
              hspace=0.45, wspace=0.38)

ax_acc  = fig.add_subplot(gs[0, :2])   # accuracy – wide left
ax_lr   = fig.add_subplot(gs[0, 2])    # lr schedule – right
ax_loss = fig.add_subplot(gs[1, :2])   # loss – wide left
ax_delta= fig.add_subplot(gs[1, 2])    # generalisation gap – right

for ax in [ax_acc, ax_lr, ax_loss, ax_delta]:
    ax.set_facecolor(COLORS["panel_bg"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#CCCCCC")
    ax.tick_params(colors=COLORS["subtext"], labelsize=8)
    ax.yaxis.set_minor_locator(MultipleLocator(0.01))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(which="major", color=COLORS["grid"], linewidth=0.7, linestyle="--")
    ax.grid(which="minor", color=COLORS["grid"], linewidth=0.3, linestyle=":")

# ─────────────────────────────────────────────────────────────────────────────
#  Panel A – Accuracy
# ─────────────────────────────────────────────────────────────────────────────
best_val_ep  = int(np.argmax(val_acc)) + 1
best_val_acc = val_acc[best_val_ep - 1]

ax_acc.fill_between(epochs, train_acc, val_acc, alpha=0.08, color=COLORS["val"])
ax_acc.axhline(baseline[0], color=COLORS["baseline"], lw=1.4,
               ls="--", dashes=(6,3), label="SoTA Baseline (89.1 %)")
ax_acc.plot(epochs, train_acc, color=COLORS["train"], lw=2.2,
            label="Training accuracy", zorder=4)
ax_acc.plot(epochs, val_acc,   color=COLORS["val"],   lw=2.2,
            label="Validation accuracy", zorder=4)

# Annotate best epoch
ax_acc.axvline(best_val_ep, color=COLORS["accent"], lw=1.2, ls=":", alpha=0.8)
ax_acc.scatter([best_val_ep], [best_val_acc], s=80, color=COLORS["accent"],
               zorder=6, edgecolors="white", linewidths=1.2)

ax_acc.annotate(
    f"Best val.\n{best_val_acc:.3f} @ ep. {best_val_ep}",
    xy=(best_val_ep, best_val_acc),
    xytext=(best_val_ep + 7, best_val_acc - 0.025),
    fontsize=7.5, color=COLORS["text"],
    arrowprops=dict(arrowstyle="-|>", color=COLORS["accent"],
                    lw=1.3, connectionstyle="arc3,rad=-0.2"),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS["accent"],
              lw=1, alpha=0.92),
)

# Overfitting gap bracket
ax_acc.annotate("", xy=(92, train_acc[91]), xytext=(92, val_acc[91]),
                arrowprops=dict(arrowstyle="<->", color=COLORS["subtext"], lw=1.2))
ax_acc.text(93.5, (train_acc[91] + val_acc[91]) / 2,
            "Gen.\ngap", fontsize=6.5, color=COLORS["subtext"], va="center")

ax_acc.set_xlim(1, 100); ax_acc.set_ylim(0.80, 1.00)
ax_acc.set_ylabel("Accuracy", fontsize=9, color=COLORS["text"], labelpad=6)
ax_acc.set_xlabel("Epoch", fontsize=9, color=COLORS["text"])
ax_acc.legend(fontsize=7.5, frameon=True, framealpha=0.9, edgecolor="#CCCCCC",
              loc="lower right")
ax_acc.set_title("A   Classification Accuracy", fontsize=10, fontweight="bold",
                 color=COLORS["text"], loc="left", pad=8)

# Shaded LR phases
phase_colors = ["#E8F4FD", "#EBF5FB", "#E9F7EF", "#FEF9E7"]
phase_bounds = [(1, 30), (30, 60), (60, 80), (80, 100)]
for (x0, x1), pc in zip(phase_bounds, phase_colors):
    ax_acc.axvspan(x0, x1, color=pc, alpha=0.35, zorder=0)

# ─────────────────────────────────────────────────────────────────────────────
#  Panel B – LR Schedule
# ─────────────────────────────────────────────────────────────────────────────
ax_lr.step(epochs, lr_schedule * 1e3, where="post",
           color=COLORS["train"], lw=2, zorder=4)
ax_lr.fill_between(epochs, lr_schedule * 1e3, step="post",
                   alpha=0.15, color=COLORS["train"])

for ep, label in [(30, "Phase 2"), (60, "Phase 3"), (80, "Phase 4")]:
    ax_lr.axvline(ep, color="#AAAAAA", lw=0.8, ls=":")
    ax_lr.text(ep + 1, 0.85, label, fontsize=6, color=COLORS["subtext"], rotation=90, va="top")

ax_lr.set_xlim(1, 100); ax_lr.set_ylim(-0.05, 1.15)
ax_lr.set_xlabel("Epoch", fontsize=9, color=COLORS["text"])
ax_lr.set_ylabel("LR (×10⁻³)", fontsize=9, color=COLORS["text"], labelpad=4)
ax_lr.set_title("B   LR Schedule", fontsize=10, fontweight="bold",
                color=COLORS["text"], loc="left", pad=8)
ax_lr.yaxis.set_minor_locator(MultipleLocator(0.1))

# ─────────────────────────────────────────────────────────────────────────────
#  Panel C – Loss
# ─────────────────────────────────────────────────────────────────────────────
ax_loss.fill_between(epochs, train_loss, val_loss, alpha=0.07, color=COLORS["val"])
ax_loss.plot(epochs, train_loss, color=COLORS["train"], lw=2.2,
             label="Training loss", zorder=4)
ax_loss.plot(epochs, val_loss,   color=COLORS["val"],   lw=2.2,
             label="Validation loss", zorder=4)

# Inflection annotation
infl = 18
ax_loss.annotate(
    "Rapid\ndescent",
    xy=(infl, train_loss[infl]),
    xytext=(infl + 12, train_loss[infl] + 0.3),
    fontsize=7.5, color=COLORS["text"],
    arrowprops=dict(arrowstyle="-|>", color=COLORS["train"],
                    lw=1.2, connectionstyle="arc3,rad=0.25"),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS["train"],
              lw=1, alpha=0.92),
)

ax_loss.set_xlim(1, 100); ax_loss.set_ylim(0, 2.1)
ax_loss.set_ylabel("Cross-Entropy Loss", fontsize=9, color=COLORS["text"], labelpad=6)
ax_loss.set_xlabel("Epoch", fontsize=9, color=COLORS["text"])
ax_loss.legend(fontsize=7.5, frameon=True, framealpha=0.9, edgecolor="#CCCCCC",
               loc="upper right")
ax_loss.set_title("C   Training & Validation Loss", fontsize=10, fontweight="bold",
                  color=COLORS["text"], loc="left", pad=8)

# ─────────────────────────────────────────────────────────────────────────────
#  Panel D – Generalisation Gap
# ─────────────────────────────────────────────────────────────────────────────
gap = val_loss - train_loss
ax_delta.plot(epochs, gap, color=COLORS["val"], lw=2, zorder=4)
ax_delta.fill_between(epochs, 0, gap, alpha=0.15, color=COLORS["val"])
ax_delta.axhline(0, color="#AAAAAA", lw=0.8)

peak_ep = int(np.argmax(gap)) + 1
ax_delta.scatter([peak_ep], [gap[peak_ep-1]], s=70, color=COLORS["accent"],
                 zorder=6, edgecolors="white", linewidths=1.2)
ax_delta.annotate(
    f"Peak gap\n@ ep. {peak_ep}",
    xy=(peak_ep, gap[peak_ep-1]),
    xytext=(peak_ep + 8, gap[peak_ep-1] + 0.01),
    fontsize=7, color=COLORS["text"],
    arrowprops=dict(arrowstyle="-|>", color=COLORS["accent"], lw=1.1),
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=COLORS["accent"],
              lw=1, alpha=0.92),
)

ax_delta.set_xlim(1, 100)
ax_delta.set_xlabel("Epoch", fontsize=9, color=COLORS["text"])
ax_delta.set_ylabel("Val. Loss − Train. Loss", fontsize=8.5, color=COLORS["text"], labelpad=4)
ax_delta.set_title("D   Generalisation Gap", fontsize=10, fontweight="bold",
                   color=COLORS["text"], loc="left", pad=8)
ax_delta.yaxis.set_minor_locator(MultipleLocator(0.01))

# ─────────────────────────────────────────────────────────────────────────────
#  Figure-level title & caption
# ─────────────────────────────────────────────────────────────────────────────
fig.suptitle(
    "Training Dynamics of a ResNet-50 on CIFAR-100\n"
    "with Staged Learning-Rate Decay",
    fontsize=13, fontweight="bold", color=COLORS["text"],
    y=0.96, x=0.52,
)

caption = (
    "Figure 1. Four-panel overview of training dynamics. "
    "(A) Classification accuracy for training and validation sets "
    "versus the SoTA baseline (dashed). "
    "(B) Staged learning-rate schedule divided into four phases. "
    "(C) Cross-entropy loss curves; the shaded region highlights the generalisation gap. "
    "(D) Instantaneous generalisation gap (Δ = validation − training loss)."
)
fig.text(0.5, 0.02, caption, ha="center", va="bottom",
         fontsize=7.2, color=COLORS["subtext"],
         wrap=True, style="italic",
         transform=fig.transFigure)
