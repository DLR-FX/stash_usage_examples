import os
import json
import numpy as np

from terra_safe.safety_handling import get_sink_rate

def setup_sensor_dict(list_of_sensors):
    """
    Creates a empty subdictionary for each sensor that is in the list of sensors and returns the dictionary with all sensors
    and there subdictionaries.

    :param list_of_sensors: list of all sensors that should be used for the program


    :return: sensor_dictionary containing all sensors and there dictionaries which are empty
    """

    sensor_dict = {}
    for sensor in list_of_sensors:
        sensor_dict.update({sensor : {}})
    return sensor_dict

def correct_position_values(normal_value, fine_value):
    """
    Adds the Latitude/Longitude and the LatitudeFine/LongitudeFine Values for all values in the Array to get more precise
    Latitude and Longitude Values

    :param normal_value: Array of Latitude/Longitude Values
    :param fine_value: Array of LatitudeFine/LongitudeFine Values

    :return: Array of a more precise Array for Latitude/Longitude
    """
    normal_array = np.array(normal_value)
    fine_array = np.array(fine_value)
    corrected_vector = normal_array + fine_array
    return corrected_vector


def corrected_value_to_dict(name, reference_time, data):
    """
    Creates a Dictionary for the corrected Sensor with name as Key and the Sub-Elements reference_time and data

    :param name: String with the Name of the corrected Sensor
    :param reference_time: Array of time values
    :param data: Array of the data of the corrected Sensor

    :return: dictionary with one Element that contains the new corrected Sensor
    """
    sensor_dict_content = {name: {"time": reference_time, "data": data}}
    return sensor_dict_content




def transform_data(sensor_dict):
    """
    Fills a dictionary with the data and time for the sensors containt in the sensors_dict and also append the corrected
    Values for Latitude and Longitude to the dictionary

    :param sensor_dict: dictionary with the sensor names of the sensor where the data should be stored

    :return: dictionary with the sensor names and there time and data values
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor]["time"], sensor_dict[sensor]["data"] = read_and_downsample(sensor_dict[sensor]["time"],
                                                                                       sensor_dict[sensor]["data"])

    corrected_lat = correct_position_values(sensor_dict["IRH_LAT"]["data"], sensor_dict["IRH_LATFINE"]["data"])
    corrected_long = correct_position_values(sensor_dict["IRH_LONG"]["data"], sensor_dict["IRH_LONGFINE"]["data"])
    sensor_dict.update(corrected_value_to_dict("LAT_CORRECTED", sensor_dict["IRH_LAT"]["time"], corrected_lat))
    sensor_dict.update(corrected_value_to_dict("LONG_CORRECTED", sensor_dict["IRH_LONG"]["time"], corrected_long))
    return sensor_dict


def read_and_downsample(sensor_time, sensor_data):
    """
    Reads the Sensor Values and sample the data down to 1 Hz

    :param sensor_time: Array with the Time Values of the Sensor
    :param sensor_data: Array with the Data of the Sensor

    :return: Sampled Array of the time and Sampled Array of the Data
    """

    sampled_time = []
    sampled_data = []
    for sensor_index in range(len(sensor_data) - 1):
        if (int(sensor_time[sensor_index])) not in sampled_time:
            sampled_time.append(int(sensor_time[sensor_index]))
            sampled_data.append(sensor_data[sensor_index])
    return sampled_time, sampled_data


def slice_calibrationphase(groundspeed_data):
    """
    Remove the calibrationphase from the Data by checking the groundspeed

    :param groundspeed_data: Array of the Groundspeed Data

    :return: index of the first value where the Groundspeed is bigger than 50
    """

    for groundspeed_index in range(len(groundspeed_data)):
        if groundspeed_data[groundspeed_index] >= 50:
            return groundspeed_index


def get_height_above_groundlevel(sensor_dict, position_elevation):
    """
    Calculates the height above groundlevel and appends it to the position_elevation dictionary

    :param sensor_dict: dictionary with the data and time for each sensor
    :param position_elevation: dictionary with the terrain height for each time

    :return: position_elevation dictionary with the height above groundlevel appended to the dictionary as Height
    """

    for i in range(len(position_elevation)):
        position_elevation[i].update(
            {'Height': sensor_dict["IRH_ALT"]["data"][i] - (position_elevation[i]['Elevation'] * 3.28084)})
        position_elevation[i].update({'Vertvel': sensor_dict["IRH_VERTVEL"]["data"][i]})
    return position_elevation


def get_missing_flight_data(sensor_dict):
    """
    Gets the position_elevation dictionary with height above groundlevel and terrain height without the calibration phase

    :param sensor_dictionary: Dictionary of all sensors used and there data and time

    :return: position_elevation Dictionary with height above groundlevel and terrain height without the calibration phase
    """

    position_elevation = get_geo_data(sensor_dict["IRH_LONG"]["data"], sensor_dict["IRH_LAT"]["data"],
                                      sensor_dict["IRH_LAT"]["time"])
    position_elevation = get_height_above_groundlevel(sensor_dict, position_elevation)
    flight_start_index = slice_calibrationphase(sensor_dict["IRH_GS"]["data"])
    position_elevation = position_elevation[flight_start_index:]
    return position_elevation


def get_geo_data(long, lat, time):
    """
    Splits the longitude and latitude and into list with the size 100 elements for the api request to get the terrain height

    :param long: list of the longitude values form the flight
    :param lat: list of the latitude values form the flight
    :param time: list of the time values form the flight

    :return: position_elevation Dictionary with the Terrain height for given latitude and longitude
    """
    position_elevation = []
    for i in range(0, len(long), 100):
        if (len(long) - 1 - i) >= 100:
            position_elevation += (get_list_elevation(lat[i:i + 100], long[i:i + 100], time[i:i + 100]))
        else:
            position_elevation += (
                get_list_elevation(lat[i:len(long)], long[i:len(long)], time[i:len(time)]))
    return position_elevation


def get_limits():
    """
    Calculates the limit for the sinkrate for the elevation between 20 and 3500ft and returns a dictionary with the values
    for the elevation and the sinkrate limits

    :return: vertvel_threshold_dict dictionary with the sinkrate limits
    """
    vertvel_threshold_dict = {}
    for rad_alt in range(20, 3501):
        sinkrate = get_sink_rate(rad_alt)
        vertvel_threshold_dict[str(rad_alt)] = {'elev': rad_alt, 'sink_rate_limit': sinkrate}
    return vertvel_threshold_dict


def get_list_elevation(lat_list, long_list, timestamp):
    """
    Reqeust the terrain height form 'opentopodata.org' for max 100 values in one request and creates a dictionary element
    with the elevation, latitude, longitude and time for each request and appends this dictionary element to the elevation
    dictionary

    :param lat_list: latitude list max 100 elements
    :param long_list: longitude list max 100 elements
    :param timestamp: time list max 100 elements

    :return: dictionary with elevation, latitude, longitude and time for each request in the lists
    """

    if len(lat_list) != len(long_list) or (len(lat_list) > 100 and len(long_list) > 100):
        print("Check Lists, Value not Accepted")
        return []
    else:
        command = "curl \""
        for lat, long in zip(lat_list, long_list):
            command = command + str(lat) + "," + str(long) + "|"
        command = command[:-1]
        command = command + "\""
        result = os.popen(command[:-1]).read()
        print(result)
        preliminary_dict = json.loads(result)
        result_list = preliminary_dict['results']
        elevation = []
        time_index = 0
        for result_dict in result_list:
            time_stamp = timestamp[time_index]
            elev = result_dict['elevation']
            lat = result_dict['location']['lat']
            long = result_dict['location']['lng']
            elevation.append({'Timestamp': time_stamp, 'Latitude': lat, 'Longitude': long, 'Elevation': elev})
            time_index += 1
        return elevation
