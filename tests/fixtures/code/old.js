// Utility functions

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

const config = {
    apiUrl: 'http://localhost:3000',
    timeout: 5000
};

module.exports = { add, subtract, config };
