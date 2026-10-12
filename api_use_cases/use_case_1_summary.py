import requests

API_URL = "https://kaiyunh2.pythonanywhere.com/api/chart/activity-categories/"

response = requests.get(API_URL)
response.raise_for_status()

data = response.json()

print("Public API:", API_URL)
print("API data:", data)

total_activities = sum(item["count"] for item in data)
largest_category = max(data, key=lambda item: item["count"])

print("\nSummary")
print("Total activities:", total_activities)
print(
    "Largest category:",
    largest_category["category"],
    "with",
    largest_category["count"],
    "activities"
)