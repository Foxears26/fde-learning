import argparse
import requests

WEATHER_DESC = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Light rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}   # Weather code descriptions

def get_coords(city):
    # Send a geocoding request with params={"name": city, "count": 1}.
    # Check .get("results"): return None if there are no results.
    # Otherwise, return (latitude, longitude).
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": city, "count": 1, "language": "zh"}, timeout=10)
    response.raise_for_status()

    results = response.json().get("results")
    if not results:
        return None

    location = results[0]
    return location["latitude"], location["longitude"]

def get_weather(lat, lon):
    # Send a forecast request with latitude, longitude, current, daily, and timezone params.
    # Return the response JSON.
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "America/Toronto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description="A simple weather lookup tool")
    parser.add_argument("city", help="City name, e.g. Toronto")
    args = parser.parse_args()

    coords = get_coords(args.city)
    if coords is None:
        print("City not found: {}".format(args.city))
        return

    weather = get_weather(*coords)
    current = weather["current"]
    current_desc = WEATHER_DESC.get(current["weather_code"], "Unknown")
    print("{} current temperature: {}°C, {}".format(args.city, current["temperature_2m"], current_desc))

    daily = weather["daily"]
    print("Forecast for the next 3 days:")
    for i in range(min(3, len(daily["time"]))):
        description = WEATHER_DESC.get(daily["weather_code"][i], "Unknown")
        print(
            "{}: {}, high {}°C, low {}°C".format(
                daily["time"][i], description,
                daily["temperature_2m_max"][i], daily["temperature_2m_min"][i]
            )
        )

if __name__ == "__main__":
    main()
