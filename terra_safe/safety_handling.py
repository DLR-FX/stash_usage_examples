def check_below_rad_alt_max(altitude):
    """
    Checks if the given altitude is between 3500 and 50

    :param altitude: integer with the altitude

    :return: Bool with True if the altitude is between 3500 and 50 else Bool with False
    """

    if 3500 > altitude >= 50:
        return True
    else:
        return False


def get_sink_rate(ft):
    """
    Calculates the sinkrate for a given altitude

    :return: sinkrate for the given altitude
    """

    sink_rate = 2000 + ((6000 - 2000) / (3200 - 720)) * (ft - 720)
    return sink_rate


def check_flight(position_elevation, vertvel_threshold_dict):
    """
    Checks for each value in the position_elevation dictionary if the active_sinkrate is bigger than the sinkrate_limit for
    that height.
    If its above the limit there will be a warning printed
    """

    for position_elevation_index in range(len(position_elevation)):
        if position_elevation[position_elevation_index]["Vertvel"] < 0.0 and check_below_rad_alt_max(
                position_elevation[position_elevation_index]["Height"]):
            active_sinkrate = position_elevation[position_elevation_index]["Vertvel"] * -1.0
            height_int = int(position_elevation[position_elevation_index][
                                 "Height"])
            if active_sinkrate >= vertvel_threshold_dict[str(height_int)]["sink_rate_limit"]:
                print("Warning")