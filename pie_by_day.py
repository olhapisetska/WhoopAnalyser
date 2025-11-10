import pandas as pd
import matplotlib.pyplot as plt

# Load your existing dataset
df = pd.read_csv("workouts_analysis.csv")

# Ensure the 'start' column is datetime
df["start"] = pd.to_datetime(df["start"], errors="coerce")

# Extract the day of week (Monday, Tuesday, etc.)
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

# Define colors (highlight the top day)
colors = ["gold" if day == top_day else "skyblue" for day in workouts_per_day.index]

# Create the pie chart
plt.figure(figsize=(8, 8))
wedges, texts = plt.pie(
    workouts_per_day,
    labels=labels,
    colors=colors,
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
)

# Title and legend
plt.title("🏋️‍♀️ Workouts by Day of Week\n(Highlighting Top Training Day)", fontsize=14, weight="bold")
plt.legend(
    [f"🌟 Top Training Day: {top_day} ({workouts_per_day[top_day]} workouts)"],
    loc="lower center",
    bbox_to_anchor=(0.5, -0.1),
    fontsize=11,
    frameon=False,
)

# Save and close
plt.tight_layout()
plt.savefig("pie_chart_days.png", dpi=300)
plt.close()

print("📈 Saved pie_chart_days.png successfully!")
