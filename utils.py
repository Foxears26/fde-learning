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


def is_even(number):
    """Return True if number is even, otherwise return False."""
    return number % 2 == 0


def reverse_string(text):
    """Return text with its characters in reverse order."""
    return text[::-1]


def average(numbers):
    """Return the arithmetic mean of a non-empty collection of numbers."""
    if not numbers:
        raise ValueError("numbers must not be empty")

    return sum(numbers) / len(numbers)


def max_of_three(first, second, third):
    """Return the largest of three values."""
    return max(first, second, third)


def count_vowels(text):
    """Count English vowels (a, e, i, o, u) in text, ignoring case."""
    vowels = "aeiou"
    return sum(1 for character in text.lower() if character in vowels)


def factorial(number):
    """Return the factorial of a non-negative integer."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("number must be an integer")
    if number < 0:
        raise ValueError("number must not be negative")

    result = 1
    for value in range(2, number + 1):
        result *= value
    return result


def is_prime(number):
    """Return True if number is a prime integer, otherwise return False."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("number must be an integer")
    if number < 2:
        return False

    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


def remove_duplicates(items):
    """Return a list without duplicate items, preserving their original order."""
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def word_count(text):
    """Return the number of whitespace-separated words in text."""
    return len(text.split())
