import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import numpy as np

rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
rc("text", usetex=True)

# Read the data
data = pd.read_csv("benchmarks/csv/accuracy_spectral_methods.csv")

# Define "big enough" vertex count threshold
MIN_VERTICES = data["vertices"].quantile(0.25)  # Use 25th percentile as threshold
print(f"Minimum vertex count threshold: {MIN_VERTICES}")

# Filter data for models with sufficient vertices
filtered_data = data[data["vertices"] >= MIN_VERTICES].copy()

print(f"Models before filtering: {data['model'].nunique()}")
print(f"Models after filtering: {filtered_data['model'].nunique()}")
print(f"Data points before filtering: {len(data)}")
print(f"Data points after filtering: {len(filtered_data)}")

# Group by method and relative embedding size, then average
grouped_data = (
    filtered_data.groupby(["method", "relative embedding size"])
    .agg({
        "relative error": "mean",
        "model": "count"  # Count number of models averaged
    })
    .reset_index()
)
grouped_data.columns = ["method", "relative embedding size", "relative error", "n_models"]

# Create the plot
fig, ax = plt.subplots(figsize=(6, 3.3))

# Color palette for methods
methods = grouped_data["method"].unique()
colors = sns.color_palette("husl", len(methods))

# Plot each method
for i, method in enumerate(methods):
    method_data = grouped_data[grouped_data["method"] == method].sort_values("relative embedding size")
    
    # Plot the average curve with markers
    ax.scatter(
        method_data["relative embedding size"],
        method_data["relative error"],
        marker="o",
        s=10,
        label=method,
        color=colors[i],
        alpha=0.8
    )

ax.set_xlabel("Relative Size of the Eigenvalue Embedding", fontsize=12)
ax.set_ylabel("Relative Error", fontsize=12)
ax.set_xscale("log")
ax.set_yscale("log")
ax.grid(True, alpha=0.3, which="both", linestyle=":")
ax.legend(fontsize=10, loc="best")

plt.tight_layout()
plt.savefig("benchmarks/pdf/accuracy_spectral_methods.pdf", bbox_inches="tight")
plt.show()
