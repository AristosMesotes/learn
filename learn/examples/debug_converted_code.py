#!/usr/bin/env python
"""
Helper script to debug and fix converted JavaScript/TypeScript code.

This script:
1. Extracts JavaScript code from our tools
2. Runs the conversion manually
3. Shows potential indentation issues
4. Creates fixed versions with proper Python syntax
"""

from learn.js_to_python_converter import js_to_python
import re
import ast
import inspect
from textwrap import dedent, indent

# Extract JS code from a Python docstring
def extract_js_code(func_or_docstring):
    if callable(func_or_docstring):
        docstring = func_or_docstring.__doc__ or ""
    else:
        docstring = func_or_docstring
    
    return docstring.strip()

# Fix common indentation issues
def fix_indentation(python_code):
    """Fix common indentation issues in converted code."""
    lines = python_code.split('\n')
    fixed_lines = []
    indent_level = 0
    
    # Fix common issues
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            fixed_lines.append('')
            continue
            
        # Adjust indent for control flow keywords
        if stripped.startswith(('elif', 'else', 'except', 'finally')):
            indent_level = max(0, indent_level - 1)
        
        # Add indented line
        fixed_lines.append('    ' * indent_level + stripped)
        
        # Adjust indent level for next line
        if stripped.endswith(':'):
            indent_level += 1
        elif i < len(lines) - 1 and re.match(r'\s*return\s+', stripped) and not lines[i+1].strip().startswith(('elif', 'else', 'except', 'finally')):
            # Return statement that's not followed by an outdent keyword
            pass  # Don't change indent level
    
    return '\n'.join(fixed_lines)

# Test if the Python code is valid
def is_valid_python(code):
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

# Fix common conversion issues
def post_process_conversion(python_code):
    """Fix common issues in the converted code."""
    # Fix JS-style comments that weren't converted
    python_code = re.sub(r'//\s*(.*)', r'# \1', python_code)
    
    # Fix indentation
    python_code = fix_indentation(python_code)
    
    # Add missing pass statement to empty blocks
    python_code = re.sub(r'(\w+):\s*\n\s*\n', r'\1:\n    pass\n\n', python_code)
    
    # Fix missing colons in if/for/while statements
    python_code = re.sub(r'(if|for|while)\s+(.+)\s*\n', r'\1 \2:\n', python_code)
    
    return python_code

# Fix a specific tool
def fix_tool_code(js_code, name):
    """Fix a specific tool's code."""
    print(f"\n{'='*40}")
    print(f"Debugging tool: {name}")
    print(f"{'='*40}")
    
    # Convert JS to Python
    raw_python = js_to_python(js_code)
    print("\nRaw conversion:")
    print("-" * 20)
    print(raw_python)
    
    # Check if valid Python
    is_valid, error = is_valid_python(raw_python)
    if is_valid:
        print("\n✅ Valid Python code!")
    else:
        print(f"\n❌ Invalid Python code: {error}")
        
        # Try to fix issues
        fixed_python = post_process_conversion(raw_python)
        print("\nFixed version:")
        print("-" * 20)
        print(fixed_python)
        
        # Check if fixed version is valid
        is_valid, error = is_valid_python(fixed_python)
        if is_valid:
            print("\n✅ Fixed version is valid Python!")
        else:
            print(f"\n❌ Fixed version still has issues: {error}")
            
    return raw_python

# Test with our space explorer tools
def main():
    # Import space_explorer_js tools
    from learn.examples.space_explorer_js import travel_to_planet, scan_planet

    # Fix travel_to_planet
    js_code = extract_js_code(travel_to_planet)
    fixed_travel = fix_tool_code(js_code, "travel_to_planet")
    
    # Fix scan_planet
    js_code = extract_js_code(scan_planet)
    fixed_scan = fix_tool_code(js_code, "scan_planet")
    
    print("\n\n💡 RECOMMENDATION:")
    print("To fix the indentation errors in your converted JavaScript/TypeScript code:")
    print("1. Make sure all JS comments use // style (not /* */) for better conversion")
    print("2. Be consistent with bracketing in your JavaScript code")
    print("3. Consider using our improved post-processing function to fix common issues:")
    print("   - Add to js_to_python_converter.py")
    print("   - Call after the main conversion")
    print("   - Fix common indentation and syntax issues")

if __name__ == "__main__":
    main()
