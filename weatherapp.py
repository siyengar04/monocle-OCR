import asyncio
import datetime
import requests
from brilliant import Monocle

async def fetch_weather():
    try:
        # Step 1: Get the forecast URL
        points_url = "https://api.weather.gov/points/39.7456,-97.0892"
        response = requests.get(points_url)
        response.raise_for_status()
        forecast_url = response.json()['properties']['forecast']

        # Step 2: Fetch the weather forecast
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        current_weather = forecast_data['properties']['periods'][0]

        description = current_weather['shortForecast']
        temperature = current_weather['temperature']
        temperature_unit = current_weather['temperatureUnit']

        return f"{description}, {temperature} {temperature_unit}"

    except requests.RequestException as e:
        print(f"Failed to fetch weather data: {e}")
        return "Failed to connect to weather service"

def generate_display_script(weather, current_time):
    return f'''
import display

def update_display():
    text = display.Text("Weather: {weather}", 100, 0, display.WHITE, justify=display.TOP_LEFT)
    text2 = display.Text("Time: {current_time}", 100, 100, display.BLUE, justify=display.TOP_LEFT)
    display.show(text, text2)
    

update_display()
'''

async def main():
    async with Monocle() as monocle:
        weather = await fetch_weather()
        current_time = datetime.datetime.now().strftime("%H:%M")
        remote_script = generate_display_script(weather, current_time)
        await monocle.send_command(remote_script)
        print("Monocle is now displaying weather information and time.")

asyncio.run(main())
