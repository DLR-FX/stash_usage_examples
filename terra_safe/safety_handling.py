def check_below_rad_alt_max(altitude):
    """
    This function checks if the given altitude is within the range of 3500 and 50.

    :param altitude: An integer representing the altitude value.

    :return: A boolean value. Returns True if the altitude is between 3500 and 50, otherwise returns False.
    """


    if 3500 > altitude >= 50:
        return True
    else:
        return False


def get_sink_rate(ft):
    """
    Calculates the sink rate for a given altitude.

    :param height: The altitude in feet.
    :return: The sink rate for the given altitude.
    """

    sink_rate = 2000 + ((6000 - 2000) / (3200 - 720)) * (ft - 720)
    return sink_rate


def check_flight(position_elevation, vertvel_threshold_dict):
    """
    Checks each value in the position_elevation dictionary to determine if the active sink rate is greater than the sink rate limit for that height. If the sink rate exceeds the limit, a warning will be printed.

    :param position_elevation: A dictionary with the information for each timestamp of the flight.
    :param vertvel_threshold_dict: A dictionary with the altitude and the corresponding sink rate limit for that altitude.

    """

    for position_elevation_index in range(len(position_elevation)):
        if position_elevation[position_elevation_index]["Vertvel"] < 0.0 and check_below_rad_alt_max(
                position_elevation[position_elevation_index]["Height"]):
            active_sinkrate = position_elevation[position_elevation_index]["Vertvel"] * -1.0
            height_int = int(position_elevation[position_elevation_index][
                                 "Height"])
            if active_sinkrate >= vertvel_threshold_dict[str(height_int)]["sink_rate_limit"]:
                print("Warning")