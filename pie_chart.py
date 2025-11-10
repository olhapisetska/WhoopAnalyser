import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# 1️⃣ Load the data
# ==========================================
CSV_FILE = "workouts_analysis.csv"

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"❌ {CSV_FILE} not found. Please run statistics.py first.")

print("🥧 Loaded data from workouts_analysis.csv")

df = pd.read_csv(CSV_FILE)

# ==========================================
# 2️⃣ Choose metric for the pie chart
# ==========================================
# Options: "energy_kcal", "strain", "score_strain"
if "energy_kcal" in df.columns:
    metric = "energy_kcal"
    metric_name = "Total Energy (kcal)"
elif "score_strain" in df.columns:
    metric = "score_strain"
    metric_name = "Total Strain"
else:
    metric = "strain"
    metric_name = "Total Strain"

# ==========================================
# 3️⃣ Aggregate by sport
# ==========================================
if "sport_name" not in df.columns:
    raise KeyError("No 'sport_name' column found in dataset!")

sport_data = df.groupby("sport_name")[metric].sum().sort_values(ascending=False)

# ==========================================
# 4️⃣ Create Pie Chart
# ==========================================
fig, ax = plt.subplots(figsize=(8, 8))

colors = plt.cm.Paired(range(len(sport_data)))

wedges, texts, autotexts = ax.pie(
    sport_data,
    labels=sport_data.index,
    autopct=lambda p: f"{p:.1f}%",
    startangle=90,
    colors=colors,
    textprops={'fontsize': 10}
)

ax.set_title(f"🥧 {metric_name} by Sport", fontsize=16, fontweight="bold", pad=20)
ax.axis("equal")  # Equal aspect ratio ensures the pie is circular

plt.tight_layout()
plt.savefig("pie_chart_sports.png", dpi=300)
plt.close()

print("📈 Saved pie_chart_sports.png successfully!")
