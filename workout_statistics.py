import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- CONFIG ---------------- #
INPUT_JSON = "workouts.json"
OUTPUT_CSV = "workouts_analysis.csv"
OUTPUT_SUMMARY_JSON = "workout_analysis_summary.json"
OUTPUT_SUMMARY_XLSX = "workout_analysis_summary.xlsx"

# ---------------- LOAD DATA ---------------- #
with open(INPUT_JSON, "r") as f:
    workouts = json.load(f)

if not workouts:
    print("❌ No workouts found in JSON file.")
    exit()

# Convert to DataFrame
df = pd.DataFrame(workouts)

# Normalize nested 'score' field
score_df = pd.json_normalize(df["score"])
df = pd.concat([df.drop(columns=["score"]), score_df.add_prefix("score_")], axis=1)

# Convert timestamps
df["start"] = pd.to_datetime(df["start"])
df["end"] = pd.to_datetime(df["end"])
df["duration_hr"] = (df["end"] - df["start"]).dt.total_seconds() / 3600

# ---------------- ENERGY FIELD HANDLING ---------------- #
# Handle energy field variations (kilojoule / energy / kcal)
energy_col = None
for possible_col in ["score_energy", "score_kilojoule", "score_kj"]:
    if possible_col in df.columns:
        energy_col = possible_col
        break

if energy_col is None:
    print("⚠️ No energy column found (expected 'kilojoule' or 'energy'). Using 0 kcal.")
    df["energy_kcal"] = 0
else:
    df["energy_kcal"] = df[energy_col] / 4.184  # Convert from kJ → kcal

# ---------------- WEEK COLUMN ---------------- #
df["week"] = df["start"].dt.to_period("W").apply(lambda r: r.start_time.date())

# ---------------- SUMMARY STATS ---------------- #
summary_stats = {
    "total_workouts": len(df),
    "avg_strain": round(df["score_strain"].mean(), 2),
    "avg_hr": round(df["score_average_heart_rate"].mean(), 2),
    "max_hr_overall": int(df["score_max_heart_rate"].max()),
    "total_kcal": round(df["energy_kcal"].sum(), 2),
}

print("\n📊 SUMMARY STATS")
for k, v in summary_stats.items():
    print(f"{k:20}: {v:.2f}" if isinstance(v, float) else f"{k:20}: {v}")

# ---------------- WEEKLY AGGREGATES ---------------- #
weekly = df.groupby("week").agg(
    avg_strain=("score_strain", "mean"),
    total_calories=("energy_kcal", "sum")
).reset_index()

# ---------------- TRAINING FREQUENCY BY SPORT ---------------- #
sport_freq = df["sport_name"].value_counts().sort_values(ascending=False)

# ---------------- HR ZONE DISTRIBUTION ---------------- #
zone_cols = [c for c in df.columns if "zone_durations" in c]
hr_zone_means = df[zone_cols].mean()

# ---------------- SAVE CSV ---------------- #
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n💾 Saved detailed data to {OUTPUT_CSV}")

# ---------------- PLOTS ---------------- #

# 1️⃣ Training Frequency by Sport
plt.figure(figsize=(10, 5))
sport_freq.plot(kind="bar")
plt.title("Training Frequency by Sport")
plt.xlabel("Sport")
plt.ylabel("Sessions")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("training_frequency_by_sport.png")
plt.close()
print("📈 Saved training_frequency_by_sport.png")

# 2️⃣ Average Strain per Week
plt.figure(figsize=(10, 5))
plt.plot(weekly["week"], weekly["avg_strain"], marker="o")
plt.title("Average Strain per Week")
plt.xlabel("Week")
plt.ylabel("Average Strain")
plt.grid(True, linestyle="--", alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("average_strain_per_week.png")
plt.close()
print("📈 Saved average_strain_per_week.png")

# 3️⃣ Total Calories per Week (kcal)
plt.figure(figsize=(10, 5))
plt.bar(weekly["week"].astype(str), weekly["total_calories"])
plt.title("Total Calories Burned per Week")
plt.xlabel("Week")
plt.ylabel("Total kcal")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("total_calories_per_week.png")
plt.close()
print("📈 Saved total_calories_per_week.png")

# 4️⃣ HR Zone Distribution
if not hr_zone_means.empty:
    plt.figure(figsize=(8, 5))
    hr_zone_means.plot(kind="bar")
    plt.title("Average HR Zone Duration per Workout")
    plt.xlabel("HR Zone")
    plt.ylabel("Average Duration (ms)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("hr_zone_distribution.png")
    plt.close()
    print("📈 Saved hr_zone_distribution.png")

# ---------------- SUMMARY EXPORTS ---------------- #

summary = {
    "summary_stats": {k: float(v) if isinstance(v, (int, float)) else v for k, v in summary_stats.items()},
    "workouts_by_sport": {str(k): int(v) for k, v in sport_freq.to_dict().items()},
}

# Safe JSON serialization
def default_converter(o):
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    if hasattr(o, "item"):
        return o.item()
    return str(o)

with open(OUTPUT_SUMMARY_JSON, "w") as f:
    json.dump(summary, f, indent=4, default=default_converter)

print(f"💾 Saved summary JSON to {OUTPUT_SUMMARY_JSON}")

# Save Excel
with pd.ExcelWriter(OUTPUT_SUMMARY_XLSX) as writer:
    pd.DataFrame([summary_stats]).to_excel(writer, sheet_name="Summary Stats", index=False)
    sport_freq.reset_index().rename(columns={"index": "sport", "sport_name": "sessions"}).to_excel(writer, sheet_name="By Sport", index=False)
    weekly.to_excel(writer, sheet_name="Weekly Trends", index=False)
print(f"💾 Saved Excel summary to {OUTPUT_SUMMARY_XLSX}")

print("\n✅ All analysis completed successfully!")
