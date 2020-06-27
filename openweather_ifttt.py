from datetime import datetime

import click
from pyowm.owm import OWM
import requests

LAST_EVENT_FILENAME = '/tmp/openweather_ifttt_event_data'


def get_last_event():
    try:
        with open(LAST_EVENT_FILENAME, 'rt') as f:
            return f.readlines()[0].strip()
    except FileNotFoundError:
        return None


def write_event(event_name):
    with open(LAST_EVENT_FILENAME, 'wt') as f:
        f.write(event_name)
        f.write('\n%s' % datetime.now().isoformat())


@click.command()
@click.option('--owm_api_key', help='OpenWeatherMap.org API key')
@click.option('--ifttt_api_key', help='IFTTT API key')
@click.option('--temp_threshold', type=float, default=25.0, help='High temperature threshold')
@click.option('--high_temp_event_name', default='high_temp',
              help='The IFTTT event name for when the temperature goes over the threshold')
@click.option('--normal_temp_event_name', default='normal_temp',
              help='The IFTTT event name for when the temperature goes under the threshold')
@click.option('--city', default='Pavia,IT', help='The OpenWeatherMap city name to read temp for')
@click.option('--motherboard_temp', type=float, help='The motherboard temperature (or another secondary temperature)')
@click.option('--motherboard_temp_threshold', default=45.0, type=float, help='the motherboard (or other) temperature threshold')
def main(owm_api_key,
         ifttt_api_key,
         temp_threshold,
         high_temp_event_name,
         normal_temp_event_name,
         city,
         motherboard_temp,
         motherboard_temp_threshold):
    """
    If *either* the outside temperature is over a threshold, *or* some other
    temperature (currently motherboard temp, measured outside this script)
    is over a threshold, consider the temperature "high". Send an event to
    IFTTT so we can take action (like turning on a fan).
    """
    owm = OWM(owm_api_key)
    weather_manager = owm.weather_manager()
    observation = weather_manager.weather_at_place(city)
    temp = observation.weather.temperature('celsius')['temp']
    event_name = normal_temp_event_name
    if temp > temp_threshold or motherboard_temp > motherboard_temp_threshold:
        event_name = high_temp_event_name

    previous_event = get_last_event()

    if previous_event != event_name:
        ifttt_url = 'https://maker.ifttt.com/trigger/{event_name}/with/key/%s' % ifttt_api_key
        ifttt_data = {'value1': temp, 'value2': motherboard_temp}
        requests.post(ifttt_url, data=ifttt_data)
        write_event(event_name)


if __name__ == '__main__':
    main()