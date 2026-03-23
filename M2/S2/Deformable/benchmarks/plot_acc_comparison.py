import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rc
import numpy as np

rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
rc("text", usetex=True)

CSV = "benchmarks/csv/comparison_benchmark_03:21_17:11:30.csv"

data = pd.read_csv(CSV)

MIN_SHORT = {
    "FermatIntegral":   "Fermat",
    "EikonalEquation":  "Eikonal",
    "CellBasedMarching":"Cell",
    "QuadraticCurve":   "Quad",
}
STENCIL_SHORT = {
    "Mesh":        "Mesh",
    "Ell1(0.5)":   r"$\ell_1(0.5)$",
    "Ell1(2)":     r"$\ell_1(2)$",
    "MeshEll1(0.5)": r"M+$\ell_1(0.5)$",
    "MeshEll1(2)":   r"M+$\ell_1(2)$",
}

data["stencil_s"] = data["stencil"].map(STENCIL_SHORT).fillna(data["stencil"])
data["min_s"]     = data["minimization"].map(MIN_SHORT).fillna(data["minimization"])
data["interp_s"]  = data["interpolant"].str[0]   # C or G

data["variant"] = data["stencil_s"] + "/" + data["min_s"] + "/" + data["interp_s"]

slowness_fields = ["constant_1", "constant_2", "linear_x", "radial", "pervertex_random"]
SLOWNESS_LABELS = {
    "constant_1":       r"const(1)",
    "constant_2":       r"const(2)",
    "linear_x":         r"lin-$x$",
    "radial":           r"radial",
    "pervertex_random": r"random",
}

metrics = ["mae_vs_fm", "max_err_vs_fm"]
METRIC_LABELS = {
    "mae_vs_fm":     r"MAE vs FM",
    "max_err_vs_fm": r"Max error vs FM",
}

variants_ordered = sorted(data["variant"].unique())

n_slow = len(slowness_fields)
n_met  = len(metrics)
fig, axes = plt.subplots(
    n_met, n_slow,
    figsize=(3.2 * n_slow, 3.5 * n_met),
    sharey="row",
)

COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]
variant_color = {v: COLORS[i % len(COLORS)] for i, v in enumerate(variants_ordered)}

for row, metric in enumerate(metrics):
    for col, slow in enumerate(slowness_fields):
        ax = axes[row, col]
        sub = data[data["slowness"] == slow]

        boxes, positions, colors = [], [], []
        for i, var in enumerate(variants_ordered):
            vals = sub.loc[sub["variant"] == var, metric].dropna().values
            vals = vals[vals > 0]
            if len(vals):
                boxes.append(vals)
                positions.append(i)
                colors.append(variant_color[var])

        bp = ax.boxplot(
            boxes,
            positions=positions,
            widths=0.6,
            patch_artist=True,
            showfliers=False,
            medianprops=dict(color="black", linewidth=1.2),
            whiskerprops=dict(linewidth=0.8),
            capprops=dict(linewidth=0.8),
        )
        for patch, col_c in zip(bp["boxes"], colors):
            patch.set_facecolor(col_c)
            patch.set_alpha(0.6)

        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mticker.LogFormatterSciNotation())
        ax.grid(True, which="both", axis="y", linestyle=":", linewidth=0.4, alpha=0.5)

        if row == 0:
            ax.set_title(SLOWNESS_LABELS[slow], fontsize=9)
        if col == 0:
            ax.set_ylabel(METRIC_LABELS[metric], fontsize=8)

        if row == n_met - 1:
            ax.set_xticks(range(len(variants_ordered)))
            ax.set_xticklabels(variants_ordered, rotation=90, fontsize=5)
        else:
            ax.set_xticks([])

fig.suptitle(r"\textbf{JetMarching accuracy vs FastMarching reference}", fontsize=11, y=1.01)
fig.tight_layout()
fig.savefig("benchmarks/pdf/plot2_accuracy_comparison.pdf", bbox_inches="tight")
plt.close()

print("Saved: benchmarks/pdf/plot2_accuracy_comparison.pdf")
print("Variants plotted:", len(variants_ordered))
