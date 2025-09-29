#!/usr/bin/env python3
"""
Example script to demonstrate git workflow with JS/TS converter.

This script shows how to:
1. Create tools in JavaScript/TypeScript
2. Generate Python code for inspection/debugging
3. Track changes with git
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the parent directory to sys.path if needed
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from learn.nodeai_js_deployer import js_tool, js_box, js_brain
from learn.js_to_python_converter import js_to_python

# Directory to store generated Python files
GENERATED_DIR = Path(__file__).parent / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

# Create example JavaScript tools for demonstration

@js_tool(["GitExample"])
def calculate_statistics(numbers):
    """
    function calculateStatistics(numbers) {
        // Sort the numbers for calculations
        const sorted = [...numbers].sort((a, b) => a - b);
        
        // Calculate basic statistics
        const sum = numbers.reduce((a, b) => a + b, 0);
        const mean = sum / numbers.length;
        const min = sorted[0];
        const max = sorted[sorted.length - 1];
        
        // Calculate median
        const middle = Math.floor(sorted.length / 2);
        const median = sorted.length % 2 === 0
            ? (sorted[middle - 1] + sorted[middle]) / 2
            : sorted[middle];
        
        // Calculate standard deviation
        const squaredDiffs = numbers.map(n => Math.pow(n - mean, 2));
        const variance = squaredDiffs.reduce((a, b) => a + b, 0) / numbers.length;
        const stdDev = Math.sqrt(variance);
        
        return {
            count: numbers.length,
            sum: sum,
            mean: mean,
            median: median,
            min: min,
            max: max,
            stdDev: stdDev
        };
    }
    """
    pass

@js_tool(["GitExample"], language="typescript")
def filter_data(data: list, criteria: dict) -> list:
    """
    function filterData(data: any[], criteria: Record<string, any>): any[] {
        return data.filter(item => {
            // Check each criteria key
            for (const key in criteria) {
                if (criteria.hasOwnProperty(key)) {
                    const criteriaValue = criteria[key];
                    
                    // Skip undefined/null criteria
                    if (criteriaValue === undefined || criteriaValue === null) {
                        continue;
                    }
                    
                    // Handle different types of criteria
                    if (typeof criteriaValue === 'object') {
                        // Range filter with min/max
                        if ('min' in criteriaValue && item[key] < criteriaValue.min) {
                            return false;
                        }
                        if ('max' in criteriaValue && item[key] > criteriaValue.max) {
                            return false;
                        }
                    } else {
                        // Exact match filter
                        if (item[key] !== criteriaValue) {
                            return false;
                        }
                    }
                }
            }
            
            // All criteria passed
            return true;
        });
    }
    """
    pass

def extract_js_code(func):
    """Extract JavaScript code from a function's docstring."""
    docstring = func.__doc__
    if not docstring:
        return ""
    
    # Extract code from docstring (between triple quotes)
    lines = docstring.strip().split("\n")
    code = "\n".join(lines)
    
    return code

def generate_python_code():
    """Generate Python code from JavaScript/TypeScript tools."""
    tools = [
        (calculate_statistics, "calculate_statistics.py"),
        (filter_data, "filter_data.py")
    ]
    
    for tool, filename in tools:
        js_code = extract_js_code(tool)
        python_code = js_to_python(js_code)
        
        # Save to generated directory
        output_path = GENERATED_DIR / filename
        with open(output_path, "w") as f:
            f.write("# Generated Python code from JavaScript/TypeScript\n")
            f.write("# DO NOT EDIT DIRECTLY - EDIT THE SOURCE JS/TS INSTEAD\n\n")
            f.write(python_code)
            
        print(f"Generated Python code for {tool.__name__} -> {output_path}")

def run_git_commands():
    """Run git commands to demonstrate workflow."""
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "status"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Not in a git repository or git not installed. Skipping git commands.")
        return False
    
    commands = [
        # Show status
        ["git", "status"],
        
        # Add generated files to git
        ["git", "add", str(GENERATED_DIR)],
        
        # Show what would be committed
        ["git", "status"]
    ]
    
    print("\n--- Git Workflow Demonstration ---")
    for cmd in commands:
        print(f"\n> {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    
    # Remind user about committing
    print("\nTo commit these changes:")
    print("git commit -m \"Update generated Python code from JS/TS tools\"")
    
    return True

def main():
    """Main function to demonstrate git workflow."""
    print("🚀 JavaScript/TypeScript to Python Converter Git Workflow Example")
    print("=" * 70)
    
    # Generate Python code from JS/TS tools
    generate_python_code()
    
    # Run git commands
    git_success = run_git_commands()
    
    if git_success:
        print("\n✅ Git workflow demonstration completed successfully.")
    else:
        print("\n⚠️ Git commands were skipped. Make sure git is installed and you're in a git repository.")
    
    print("\nCheck the 'examples/generated' directory for the generated Python files.")

if __name__ == "__main__":
    main()
