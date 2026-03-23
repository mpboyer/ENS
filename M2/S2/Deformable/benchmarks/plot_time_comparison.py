import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import rc
import seaborn as sns
import scipy.stats as stats
import numpy as np

rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
rc("text", usetex=True)

CSV = "benchmarks/csv/comparison_benchmark_03:21_17:11:30.csv"

data = pd.read_csv(CSV)

MIN_SHORT = {
    "FermatIntegral":    "Fermat",
    "EikonalEquation":   "Eikonal",
    "CellBasedMarching": "Cell",
    "QuadraticCurve":    "Quad",
}
STENCIL_SHORT = {
    "Mesh":          "Mesh",
    "Ell1(0.5)":     r"$\ell_1(0.5)$",
    "Ell1(2)":       r"$\ell_1(2)$",
    "MeshEll1(0.5)": r"M+$\ell_1(0.5)$",
    "MeshEll1(2)":   r"M+$\ell_1(2)$",
}

data["stencil_s"] = data["stencil"].map(STENCIL_SHORT).fillna(data["stencil"])
data["min_s"]     = data["minimization"].map(MIN_SHORT).fillna(data["minimization"])
data["interp_s"]  = data["interpolant"].str[0]

data["variant"] = data["stencil_s"] + "/" + data["min_s"] + "/" + data["interp_s"]

agg_v = (
    data.groupby(["variant", "vertices"])["time_s"]
    .median()
    .reset_index()
)

variants_ordered = sorted(data["variant"].unique())
n_var = len(variants_ordered)
cmap  = plt.colormaps["tab20"].resampled(n_var)
colors_v = {v: cmap(i) for i, v in enumerate(variants_ordered)}

fig_a, ax_a = plt.subplots(figsize=(8, 4))
for var in variants_ordered:
    sub = agg_v[agg_v["variant"] == var].sort_values("vertices")
    ax_a.plot(sub["vertices"], sub["time_s"],
              marker="o", markersize=2.5, linewidth=0.8,
              color=colors_v[var], alpha=0.8)
    last = sub.iloc[-1]
    ax_a.text(last["vertices"] * 1.02, last["time_s"], var,
              fontsize=4.5, va="center", color=colors_v[var])

x_all = np.log10(agg_v["vertices"])
y_all = np.log10(agg_v["time_s"])
slope, intercept, r_value, *_ = stats.linregress(x_all, y_all)
x_fit = np.linspace(x_all.min(), x_all.max(), 200)
ax_a.plot(10**x_fit, 10**(slope * x_fit + intercept),
          "k--", linewidth=1.0, alpha=0.5,
          label=rf"Overall fit: slope $={slope:.2f}$, $R^2={r_value**2:.3f}$")

ax_a.set_xscale("log")
ax_a.set_yscale("log")
ax_a.set_xlabel("Number of Vertices")
ax_a.set_ylabel("Time (s)")
ax_a.set_title(r"\textbf{JetMarching timing by variant} (all slowness fields, median)")
ax_a.legend(fontsize=7, loc="upper left")
ax_a.grid(True, which="both", linestyle=":", linewidth=0.4, alpha=0.4)
fig_a.tight_layout()
fig_a.savefig("benchmarks/pdf/plot3a_timing_loglog.pdf", bbox_inches="tight")
plt.close()
print(f"Saved: benchmarks/pdf/plot3a_timing_loglog.pdf  (slope={slope:.3f}, R²={r_value**2:.4f})")

agg_m = (
    data.groupby(["model", "variant"])["time_s"]
    .median()
    .reset_index()
)
pivot = agg_m.pivot(index="variant", columns="model", values="time_s")

pivot_norm = pivot.div(pivot.min(axis=0), axis=1)

fig_b, ax_b = plt.subplots(figsize=(max(8, pivot_norm.shape[1] * 0.35 + 2),
                                     max(5, pivot_norm.shape[0] * 0.3 + 1)))
im = ax_b.imshow(pivot_norm.values, aspect="auto",
                 norm=mcolors.LogNorm(vmin=1, vmax=pivot_norm.values.max()),
                 cmap="YlOrRd")
cbar = fig_b.colorbar(im, ax=ax_b, fraction=0.03, pad=0.02)
cbar.set_label(r"Relative time (1 = fastest)", fontsize=8)
cbar.ax.tick_params(labelsize=7)

ax_b.set_xticks(range(pivot_norm.shape[1]))
ax_b.set_xticklabels(
    [m.replace(".obj", "") for m in pivot_norm.columns],
    rotation=45, ha="right", fontsize=5,
)
ax_b.set_yticks(range(pivot_norm.shape[0]))
ax_b.set_yticklabels(pivot_norm.index, fontsize=5)
ax_b.set_title(r"\textbf{Relative timing heatmap} (log-scale, per model)")
fig_b.tight_layout()
fig_b.savefig("benchmarks/pdf/plot3b_timing_heatmap.pdf", bbox_inches="tight")
plt.close()
print("Saved: benchmarks/pdf/plot3b_timing_heatmap.pdf")

agg_src = (
    data.groupby(["model", "source", "variant"])["time_s"]
    .median()
    .reset_index()
)
agg_src["rel_time"] = agg_src.groupby(["model", "source"])["time_s"].transform(
    lambda x: x / x.min()
)
mean_rel = agg_src.groupby("variant")["rel_time"].mean().reset_index()
mean_rel = mean_rel.sort_values("rel_time")

# Stencil group for colour
mean_rel["stencil_g"] = mean_rel["variant"].str.split("/").str[0]
stencil_groups = mean_rel["stencil_g"].unique()
sg_colors = {sg: plt.colormaps["Set2"](i) for i, sg in enumerate(stencil_groups)}
bar_colors = [sg_colors[sg] for sg in mean_rel["stencil_g"]]

fig_c, ax_c = plt.subplots(figsize=(max(8, len(mean_rel) * 0.35 + 1.5), 4))
bars = ax_c.bar(range(len(mean_rel)), mean_rel["rel_time"], color=bar_colors, edgecolor="white",
                linewidth=0.5)
ax_c.axhline(1, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
ax_c.set_xticks(range(len(mean_rel)))
ax_c.set_xticklabels(mean_rel["variant"], rotation=90, fontsize=5)
ax_c.set_ylabel(r"Mean relative time ($\times$ fastest)")
ax_c.set_title(r"\textbf{Average timing slowdown per JetMarching variant}")
ax_c.grid(True, axis="y", linestyle=":", linewidth=0.4, alpha=0.5)

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in sg_colors.values()]
ax_c.legend(handles, sg_colors.keys(), title="Stencil", fontsize=7, title_fontsize=7)

fig_c.tight_layout()
fig_c.savefig("benchmarks/pdf/plot3c_timing_barplot.pdf", bbox_inches="tight")
plt.close()
print("Saved: benchmarks/pdf/plot3c_timing_barplot.pdf")

print(f"\nVariants ranked by mean relative time:")
for _, row in mean_rel.iterrows():
    print(f"  {row['variant']:45s}  {row['rel_time']:.3f}×")
