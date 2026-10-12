import csv
import requests

API_URL = "https://kaiyunh2.pythonanywhere.com/api/chart/activity-categories/"

response = requests.get(API_URL)
response.raise_for_status()

data = response.json()

output_file = "api_use_cases/activity_categories.csv"

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=["category", "count"]
    )

    writer.writeheader()
    writer.writerows(data)

print("Public API:", API_URL)
print("API data:", data)
print("CSV file created:", output_file)