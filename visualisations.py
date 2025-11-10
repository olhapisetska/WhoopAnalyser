import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ==========================================
# 1️⃣ Load data
# ==========================================
CSV_FILE = "workouts_analysis.csv"

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"❌ {CSV_FILE} not found. Please run statistics.py first.")

print("🎨 Loaded data from workouts_analysis.csv")

df = pd.read_csv(CSV_FILE)
df["start"] = pd.to_datetime(df["start"], errors="coerce")

# ==========================================
# 2️⃣ Heatmap Calendar (like GitHub activity)
# ==========================================
df["date"] = df["start"].dt.date
workouts_per_day = df.groupby("date").size().reset_index(name="count")

# Pivot for calendar heatmap
workouts_per_day["weekday"] = pd.to_datetime(workouts_per_day["date"]).dt.weekday
workouts_per_day["week"] = pd.to_datetime(workouts_per_day["date"]).dt.isocalendar().week

# ✅ Corrected pivot syntax
heatmap_data = workouts_per_day.pivot(index="weekday", columns="week", values="count")

plt.figure(figsize=(14, 4))
sns.heatmap(heatmap_data, cmap="YlGnBu", cbar=False, linewidths=0.3)
plt.title("Workout Frequency by Day (Heatmap Calendar)", fontsize=14)
plt.yticks(
    ticks=np.arange(7) + 0.5,
    labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    rotation=0,
)
plt.xlabel("Week Number")
plt.ylabel("")
plt.tight_layout()
plt.savefig("workout_heatmap_calendar.png", dpi=300)
plt.close()
print("📈 Saved workout_heatmap_calendar.png")

# ==========================================
# 3️⃣ Radar Chart (avg HR zones per sport)
# ==========================================
zone_cols = [c for c in df.columns if "score_zone" in c]

if zone_cols:
    zone_means = df.groupby("sport_name")[zone_cols].mean().reset_index()
    sport_names = zone_means["sport_name"].values
    zones = [z.replace("score_zone_", "Z") for z in zone_cols]

    plt.figure(figsize=(7, 7))
    angles = np.linspace(0, 2 * np.pi, len(zone_cols), endpoint=False).tolist()
    angles += angles[:1]  # close the circle

    for i, sport in enumerate(sport_names):
        values = zone_means.iloc[i, 1:].tolist()
        values += values[:1]
        plt.polar(angles, values, label=sport, linewidth=2)

    plt.xticks(angles[:-1], zones)
    plt.title("Average HR Zone Distribution per Sport", fontsize=14)
    plt.legend(bbox_to_anchor=(1.2, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("radar_chart_hr_zones.png", dpi=300)
    plt.close()
    print("📈 Saved radar_chart_hr_zones.png")
else:
    print("⚠️ No HR zone columns found — skipping radar chart.")

# ==========================================
# 4️⃣ Bubble Chart (strain vs kcal vs duration)
# ==========================================
possible_duration_cols = [
    "duration", "score_duration", "duration_sec", "workout_duration", "score_workout_duration"
]
duration_col = next((c for c in possible_duration_cols if c in df.columns), None)

strain_col = "strain" if "strain" in df.columns else "score_strain"
energy_col = "energy_kcal" if "energy_kcal" in df.columns else None

if not all([strain_col in df.columns, energy_col in df.columns, duration_col]):
    print("⚠️ Missing columns for bubble chart — skipping.")
else:
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce") / 60  # convert seconds → minutes
    plt.figure(figsize=(8, 6))
    plt.scatter(
        df[strain_col],
        df[energy_col],
        s=df[duration_col],
        alpha=0.5,
        c=np.random.rand(len(df)),
    )
    plt.title("Workout Bubble Chart — Strain vs Energy vs Duration", fontsize=14)
    plt.xlabel("Strain")
    plt.ylabel("Energy (kcal)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("bubble_chart_strain_energy_duration.png", dpi=300)
    plt.close()
    print("📈 Saved bubble_chart_strain_energy_duration.png")

print("✅ All visualisations completed successfully!")
