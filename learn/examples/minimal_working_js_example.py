#!/usr/bin/env python
"""
Minimal Working JavaScript Example

This example contains the absolute minimum JavaScript code that will successfully
convert to Python with our converter. It follows all the best practices and avoids
complex features that might cause conversion issues.
"""

from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain

# --- Agent Configuration ---
AGENT_TYPE = "MathHelper"

# --- Data Model ---
@js_box([AGENT_TYPE])
class MathHistory:
    """
    interface MathHistory {
        operations: Array<string>;
        lastValue: number;
    }
    """
    pass

# --- Tools ---

@js_tool([AGENT_TYPE])
def add_numbers():
    """
    function addNumbers(a, b) {
      var result = a + b;
      
      var history = this.unbox("math_history") || {
        operations: [],
        lastValue: 0
      };
      
      history.operations.push(a + " + " + b + " = " + result);
      history.lastValue = result;
      
      this.box("math_history", history);
      
      return "The sum is: " + result;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def get_math_history():
    """
    function getMathHistory() {
      var history = this.unbox("math_history");
      
      if (!history || history.operations.length === 0) {
        return "No calculation history available";
      }
      
      var output = "Calculation History:";
      
      for (var i = 0; i < history.operations.length; i++) {
        output = output + "\\n" + (i + 1) + ". " + history.operations[i];
      }
      
      return output;
    }
    """
    pass

# --- Brain Configuration ---
@js_brain([AGENT_TYPE])
def math_helper_brain():
    """Configure the brain for the math helper."""
    return {
        "instructions": """
        You are a math helper that can add numbers.
        You can use:
        - add_numbers(a, b): Add two numbers together
        - get_math_history(): Show history of calculations
        """,
        "clients": [
            {
                "model_name": "gpt-3.5-turbo",
                "provider": "openai",
            }
        ]
    }

# --- Demo Code ---
def main():
    """Run a demonstration of the JavaScript to Python converter."""
    print("🚀 Minimal JavaScript to Python Converter Example")
    print("=" * 60)
    
    # Extract JavaScript code
    add_js_code = add_numbers.__doc__.strip()
    history_js_code = get_math_history.__doc__.strip()
    
    # Test conversion
    from learn.js_to_python_converter import js_to_python
    
    # Test addNumbers
    print("\nJavaScript code for addNumbers:")
    print("-" * 30)
    print(add_js_code)
    
    print("\nConverted Python code:")
    print("-" * 30)
    try:
        add_py_code = js_to_python(add_js_code)
        print(add_py_code)
        
        # Validate Python syntax
        import ast
        ast.parse(add_py_code)
        print("\n✅ Valid Python code!")
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
    
    # Test getMathHistory
    print("\n\nJavaScript code for getMathHistory:")
    print("-" * 30)
    print(history_js_code)
    
    print("\nConverted Python code:")
    print("-" * 30)
    try:
        history_py_code = js_to_python(history_js_code)
        print(history_py_code)
        
        # Validate Python syntax
        import ast
        ast.parse(history_py_code)
        print("\n✅ Valid Python code!")
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
    
    # Summary
    print("\n\n📋 Key Features of This Example:")
    print("1. Simple JavaScript with minimal complexity")
    print("2. Uses 'var' instead of 'let'/'const' for better conversion")
    print("3. No template literals, only string concatenation")
    print("4. Simple control flow with if/for statements")
    print("5. No complex JavaScript features like destructuring or arrow functions")
    
    print("\n🎓 This example demonstrates the minimal working JS code that")
    print("   successfully converts to Python with our converter.")
    

if __name__ == "__main__":
    main()
