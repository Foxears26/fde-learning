import requests
r = requests.get("https://httpbin.org/json")

params={"name": "Bruce"}
headers = {"User-Agent": "MyApp/1.0"}
r = requests.get("https://httpbin.org/json", params=params, headers=headers, timeout=5)


r = requests.post("https://httpbin.org/post", json={"name": "Bruce", "score": 90})


for attempt in range(3):
    try:
        r = requests.get("https://httpbin.org/json", timeout=5)
        r.raise_for_status()
        print("Request succeeded.")
        break
    except requests.RequestException as e:
        print(f"Attempt {attempt + 1} failed: {e}")
else:
    print("All attempts failed.")
