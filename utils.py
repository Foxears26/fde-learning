"""Small reusable helper functions."""


def convert_temperature(temperature, unit):
    """Convert a temperature between Celsius and Fahrenheit.

    Args:
        temperature: The temperature value to convert.
        unit: The input unit, "C" for Celsius or "F" for Fahrenheit.

    Returns:
        The converted temperature as a float.

    Raises:
        ValueError: If unit is not "C" or "F".
    """
    unit = unit.strip().upper()

    if unit == "F":
        return (temperature - 32) * 5 / 9
    elif unit == "C":
        return temperature * 9 / 5 + 32
    else:
        raise ValueError('unit must be "C" or "F"')
