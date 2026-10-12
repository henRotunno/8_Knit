import requests

API_URL = "https://kaiyunh2.pythonanywhere.com/api/chart/activity-categories/"

response = requests.get(API_URL)
response.raise_for_status()

data = response.json()

print("Public API:", API_URL)
print("API data:", data)

total = sum(item["count"] for item in data)

print("\nStatistical Analysis")
print("Total activities:", total)

for item in data:
    percentage = item["count"] / total * 100
    print(
        f'{item["category"]}: '
        f'{item["count"]} activities '
        f'({percentage:.1f}%)'
    )