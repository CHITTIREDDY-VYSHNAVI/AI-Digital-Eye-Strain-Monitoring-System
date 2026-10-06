import csv
import time
from pathlib import Path


def save_log(blinks, distance, ear, status, filename="eye_strain_report.csv"):
    file_path = Path(__file__).resolve().parent / filename
    file_exists = file_path.exists()

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Time", "Blink Count", "Distance(cm)", "EAR", "Status"])

        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            blinks,
            round(distance, 2),
            round(ear, 2),
            status,
        ])