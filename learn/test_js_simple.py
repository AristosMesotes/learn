#!/usr/bin/env python3
"""
Simple test for JavaScript to Python conversion.
"""

from learn.js_to_python_converter import js_to_python

# Test cases
test_cases = [
    # Test 1: Simple function
    {
        "name": "Simple Addition",
        "js": """
function add(a, b) {
    return a + b;
}
""",
    },
    
    # Test 2: Variables with built-in names
    {
        "name": "Built-in Variable Names",
        "js": """
function calculate() {
    const sum = 10;
    const max = 20;
    const min = 5;
    return sum + max - min;
}
""",
    },
    
    # Test 3: Object literal
    {
        "name": "Object Return",
        "js": """
function getInfo() {
    const name = "test";
    const value = 42;
    return {
        name: name,
        value: value
    };
}
""",
    },
    
    # Test 4: Array methods
    {
        "name": "Array Methods",
        "js": """
function processArray(items) {
    const filtered = items.filter(x => x > 0);
    const doubled = filtered.map(x => x * 2);
    return doubled;
}
""",
    }
]

def main():
    """Run the tests."""
    print("JavaScript to Python Converter Tests")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 30)
        print("JavaScript:")
        print(test['js'])
        
        try:
            converted = js_to_python(test['js'])
            print("\nPython:")
            print(converted)
            
            # Try to compile the Python code to check syntax
            try:
                compile(converted, f"test_{i}", "exec")
                print("\n✓ Python syntax is valid")
            except SyntaxError as e:
                print(f"\n✗ Python syntax error: {e}")
                
        except Exception as e:
            print(f"\n✗ Conversion error: {e}")
            
        print("-" * 50)

if __name__ == "__main__":
    main()
