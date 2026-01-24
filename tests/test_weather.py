import unittest
import asyncio
from unittest.mock import patch
from radio.weather import Weather

class TestWeather(unittest.TestCase):
    @patch('radio.weather.requests.get')
    def test_get_weather_mock(self, mock_get):
        mock_response = {
            "properties": {
                "temperature": {"value": 20},
                "windSpeed": {"value": 10},
                "windDirection": {"value": 90}
            }
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        weather = Weather()
        result = asyncio.run(weather.get_weather("test_station"))

        self.assertIn("68 degrees Fahrenheit", result)
        self.assertIn("10 miles per hour", result)
        self.assertIn("east", result)

if __name__ == "__main__":
    unittest.main()
