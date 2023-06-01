def get_series_connector_id(sensor_dict, flight_id, client):
    """
    For each sensor in the sensor_dictionary we what to find the series_connector_id by searching for the name of the sensor
    and the flight_id as parent of the sensor, the flight_id identifies the flight we want to find.
    All series_connector_id's where inserted to the dictionary of the sensor and we return the dictionary of dictionaries as
    sensor_dict


    :param sensor_dict: dictionary containing all sensors we what the data from
    :param flight_id: string with the id of the flight
    :param client: stash client object to interact with the stash

    :return: sensor_dict contains all sensors and there series_connector_id's in the dictionaries form the sensors
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"scid": client.search({'name': sensor, 'parent': f'{flight_id}'},
                                                          restrict = ['series_connector_id'])[0].get('series_connector_id')})
    return sensor_dict


def get_time_series_id(sensor_dict, client):
    """
    Requests the time_id for all sensors in the sensor_dict and append them to the sensor in the sensor_dict
    the time_id is requested through the name of the sensor and the series_connector_id which connects the data and time of
    the flight form which we want to get the time.
    And we also check in the request if the time_id is for an object that represents the time.
    The series_connector_id must already exists in the dictionary for each sensor.

    :param sensor_dict: dictionary containing all sensors we what the data from
    :param client: stash client object to interact with the stash

    :return: sensor_dict filled with the time_id foreach sensor in the dictionary
    """
    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"time_id": client.search({'series_connector_id': f'{sensor_dict[sensor]["scid"]}',
                                                              'represents': 'time'}, restrict = ['id'])[0].get('id')})
    return sensor_dict


def get_time_series(sensor_dict, client):
    """
    Requests the time values for all sensors in the sensor_dict and append them to the sensor in the sensor_dict
    the time data is requested through the time_id which must be contained in the dictionary first

    :param sensor_dict: dictionary containing all sensors we what the data from
    :param client: stash client object to interact with the stash

    :return: sensor_dict filled with the time values foreach sensor in the dictionary
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"time": client.data(sensor_dict[sensor]["time_id"])})
    return sensor_dict


def get_data_series_id(sensor_dict, client, flight_id):
    """
    Requests the data_id for all sensors in the sensor_dict and append them to the sensor in the sensor_dict
    the data_id is requested through the name of the sensor and the flight_id which identifies the flight form which we want
    to get the data

    :param sensor_dict: dictionary containing all sensors we what the data from
    :param client: stash client object to interact with the stash
    :param flight_id: string with the id of the flight

    :return: sensor_dict filled with the data_id foreach sensor in the dictionary
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"data_id": client.search({'name': sensor, 'parent': f'{flight_id}'},
                                                             restrict = ['id'])[0].get('id')})
    return sensor_dict


def get_data_series(sensor_dict, client):
    """
    Requests the data values for all sensors in the sensor_dict and append them to the sensor in the sensor_dict
    the data is requested through the data_id which must be contained in the dictionary first


    :param sensor_dict: dictionary containing all sensors we what the data from
    :param client: stash client object to interact with the stash

    :return: sensor_dict filled with the data foreach sensor in the dictionary
    """

    for sensor in sensor_dict.keys():
        sensor_dict[sensor].update({"data": client.data(sensor_dict[sensor]["data_id"])})
    return sensor_dict
