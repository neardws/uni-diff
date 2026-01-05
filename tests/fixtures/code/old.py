"""Sample Python module."""

def greet(name):
    """Greet a person."""
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b


if __name__ == "__main__":
    print(greet("World"))
