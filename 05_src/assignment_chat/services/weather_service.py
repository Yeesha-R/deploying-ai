import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: "clear skies",
    1: "mostly clear skies",
    2: "partly cloudy conditions",
    3: "overcast conditions",
    45: "foggy conditions",
    48: "fog with frost",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "heavy drizzle",
    56: "light freezing drizzle",
    57: "heavy freezing drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "light snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    77: "snow grains",
    80: "light rain showers",
    81: "moderate rain showers",
    82: "heavy rain showers",
    85: "light snow showers",
    86: "heavy snow showers",
    95: "a thunderstorm",
    96: "a thunderstorm with light hail",
    99: "a thunderstorm with heavy hail",
}


class WeatherServiceError(Exception):
    """Raised when the weather service cannot complete a request."""


class WeatherService:
    """Retrieves and summarizes weather information from Open-Meteo."""

    def _get_json(
        self,
        base_url: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Send a GET request and parse the JSON response."""
        url = f"{base_url}?{urlencode(parameters)}"

        request = Request(
            url,
            headers={
                "User-Agent": "Atlas-Travel-Assistant/1.0",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            raise WeatherServiceError(
                f"The weather server returned HTTP error {error.code}."
            ) from error

        except URLError as error:
            raise WeatherServiceError(
                "The weather service could not be reached. "
                "Please check your internet connection."
            ) from error

        except TimeoutError as error:
            raise WeatherServiceError(
                "The weather request took too long."
            ) from error

        except json.JSONDecodeError as error:
            raise WeatherServiceError(
                "The weather service returned an invalid response."
            ) from error

    def find_location(self, city: str) -> dict[str, Any]:
        """Find the coordinates and identifying details for a city."""
        cleaned_city = city.strip()

        if not cleaned_city:
            raise WeatherServiceError("Please provide a city name.")

        data = self._get_json(
            GEOCODING_URL,
            {
                "name": cleaned_city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        results = data.get("results", [])

        if not results:
            raise WeatherServiceError(
                f"I could not find a location matching '{cleaned_city}'."
            )

        location = results[0]

        return {
            "name": location["name"],
            "country": location.get("country", ""),
            "region": location.get("admin1", ""),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": location.get("timezone", "auto"),
        }

    def get_current_weather(self, city: str) -> dict[str, Any]:
        """Retrieve current weather for a city."""
        location = self.find_location(city)

        data = self._get_json(
            WEATHER_URL,
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "apparent_temperature,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "auto",
            },
        )

        current = data.get("current")

        if not current:
            raise WeatherServiceError(
                "Current weather information was unavailable."
            )

        return {
            "city": location["name"],
            "country": location["country"],
            "region": location["region"],
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "weather_code": current.get("weather_code"),
            "wind_speed": current.get("wind_speed_10m"),
            "observation_time": current.get("time"),
        }

    def _travel_tip(self, weather: dict[str, Any]) -> str:
        """Generate a simple packing or travel suggestion."""
        weather_code = weather.get("weather_code")
        temperature = weather.get("temperature")
        wind_speed = weather.get("wind_speed") or 0

        tips: list[str] = []

        rainy_codes = {
            51, 53, 55, 56, 57,
            61, 63, 65, 66, 67,
            80, 81, 82, 95, 96, 99,
        }
        snowy_codes = {71, 73, 75, 77, 85, 86}

        if weather_code in rainy_codes:
            tips.append("Bring an umbrella or waterproof jacket")

        if weather_code in snowy_codes:
            tips.append("Wear warm layers and shoes with good traction")

        if temperature is not None:
            if temperature <= 5:
                tips.append("Pack a warm coat")
            elif temperature >= 28:
                tips.append("Carry water and use sun protection")
            elif temperature < 15:
                tips.append("A light jacket may be useful")

        if wind_speed >= 30:
            tips.append("Expect strong winds")

        if not tips:
            tips.append("Conditions look fairly comfortable for sightseeing")

        return ". ".join(tips) + "."

    def format_response(self, weather: dict[str, Any]) -> str:
        """Transform API data into a conversational response."""
        condition = WEATHER_CODES.get(
            weather["weather_code"],
            "unavailable weather conditions",
        )

        location_parts = [weather["city"]]

        if weather.get("region"):
            location_parts.append(weather["region"])

        if weather.get("country"):
            location_parts.append(weather["country"])

        location_name = ", ".join(location_parts)

        return (
            f"Atlas weather update for {location_name}: "
            f"It is currently {weather['temperature']}°C with {condition}. "
            f"It feels like {weather['feels_like']}°C. "
            f"Humidity is {weather['humidity']}%, and winds are approximately "
            f"{weather['wind_speed']} km/h. "
            f"{self._travel_tip(weather)}"
        )

    def weather_report(self, city: str) -> str:
        """Retrieve and format a complete weather report."""
        weather = self.get_current_weather(city)
        return self.format_response(weather)


def main() -> None:
    service = WeatherService()

    print("Atlas Weather Service")
    print("Enter 'quit' to stop.\n")

    while True:
        city = input("Enter a city: ").strip()

        if city.lower() == "quit":
            break

        try:
            print(service.weather_report(city))
        except WeatherServiceError as error:
            print(f"Atlas could not retrieve the weather: {error}")

        print()


if __name__ == "__main__":
    main()