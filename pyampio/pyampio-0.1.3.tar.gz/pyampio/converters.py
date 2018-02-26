"""This is a helper module with value conversion functions."""


from calendar import day_name


def convert_unchanged(value):
    """Fake data converter."""
    return value


def convert_temperature_int(value):
    """Convert the integer temperature value to signed."""
    return int(value) - 100


def convert_temperature(value):
    """Convert the decimal dotted temperature value (single digit)."""
    return (int(value) - 1000) / 10


def convert_meteo(value):
    """Convert the value from METEO station."""
    return (int(value) - 10000) / 10


def convert_weekday(value):
    """Convert the week day number to weekday name."""
    try:
        return day_name[value - 1]
    except (TypeError, IndexError):
        return "N/A"
