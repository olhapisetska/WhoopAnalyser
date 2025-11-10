import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 1️⃣ Load data
# ==========================================
CSV_FILE = "workouts_analysis.csv"

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"❌ {CSV_FILE} not found. Please run statistics.py first.")

print("🌂 Loaded data from workouts_analysis.csv")

df = pd.read_csv(CSV_FILE)
df["start"] = pd.to_datetime(df["start"], errors="coerce")
df["weekday"] = df["start"].dt.day_name()

# ==========================================
# 2️⃣ Choose metric to visualize
# ==========================================
# Change this to "energy_kcal" or "duration" if you prefer
if "strain" in df.columns:
    metric = "strain"
elif "score_strain" in df.columns:
    metric = "score_strain"
else:
    raise KeyError("No strain column found in dataset!")

metric_name = "Average Strain"

# ==========================================
# 3️⃣ Aggregate by weekday
# ==========================================
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
data = df.groupby("weekday")[metric].mean().reindex(weekday_order)

# ==========================================
# 4️⃣ Create Umbrella (Polar) Graph
# ==========================================
angles = np.linspace(0, 2 * np.pi, len(data), endpoint=False).tolist()
values = data.values.tolist()
values += values[:1]   # close the circle
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, color="teal", alpha=0.8)
ax.fill(angles, values, color="teal", alpha=0.3)

# Set labels and style
ax.set_xticks(angles[:-1])
ax.set_xticklabels(data.index, fontsize=11)
ax.set_yticklabels([])
ax.set_title(f"🌂 {metric_name} by Weekday", va="bottom", fontsize=16, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("umbrella_graph_weekday.png", dpi=300)
plt.close()

print("📈 Saved umbrella_graph_weekday.png successfully!")
