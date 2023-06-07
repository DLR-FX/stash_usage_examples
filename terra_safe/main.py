from stashclient.client import Client

from terra_safe.data_handling import transform_data, get_missing_flight_data, get_limits, setup_sensor_dict
from terra_safe.safety_handling import check_flight
from terra_safe.stash_requests import get_series_connector_id, get_time_series, get_data_series, \
    get_data_series_id, get_time_series_id


def fill_sensor_dict(list_of_sensors, flight_id, client):
    """
    Calls each step for filling the sensor_dictionary and fills the sensor_dict with data

    :param list_of_sensors: list with all sensor that should be used in this program
    :param flight_id: string with the id for that flight in the stash
    :param client: client object form the stash api to interact with the stash


    :return: dictionary sensor_dict containing each sensor form the sensor list and the data for that sensor
    """
    sensor_dict = setup_sensor_dict(list_of_sensors)
    sensor_dict = get_series_connector_id(sensor_dict, flight_id, client)
    sensor_dict = get_time_series_id(sensor_dict, client)
    sensor_dict = get_time_series(sensor_dict, client)
    sensor_dict = get_data_series_id(sensor_dict, client, flight_id)
    sensor_dict = get_data_series(sensor_dict, client)

    return sensor_dict


if __name__ == "__main__":
    instance = "prod"
    list_of_sensors = ["IRH_ALT", "IRH_LAT", "IRH_LONG", "IRH_LATFINE", "IRH_LONGFINE", "IRH_VERTVEL", "IRH_GS"]
    flight_name = '2022-03-16_F22-04_Training'
    client = Client.from_instance_name(instance)
    flight_id = client.id(flight_name)
    sensor_dict = fill_sensor_dict(list_of_sensors, flight_id, client)
    sensor_dict = transform_data(sensor_dict)
    position_elevation = get_missing_flight_data(sensor_dict)
    vertvel_threshold = get_limits()
    check_flight(position_elevation, vertvel_threshold)