"""Sample Python module - Updated."""

def greet(name, greeting="Hello"):
    """Greet a person with custom greeting."""
    return f"{greeting}, {name}!"


def farewell(name):
    """Say goodbye."""
    return f"Goodbye, {name}!"


class Calculator:
    """A simple calculator with more operations."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


if __name__ == "__main__":
    print(greet("World", "Hi"))
    print(farewell("World"))
