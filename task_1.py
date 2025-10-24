import pandas as pd
from datetime import datetime
import glob
import os
from math import radians, sin, cos, sqrt, atan2

# --- Helper: Haversine formula ---
# Requirement 6: Calculate the distance between two points (in km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

# --- Helper: Convert GPS coordinate from ddmm.mmmm format to decimal degrees (WGS84) ---
def convert_coord(coord):
    coord_str = str(coord).zfill(8)
    deg = int(coord_str[:2])         # first 2 digits = degrees
    minutes = float(coord_str[2:]) / 10000
    return deg + (minutes / 60)      # decimal degrees

def process_all_gsd(input_folder="data", output_file="AllTrips_Task1_Output.xlsx"):
    files = glob.glob(os.path.join(input_folder, "*.gsd"))
    all_records = []     # Will hold point-level data
    summary_records = [] # Will hold trip-level summary

    for file in files:
        user_id = os.path.splitext(os.path.basename(file))[0]  # Use filename as USER_ID (e.g. Bullis1)
        trail_id = 0
        prev_lat, prev_lon, prev_dt, prev_speed = None, None, None, None

        with open(file) as f:
            for line in f:
                if "=" not in line:
                    continue
                parts = line.strip().split("=")[1].split(",")
                if len(parts) < 6:
                    continue

                # Requirement 3: Create Trip ID (TP_ID) and Point ID (TRAIL_ID)
                trail_id += 1

                raw_lat, raw_lon, time_str, date_str, speed_raw, height = parts

                # Requirement 5: Convert raw date/time into proper formats
                try:
                    dt = datetime.strptime(date_str + time_str, "%d%m%y%H%M%S")
                except Exception:
                    continue
                time_fmt = dt.strftime("%H:%M:%S")
                date_fmt = dt.strftime("%d-%m-%y")

                # Requirement 4: Calculate speed in km/h
                speed_raw = int(speed_raw)       # raw value (centi-km/h)
                speed_kmh = speed_raw / 100      # convert to km/h
                height = int(height)

                # Convert coordinates to decimal degrees (WGS84)
                y_wgs84 = convert_coord(raw_lat)
                x_wgs84 = convert_coord(raw_lon)

                # Requirement 6: Distance between consecutive points
                distance_km = 0
                # Requirement 7: Time difference between points
                time_diff_s = 0
                # Requirement 9: Acceleration at each point
                acceleration = 0
                if prev_lat is not None:
                    distance_km = haversine(prev_lat, prev_lon, y_wgs84, x_wgs84)
                    time_diff_s = (dt - prev_dt).total_seconds()
                    v_diff = speed_kmh - prev_speed
                    if time_diff_s > 0:
                        acceleration = v_diff / (time_diff_s / 3600)  # km/h²

                # Collect point-level record
                all_records.append([
                    1, trail_id, user_id,   # Trip ID fixed as 1, Point ID increases, User ID = filename
                    raw_lat, raw_lon,
                    time_fmt, date_fmt,
                    speed_raw, height,
                    speed_kmh, y_wgs84, x_wgs84,
                    distance_km, time_diff_s, acceleration
                ])

                # Update "previous point" values
                prev_lat, prev_lon, prev_dt, prev_speed = y_wgs84, x_wgs84, dt, speed_kmh

        # Requirement 8, 10, 11: Trip-level calculations (per file)
        df_user = pd.DataFrame([r for r in all_records if r[2] == user_id],
                               columns=[
                                   "TP_ID","TRAIL_ID","USER_ID","Y_COORDINA","X_COORDINA",
                                   "TIME","DATE","SPEED","HEIGHT","SPEED(KM/H)","Y_WGS84","X_WGS84",
                                   "DISTANCE_KM","TIME_DIFF_S","ACCELERATION"
                               ])
        total_distance = df_user["DISTANCE_KM"].sum()                # Requirement 11: Trip distance
        total_duration_h = df_user["TIME_DIFF_S"].sum() / 3600       # Requirement 11: Trip duration (hours)
        avg_speed_trip = total_distance / total_duration_h if total_duration_h > 0 else 0  # Requirement 8: Avg speed
        avg_acceleration = df_user["ACCELERATION"].mean()            # Requirement 10: Avg acceleration

        summary_records.append([
            user_id, len(df_user), total_distance,
            total_duration_h, avg_speed_trip, avg_acceleration
        ])

    # --- Create DataFrames ---
    # Sheet 1: Point-level data (includes requirements 3,4,5,6,7,9)
    columns_all = [
        "TP_ID","TRAIL_ID","USER_ID","Y_COORDINA","X_COORDINA",
        "TIME","DATE","SPEED","HEIGHT","SPEED(KM/H)","Y_WGS84","X_WGS84",
        "DISTANCE_KM","TIME_DIFF_S","ACCELERATION"
    ]
    df_out = pd.DataFrame(all_records, columns=columns_all)

    # Sheet 2: Trip summary (includes requirements 8,10,11)
    columns_summary = ["USER_ID","Points","Total_Distance_KM","Total_Duration_Hours","Avg_Speed_KMH","Avg_Acceleration"]
    df_summary = pd.DataFrame(summary_records, columns=columns_summary)

    # --- Save both sheets to Excel ---
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_out.to_excel(writer, sheet_name="PointLevelData", index=False)
        df_summary.to_excel(writer, sheet_name="TripSummary", index=False)

    print(f"✅ All trips saved into {output_file}")

# Run the script
if __name__ == "__main__":
    process_all_gsd("data", "AllTrips_Task1_Output.xlsx")
