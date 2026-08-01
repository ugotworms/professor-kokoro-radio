import requests

class Weather:
    async def get_weather(self, station):
        getUrl = f'https://api.weather.gov/stations/{station}/observations/latest'
        try:
            response = requests.get(getUrl)
            response.raise_for_status()
            weather_data = response.json()
            temperature = weather_data['properties']['temperature']['value']
            # Convert temperature to Fahrenheit and round to the nearest whole number
            temperature = int((temperature * 9/5) + 32)
            wind_speed = weather_data['properties']['windSpeed']['value']
            wind_speed = int(wind_speed)
            wind_direction = weather_data['properties']['windDirection']['value']
            # Convert wind direction angle to a cardinal direction
            if 348.75 <= wind_direction < 11.25:
                wind_direction = "north"
            elif 11.25 <= wind_direction < 33.75:
                wind_direction = "north-northeast"
            elif 33.75 <= wind_direction < 56.25:
                wind_direction = "northeast"
            elif 56.25 <= wind_direction < 78.75:
                wind_direction = "east-northeast"
            elif 78.75 <= wind_direction < 101.25:
                wind_direction = "east"
            elif 101.25 <= wind_direction < 123.75:
                wind_direction = "east-southeast"
            elif 123.75 <= wind_direction < 146.25:
                wind_direction = "southeast"
            elif 146.25 <= wind_direction < 168.75:
                wind_direction = "south-southeast"
            elif 168.75 <= wind_direction < 191.25:
                wind_direction = "south"
            elif 191.25 <= wind_direction < 213.75:
                wind_direction = "south-southwest"
            elif 213.75 <= wind_direction < 236.25:
                wind_direction = "southwest"
            elif 236.25 <= wind_direction < 258.75:
                wind_direction = "west-southwest"
            elif 258.75 <= wind_direction < 281.25:
                wind_direction = "west"
            elif 281.25 <= wind_direction < 303.75:
                wind_direction = "west-northwest"
            elif 303.75 <= wind_direction < 326.25:
                wind_direction = "northwest"
            elif 326.25 <= wind_direction < 348.75:
                wind_direction = "north-northwest"
            else:
                wind_direction = "unknown"

            return f"The current temperature is a {self.describe_temperature(temperature)} {temperature} degrees Fahrenheit. The wind is at {wind_speed} miles per hour from the {wind_direction}."
        except requests.exceptions.RequestException as e:
            print(f"Error getting weather data: {e}")
            return "I'm sorry, I was unable to retrieve the weather data at this time."

    def describe_temperature(self, temp_f):
        if temp_f < 20:
            return "Frigid"
        elif 20 <= temp_f < 40:
            return "Chilly"
        elif 40 <= temp_f < 60:
            return "Brisk"
        elif 60 <= temp_f < 80:
            return "Warm"
        elif 80 <= temp_f < 100:
            return "Hot"
        else:
            return "Scorching"
