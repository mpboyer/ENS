import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import scipy.stats as stats
import numpy as np
# from adjustText import adjust_text

rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
rc("text", usetex=True)

data = pd.read_csv("benchmarks/csv/fastmarching_benchmark_12:08_14:07:15.csv")

plot = sns.relplot(
    height=3,
    aspect=1.5,
    data=data,
    x="vertices",
    y="time",
    hue="model",
    kind="line",
    marker="o",
)

plt.xlabel("Number of Vertices")
plt.ylabel("Time")
plt.xscale("log")
plt.yscale("log")

x = np.log10(data["vertices"])
y = np.log10(data["time"])
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
x_fit = np.linspace(x.min(), x.max(), 100)
y_fit = slope * x_fit + intercept
plot.ax.plot(10**x_fit, 10**y_fit, color="tab:blue", label="Linear fit (log-log)")
print(f"Slope: {slope}, Intercept: {intercept}, R-squared: {r_value**2}")

data["source"] = data["source"].astype(str)
data["model"] = data["model"].astype(str)

# Annotate each (source, model) group at the average (vertices, time) position
texts = []
for model, group in data.groupby(["model"]):
    avg_vertices = group["vertices"].mean()
    avg_time = group["time"].mean()
    # Offset label to the right by 5% of the average x value
    # plot.ax.text(avg_vertices * 1.3, avg_time, str(model[0][:-4]), fontsize=7, ha='left', va='center') # right
    # plot.ax.text(avg_vertices * 1.1, avg_time / 1.5, str(model[0][:-4]), fontsize=7, ha='left', va='center', rotation=-30) # rotated
    # texts.append(plot.ax.text(avg_vertices, avg_time, str(model[0][:-4]), fontsize=10, ha='center', va='center')) # adjust_text

    # if higher than the fit line, put label above and to the right
    if avg_time > 10 ** (slope * np.log10(avg_vertices) + intercept):
        plot.ax.text(
            avg_vertices / 1.1,
            avg_time,
            str(model[0][:-4]),
            fontsize=7,
            ha="right",
            va="center",
        )
    else:
        plot.ax.text(
            avg_vertices * 1.1,
            avg_time,
            str(model[0][:-4]),
            fontsize=7,
            ha="left",
            va="center",
        )

# adjust_text(texts, ax=plot.ax, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))
plot.figure.tight_layout()
plot.legend.remove()
plot.savefig("benchmarks/pdf/fastmarching_benchmark.pdf", bbox_inches="tight")

print("Number of models tested:", data["model"].nunique())
print("Minimum number of vertices:", data["vertices"].min())
print("Maximum number of vertices:", data["vertices"].max())
