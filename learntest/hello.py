def greet(name: str) -> str:
    """Return a friendly greeting for the given name."""
    if name == "":
        return "Hello, stranger!"
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("World"))
