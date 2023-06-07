import os
import json
import numpy as np

from terra_safe.safety_handling import get_sink_rate

def setup_sensor_dict(list_of_sensors):
    """
    Creates an empty sub-dictionary for each sensor in the list_of_sensors and returns the dictionary with all sensors and their corresponding sub-dictionaries.

    :param list_of_sensors: A list of sensors to be used in the program.

    :return: A sensor_dictionary containing all sensors and their respective empty dictionaries.
    """


    sensor_dict = {}
    for sensor in list_of_sensors:
        sensor_dict.update({sensor : {}})
    return sensor_dict

def correct_position_values(normal_value, fine_value):
    """
    Combines the Latitude/Longitude values and the LatitudeFine/LongitudeFine values from the arrays to obtain more precise latitude and longitude coordinates.

    :param normal_value: An array of Latitude/Longitude values.
    :param fine_value: An array of LatitudeFine/LongitudeFine values.

    :return: An array of more precise latitude or longitude coordinates.
    """

    normal_array = np.array(normal_value)
    fine_array = np.array(fine_value)
    corrected_vector = normal_array + fine_array
    return corrected_vector


def corrected_value_to_dict(name, reference_time, data):
    """
    Creates a dictionary for the corrected sensor using the sensor name as the key. The dictionary includes the sub-elements 'reference_time' and 'data'.

    :param name: A string representing the name of the corrected sensor.
    :param reference_time: An array of time values.
    :param data: An array containing the data of the corrected sensor.

    :return: A dictionary with one element that represents the new corrected sensor.
    """

    sensor_dict_content = {name: {"time": reference_time, "data": data}}
    return sensor_dict_content




def transform_data(sensor_dict):
    """
    Populates a dictionary with the data and time for the sensors contained in sensor_dict. Additionally, the corrected values for latitude and longitude are appended to the dictionary.

    :param sensor_dict: A dictionary containing the sensor names where the data should be stored.

    :return: A dictionary with the sensor names and their corresponding time and data values.
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
    Reads the sensor values and downsamples the data to 1 Hz.

    :param sensor_time: An array containing the time values of the sensor.
    :param sensor_data: An array containing the data of the sensor.

    :return: Sampled array of the time values and sampled array of the data.
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
    Removes the calibration phase from the data by checking the groundspeed.

    :param groundspeed_data: An array of groundspeed data.

    :return: The index of the first value where the groundspeed is greater than 50.
    """

    for groundspeed_index in range(len(groundspeed_data)):
        if groundspeed_data[groundspeed_index] >= 50:
            return groundspeed_index


def get_height_above_groundlevel(sensor_dict, position_elevation):
    """
    Calculates the height above ground level and appends it to the position_elevation dictionary.

    :param sensor_dict: A dictionary containing the data and time for each sensor.
    :param position_elevation: A dictionary containing the terrain height for each time.

    :return: The position_elevation dictionary with the height above ground level appended as 'Height'.
    """

    for i in range(len(position_elevation)):
        position_elevation[i].update(
            {'Height': sensor_dict["IRH_ALT"]["data"][i] - (position_elevation[i]['Elevation'] * 3.28084)})
        position_elevation[i].update({'Vertvel': sensor_dict["IRH_VERTVEL"]["data"][i]})
    return position_elevation


def get_missing_flight_data(sensor_dict):
    """
    Retrieves the position_elevation dictionary with height above ground level and terrain height, excluding the calibration phase.

    :param sensor_dictionary: A dictionary containing the data and time for all used sensors.

    :return: The position_elevation dictionary with height above ground level and terrain height, excluding the calibration phase.
    """


    position_elevation = get_geo_data(sensor_dict["IRH_LONG"]["data"], sensor_dict["IRH_LAT"]["data"],
                                      sensor_dict["IRH_LAT"]["time"])
    position_elevation = get_height_above_groundlevel(sensor_dict, position_elevation)
    flight_start_index = slice_calibrationphase(sensor_dict["IRH_GS"]["data"])
    position_elevation = position_elevation[flight_start_index:]
    return position_elevation


def get_geo_data(long, lat, time):
    """
    Splits the longitude and latitude values into lists with a size of 100 elements each for the API request to retrieve the terrain height.

    :param long: A list of longitude values from the flight.
    :param lat: A list of latitude values from the flight.
    :param time: A list of time values from the flight.

    :return: A position_elevation dictionary with the terrain height for the given latitude and longitude.
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
    Calculates the sink rate limits for elevations between 20 and 3500 ft and returns a dictionary with the elevation and corresponding sink rate limits.

    :return: A vertvel_threshold_dict dictionary with the sink rate limits.
    """

    vertvel_threshold_dict = {}
    for rad_alt in range(20, 3501):
        sinkrate = get_sink_rate(rad_alt)
        vertvel_threshold_dict[str(rad_alt)] = {'elev': rad_alt, 'sink_rate_limit': sinkrate}
    return vertvel_threshold_dict


def get_list_elevation(lat_list, long_list, timestamp):
    """
    Requests the terrain height from 'opentopodata.org' for a maximum of 100 values in one request. It creates a dictionary element containing the elevation, latitude, longitude, and time for each request and appends this dictionary element to the elevation dictionary.

    :param lat_list: A list of latitude values (maximum 100 elements).
    :param long_list: A list of longitude values (maximum 100 elements).
    :param timestamp: A list of time values (maximum 100 elements).

    :return: A dictionary with elevation, latitude, longitude, and time for each request in the lists.
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
