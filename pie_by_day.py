import pandas as pd
import matplotlib.pyplot as plt

# Load your existing workouts dataset
df = pd.read_csv("workouts_analysis.csv")

# Ensure 'start' column is datetime
df["start"] = pd.to_datetime(df["start"], errors="coerce")

# Extract day of week (Monday, Tuesday, etc.)
df["day_of_week"] = df["start"].dt.day_name()

# Count workouts per day
workouts_per_day = df["day_of_week"].value_counts().sort_index()

# Identify the top training day
top_day = workouts_per_day.idxmax()

# Prepare labels with counts and percentages
total_workouts = workouts_per_day.sum()
labels = [
    f"{day}\n({count} workouts, {count / total_workouts:.1%})"
    for day, count in workouts_per_day.items()
]

# Define colors (highlight top day)
colors = [
    "gold" if day == top_day else "lightblue" for day in workouts_per_day.index
]

# Create the pie chart
plt.figure(figsize=(8, 8))
wedges, texts = plt.pie(
    workouts_per_day,
    labels=labels,
    colors=colors,
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
)

# Add a central title
plt.title("🏋️‍♀️ Workouts by Day of Week\n(Highlighting Top Training Day)", fontsize=14, weight="bold")

# Add a legend showing which day is the most frequent
plt.legend(
    [f"🌟 Top Training Day: {top_day} ({workouts_per_day[top_day]} workouts)"],
    loc="lower center",
    bbox_to_anchor=(0.5, -0.1),
    fontsize=11,
    frameon=False,
)

# Save and show
plt.tight_layout()
plt.savefig("workouts_by_day_pie.png", dpi=300)
plt.show()

print(f"📈 Saved workouts_by_day_pie.png — Top day: {top_day}")
