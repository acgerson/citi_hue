import urllib.request
import json
from datetime import datetime
from phue import Bridge
import time
import sys

# define global inputs variables
# room variables
light_bike_map = {"Living room 1": "E 11 St & 1 Ave"
    , "Living room 2": "E 11 St & 1 Ave"
    , "Bedroom color": "E 10 St & Avenue A"
    , "Bedroom nightstand": "E 13 St & Avenue A"
    , "TV Light": "E 114 St & 1 Ave"}

# citibike variables
url = "https://www.citibikenyc.com/stations/json"
response = urllib.request.urlopen(url)
data = json.loads(response.read())
my_stations = ["E 11 St & 1 Ave"  # station 326
    , "E 10 St & Avenue A"
    , "E 13 St & Avenue A"
    , "E 114 St & 1 Ave"]


def citibike_update(my_stations_):
    d_ = {'name': [], 'docks': [], 'bikes': [], 'time': []}
    for station in data["stationBeanList"]:
        if station["stationName"] in my_stations_:
            d_['name'].append(str(station["stationName"]))
            d_['docks'].append(int(station['availableDocks']))
            d_['bikes'].append(int(station['availableBikes']))
            d_['time'].append(datetime.strptime(str(data["executionTime"]), "%Y-%m-%d\
     %I:%M:%S %p"))

    return d_


def get_current_light_status(b_, d_):
    try:
        lights_ = b_.lights
    except BaseException:
        time.sleep(.1)
        extract_station_value(d_)
        exit()
    light_dictionary_ = {'name': [], 'hue': [], 'brightness': [], 'saturation': [], 'on': []}
    list_keys_ = list(light_dictionary_)

    # gets current status of system
    for l in range(len(lights_)):
        # if lights['name'][l] == 'Kitchen 1':
        # value we want to print is controlled by the key of light_d
        for k in range(len(list_keys_)):
            # 1st light, looping through all the attributes
            value = getattr(lights_[l], list_keys_[k])
            # print(lights[l].name, list_keys[k], value)
            light_dictionary_[list_keys_[k]].append(value)

    return light_dictionary_, list_keys_, lights_


def update_lights(lights_, light_bike_map_, d__):
    for n in lights_:
        try:
            station_x = light_bike_map_[n.name]
            for i in range(len(d__['name'])):
                if d__['name'][i] == station_x:
                    # sends the number of bikes, docks, and name of light
                    change_light_color(d['bikes'][i], n.name)  # ~~~~~~this changes color
        except:
            print(n.name, 'this light is off')
        pass  # this will leave out any lights that are unplugged- aka ktichen


def change_light_color(bikes, light_name):
    lights_on_bright(light_name)  # turns on light that you want to use
    if bikes >= 10:
        # print('green')
        b.set_light(light_name, 'hue', 20000)
    if bikes < 10 and bikes > 3:
        # print('blue')
        b.set_light(light_name, 'hue', 46014)
    if bikes <= 3 and bikes >= 1:
        # print('red')
        b.set_light(light_name, 'hue', 64382)
    if bikes == 0:
        # print('purple')
        b.set_light(light_name, 'hue', 50000)

    time.sleep(.1)


def lights_on_bright(light_name):
    b.set_light(light_name, 'on', True)
    b.set_light(light_name, 'bri', 254)
    b.set_light(light_name, 'sat', 254)


def return_light_state(light_dictionary_, list_keys_, light_bike_map_):
    # outer loop... for each light
    list_keys_light_bike_map = light_bike_map_.keys()
    for i in range(len(light_dictionary_['name'])):
        light_name = (light_dictionary_['name'][i])
        # inner loop- for each attribute
        for a in range(len(list_keys_[1:])):
            light_attibute = list_keys_[a + 1]
            light_value = light_dictionary_[light_attibute][i]
            if light_attibute == 'brightness' or light_attibute == 'saturation':
                light_attibute = light_attibute[:3]
            # print(light_name, light_attibute, light_value)
            if light_name in list_keys_light_bike_map:
                b.set_light(light_name, light_attibute, light_value)
            else:
                pass
        time.sleep(.1)
    print('lights to normal')


def extract_station_value(d__):
    station_status_bikes = d__['bikes']
    station_status_name = d__['name']
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for b__ in range(len(station_status_name)):
        print(station_status_name[b__] + ':', ' bikes left-', station_status_bikes[b__]),
        print('')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


#############################################
# always get station information
d = citibike_update(my_stations)

try:
    b = Bridge('192.168.1.2')
    b.connect()


except TimeoutError:
    extract_station_value(d)
    exit()



# get the current light status in a dictionary, the list_keys of dictionary, and map of the lights
light_dictionary, list_keys, lights = get_current_light_status(b, d)

# update the lights based on current bike levels
update_lights(lights, light_bike_map, d)

time.sleep(3)

# return light_states
return_light_state(light_dictionary, list_keys, light_bike_map)

    # should wirte something that checks if lights are still on... but maybe thats just calling it again?


# print station station
extract_station_value(d)

