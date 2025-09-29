#!/usr/bin/env python
"""
Very Simple JavaScript Agent Example

A minimal example that focuses only on the essential patterns
that work well with our converter.
"""

from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain
from learn.thought import TextThought
from learn.js_to_python_converter import js_to_python
import ast

# --- Agent Configuration ---
AGENT_TYPE = "SimpleCalculator"
AI_MODEL = "gpt-4o"

# --- Data Models ---

@js_box([AGENT_TYPE])
class CalculationData:
    """
    interface CalculationData {
        lastResult: number;
        history: string[];
    }
    """
    pass

# --- Tools ---

@js_tool([AGENT_TYPE])
def calculate_simple():
    """
    function calculateSimple(a, b, operation) {
      // Get calculation data
      const calcData = this.unbox("calculation_data") || {
        lastResult: 0,
        history: []
      };
      
      // Validate inputs
      if (typeof a !== "number" || typeof b !== "number") {
        return "Both a and b must be numbers";
      }
      
      // Perform calculation
      let result = 0;
      let operationName = "";
      
      if (operation === "add") {
        result = a + b;
        operationName = "Addition";
      } else if (operation === "subtract") {
        result = a - b;
        operationName = "Subtraction";
      } else if (operation === "multiply") {
        result = a * b;
        operationName = "Multiplication";
      } else if (operation === "divide") {
        if (b === 0) {
          return "Cannot divide by zero";
        }
        result = a / b;
        operationName = "Division";
      } else {
        return "Invalid operation. Use 'add', 'subtract', 'multiply', or 'divide'";
      }
      
      // Update history
      const entry = operationName + ": " + a + " " + operation + " " + b + " = " + result;
      calcData.history.push(entry);
      calcData.lastResult = result;
      
      // Save data
      this.box("calculation_data", calcData);
      
      return "Result: " + result;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def get_history():
    """
    function getHistory() {
      // Get calculation data
      const calcData = this.unbox("calculation_data");
      
      // Check if data exists
      if (!calcData || !calcData.history || calcData.history.length === 0) {
        return "No calculation history yet";
      }
      
      // Build history output
      let output = "Calculation History:\\n";
      
      for (let i = 0; i < calcData.history.length; i++) {
        output += (i + 1) + ". " + calcData.history[i] + "\\n";
      }
      
      output += "\\nLast result: " + calcData.lastResult;
      
      return output;
    }
    """
    pass

# --- Brain Configuration ---

@js_brain([AGENT_TYPE])
def calculator_brain():
    """Configure the brain for the calculator."""
    return {
        "instructions": """
        You are a helpful calculator assistant.
        You can perform basic arithmetic operations.
        Use the calculate_simple tool to perform calculations.
        Use the get_history tool to retrieve calculation history.
        """,
        "clients": [
            {
                "model_name": AI_MODEL,
                "provider": "openai",
            }
        ]
    }

# --- Test Function ---
def test_tool_conversion():
    """Test if the JavaScript tools convert properly to Python."""
    # Extract JS code
    calculate_js = calculate_simple.__doc__.strip()
    history_js = get_history.__doc__.strip()
    
    # Function to test a conversion
    def test_conversion(name, js_code):
        print(f"\n--- Testing {name} conversion ---")
        try:
            python_code = js_to_python(js_code)
            # Check if valid Python
            ast.parse(python_code)
            print(f"✅ {name}: Successfully converted to valid Python")
            return True
        except Exception as e:
            print(f"❌ {name}: Conversion failed - {e}")
            return False
    
    # Test both tools
    calc_success = test_conversion("calculate_simple", calculate_js)
    history_success = test_conversion("get_history", history_js)
    
    return calc_success and history_success

if __name__ == "__main__":
    # Run the tests
    success = test_tool_conversion()
    
    if success:
        print("\n🎉 All JavaScript tools converted successfully to Python!")
        print("This example demonstrates best practices for writing JS/TS code")
        print("that will properly convert to Python with our converter.")
        
        print("\nKey patterns that work well:")
        print("1. Simple control flow with early returns")
        print("2. Avoiding template literals")
        print("3. Simple variable assignments")
        print("4. Clear, sequential logic")
    else:
        print("\n⚠️ Some conversions failed. Check the JavaScript code.")
        
    print("\nTo deploy this agent:")
    print("1. Update the base_url in the code")
    print("2. Initialize calculation_data")
    print("3. Call deploy() on the client")
