def get_series_connector_id(sensor_dict, flight_id, client):
    """
    For each sensor in the sensor_dictionary, we want to find the series_connector_id by searching for the sensor's name and the flight_id as the parent of the sensor. The flight_id identifies the flight we want to find. All series_connector_id's are inserted into the sensor dictionary as dictionaries. The updated sensor dictionary is then returned.

    :param sensor_dict: A dictionary containing all sensors from which we want to retrieve data.
    :param flight_id: A string representing the ID of the flight.
    :param client: A stash client object used to interact with the stash.

    :return: The updated sensor_dict containing all sensors and their corresponding series_connector_id's.
    """


    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"scid": client.search({'name': sensor, 'parent': f'{flight_id}'},
                                                          restrict = ['series_connector_id'])[0].get('series_connector_id')})
    return sensor_dict


def get_time_series_id(sensor_dict, client):
    """
    Requests the time_id for all sensors in the sensor_dict and appends them to each sensor in the sensor_dict. The time_id is obtained by using the sensor's name and the series_connector_id, which connects the data and time of the flight from which we want to retrieve the time. Additionally, the function checks if the time_id represents an object that represents time. It is assumed that the series_connector_id already exists in the dictionary for each sensor.

    :param sensor_dict: A dictionary containing all sensors from which we want to retrieve data.
    :param client: A stash client object used to interact with the stash.

    :return: The updated sensor_dict with the time_id appended to each sensor in the dictionary.
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"time_id": client.search({'series_connector_id': f'{sensor_dict[sensor]["scid"]}',
                                                              'represents': 'time'}, restrict = ['id'])[0].get('id')})
    return sensor_dict


def get_time_series(sensor_dict, client):
    """
    Requests the time values for all sensors in the sensor_dict and appends them to each sensor in the sensor_dict. The time data is requested using the time_id, which must be already present in the dictionary for each sensor.

    :param sensor_dict: A dictionary containing all sensors from which we want to retrieve data.
    :param client: A stash client object used to interact with the stash.

    :return: The updated sensor_dict with the time values appended to each sensor in the dictionary.
    """
    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"time": client.data(sensor_dict[sensor]["time_id"])})
    return sensor_dict


def get_data_series_id(sensor_dict, client, flight_id):
    """
    Requests the data_id for all sensors in the sensor_dict and appends them to each sensor in the sensor_dict. The data_id is obtained using the sensor's name and the flight_id, which identifies the flight from which we want to retrieve the data.

    :param sensor_dict: A dictionary containing all sensors from which we want to retrieve data.
    :param client: A stash client object used to interact with the stash.
    :param flight_id: A string representing the ID of the flight.

    :return: The updated sensor_dict with the data_id appended to each sensor in the dictionary.
    """


    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"data_id": client.search({'name': sensor, 'parent': f'{flight_id}'},
                                                             restrict = ['id'])[0].get('id')})
    return sensor_dict


def get_data_series(sensor_dict, client):
    """
    Requests the data values for all sensors in the sensor_dict and appends them to each sensor in the sensor_dict. The data is requested using the data_id, which must already be present in the dictionary for each sensor.

    :param sensor_dict: A dictionary containing all sensors from which we want to retrieve data.
    :param client: A stash client object used to interact with the stash.

    :return: The updated sensor_dict with the data values appended to each sensor in the dictionary.
    """


    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"data": client.data(sensor_dict[sensor]["data_id"])})
    return sensor_dict
