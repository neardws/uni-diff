// Utility functions - Updated

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    if (b === 0) throw new Error('Cannot divide by zero');
    return a / b;
}

const config = {
    apiUrl: 'https://api.example.com',
    timeout: 10000,
    retries: 3
};

module.exports = { add, subtract, multiply, divide, config };
