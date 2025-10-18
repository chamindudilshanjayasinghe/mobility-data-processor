import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

# Load processed data from Task 1 Excel
df = pd.read_excel("AllTrips_Task1_Output.xlsx", sheet_name="PointLevelData")

# --- Plot 1: GPS Path (Longitude vs Latitude) ---
plt.figure(figsize=(8,6))
for user_id, group in df.groupby("USER_ID"):
    plt.plot(group["X_WGS84"], group["Y_WGS84"], marker='o', markersize=2, label=user_id)

plt.title("GPS Path (Longitude vs Latitude)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(True)
plt.savefig("gps_path_plot.png")   # save to file
plt.close()

# --- Plot 2: GPS Heatmap (Density of GPS Points) ---
plt.figure(figsize=(8,6))
sns.kdeplot(
    x=df["X_WGS84"], y=df["Y_WGS84"],
    cmap="Reds", fill=True, thresh=0, levels=100
)

plt.title("GPS Point Density Heatmap")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig("gps_heatmap.png")   # save to file
plt.close()

print("✅ Plots saved as gps_path_plot.png and gps_heatmap.png")
