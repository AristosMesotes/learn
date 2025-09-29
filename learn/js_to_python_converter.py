"""
JavaScript/TypeScript to Python Code Converter

This module provides functionality to convert JavaScript/TypeScript code
to Python code that can be executed on the NodeAI backend.
"""

import re
from typing import Dict, List, Tuple, Optional
import json


class JSPythonConverter:
    """Converts JavaScript/TypeScript code to Python."""
    
    def __init__(self):
        # Track renamed variables
        self.renamed_vars = {}
        
        # Type mappings from TypeScript to Python
        self.type_map = {
            'string': 'str',
            'number': 'float',
            'boolean': 'bool',
            'any': 'Any',
            'void': 'None',
            'undefined': 'None',
            'null': 'None',
            'string[]': 'List[str]',
            'number[]': 'List[float]',
            'boolean[]': 'List[bool]',
            'any[]': 'List[Any]',
            'Array<string>': 'List[str]',
            'Array<number>': 'List[float]',
            'Array<boolean>': 'List[bool]',
            'Array<any>': 'List[Any]',
            'Promise': 'Awaitable',
            'Object': 'Dict[str, Any]',
            'Record<string, any>': 'Dict[str, Any]',
        }
        
        # Common JS/TS to Python method mappings
        self.method_map = {
            'console.log': 'print',
            'console.error': 'print',
            'console.warn': 'print',
            'Math.floor': 'int',
            'Math.ceil': 'math.ceil',
            'Math.round': 'round',
            'Math.abs': 'abs',
            'Math.max': 'max',
            'Math.min': 'min',
            'Math.random': 'random.random',
            'JSON.stringify': 'json.dumps',
            'JSON.parse': 'json.loads',
            'parseInt': 'int',
            'parseFloat': 'float',
            'toString': 'str',
            'length': 'len',
            'push': 'append',
            'pop': 'pop',
            'shift': 'pop(0)',
            'indexOf': 'index',
            'includes': 'in',
            'toLowerCase': 'lower',
            'toUpperCase': 'upper',
            'trim': 'strip',
            'split': 'split',
            'join': 'join',
            'replace': 'replace',
            'slice': 'slice',
            'substring': 'slice',
        }
        
        # Python reserved keywords and built-ins that need to be escaped
        self.python_keywords = {
            'class', 'def', 'return', 'if', 'else', 'elif', 'for', 'while',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with',
            'lambda', 'pass', 'break', 'continue', 'global', 'nonlocal',
            'assert', 'del', 'in', 'is', 'not', 'or', 'and', 'None',
            'True', 'False', 'yield', 'async', 'await',
            # Common built-ins that might be used as variable names
            'max', 'min', 'sum', 'len', 'list', 'dict', 'set', 'str',
            'int', 'float', 'bool', 'type', 'print', 'input', 'open',
            'range', 'zip', 'map', 'filter', 'sorted', 'reversed'
        }
        
    def convert(self, js_code: str) -> str:
        """Main conversion method."""
        # Remove TypeScript decorators temporarily
        decorators, js_code = self._extract_decorators(js_code)
        
        # Convert the code
        python_code = js_code
        
        # Step 1: Convert imports
        python_code = self._convert_imports(python_code)
        
        # Step 2: Convert function definitions
        python_code = self._convert_functions(python_code)
        
        # Step 3: Convert class definitions
        python_code = self._convert_classes(python_code)
        
        # Step 4: Convert array methods FIRST (before variables mess with the patterns)
        python_code = self._convert_array_methods(python_code)
        
        # Step 5: Convert variable declarations
        python_code = self._convert_variables(python_code)
        
        # Step 6: Convert control structures
        python_code = self._convert_control_structures(python_code)
        
        # Step 7: Convert object literals
        python_code = self._convert_objects(python_code)
        
        # Step 8: Convert common methods and properties
        python_code = self._convert_common_methods(python_code)
        
        # Step 9: Convert operators
        python_code = self._convert_operators(python_code)
        
        # Step 10: Clean up and format
        python_code = self._cleanup_code(python_code)
        
        # Step 11: Post-processing to fix common issues
        python_code = self._post_process(python_code)
        
        # Add necessary imports
        imports = self._generate_imports(python_code)
        if imports:
            python_code = imports + "\n\n" + python_code
            
        return python_code
    
    def _extract_decorators(self, code: str) -> Tuple[List[str], str]:
        """Extract TypeScript decorators from code."""
        decorator_pattern = r'@\w+\([^\)]*\)\s*\n'
        decorators = re.findall(decorator_pattern, code)
        clean_code = re.sub(decorator_pattern, '', code)
        return decorators, clean_code
    
    def _convert_imports(self, code: str) -> str:
        """Convert JS/TS imports to Python imports."""
        # Convert ES6 imports
        code = re.sub(
            r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?',
            lambda m: f"from {m.group(2).replace('/', '.')} import {m.group(1)}",
            code
        )
        
        # Convert default imports
        code = re.sub(
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?',
            lambda m: f"import {m.group(2).replace('/', '.')} as {m.group(1)}",
            code
        )
        
        # Convert require statements
        code = re.sub(
            r'const\s+(\w+)\s*=\s*require\([\'"]([^\'"]*)[\'"]\)\s*;?',
            lambda m: f"import {m.group(2).replace('/', '.')} as {m.group(1)}",
            code
        )
        
        return code
    
    def _convert_functions(self, code: str) -> str:
        """Convert JS/TS function definitions to Python."""
        # Convert arrow functions
        code = re.sub(
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*\{',
            r'def \1(\2):',
            code
        )
        
        # Convert async arrow functions
        code = re.sub(
            r'const\s+(\w+)\s*=\s*async\s*\(([^)]*)\)\s*=>\s*\{',
            r'async def \1(\2):',
            code
        )
        
        # Convert function declarations
        def convert_function(match):
            func_name = match.group(1)
            params = self._convert_params(match.group(2))
            return_type = self._convert_type(match.group(3)) if match.group(3) else 'Any'
            # Add a placeholder for proper indentation
            return f"def {func_name}({params}) -> {return_type}:\n    __INDENT__"
            
        code = re.sub(
            r'function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^\{]+))?\s*\{',
            convert_function,
            code
        )
        
        # Convert async function declarations
        code = re.sub(
            r'async\s+function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^\{]+))?\s*\{',
            lambda m: f"async def {m.group(1)}({self._convert_params(m.group(2))}) -> {self._convert_type(m.group(3)) if m.group(3) else 'Any'}:",
            code
        )
        
        return code
    
    def _convert_params(self, params: str) -> str:
        """Convert function parameters from TS to Python."""
        if not params.strip():
            return params
            
        param_list = []
        for param in params.split(','):
            param = param.strip()
            if ':' in param:
                # TypeScript typed parameter
                name, ts_type = param.split(':', 1)
                name = name.strip()
                ts_type = ts_type.strip()
                py_type = self._convert_type(ts_type)
                param_list.append(f"{name}: {py_type}")
            else:
                # Untyped parameter
                param_list.append(param)
                
        return ', '.join(param_list)
    
    def _convert_type(self, ts_type: str) -> str:
        """Convert TypeScript type to Python type hint."""
        if not ts_type:
            return 'Any'
            
        ts_type = ts_type.strip()
        
        # Handle union types
        if '|' in ts_type:
            types = [self._convert_type(t.strip()) for t in ts_type.split('|')]
            return f"Union[{', '.join(types)}]"
            
        # Check type map
        if ts_type in self.type_map:
            return self.type_map[ts_type]
            
        # Handle generic types
        if '<' in ts_type and '>' in ts_type:
            base_type = ts_type[:ts_type.index('<')]
            inner_type = ts_type[ts_type.index('<')+1:ts_type.rindex('>')]
            
            if base_type == 'Array':
                return f"List[{self._convert_type(inner_type)}]"
            elif base_type == 'Promise':
                return f"Awaitable[{self._convert_type(inner_type)}]"
            elif base_type == 'Record':
                # Record<K, V> -> Dict[K, V]
                key_value = inner_type.split(',', 1)
                if len(key_value) == 2:
                    return f"Dict[{self._convert_type(key_value[0])}, {self._convert_type(key_value[1])}]"
                    
        # Default to the type as-is (might be a custom class)
        return ts_type
    
    def _convert_classes(self, code: str) -> str:
        """Convert JS/TS class definitions to Python."""
        # Basic class definition
        code = re.sub(
            r'class\s+(\w+)\s*(?:extends\s+(\w+))?\s*\{',
            lambda m: f"class {m.group(1)}({m.group(2) if m.group(2) else 'object'}):",
            code
        )
        
        # Convert constructor
        code = re.sub(
            r'constructor\s*\(([^)]*)\)\s*\{',
            lambda m: f"def __init__(self, {m.group(1)}):",
            code
        )
        
        # Convert class methods (already handled by function conversion)
        
        return code
    
    def _convert_variables(self, code: str) -> str:
        """Convert variable declarations."""
        # Track renamed variables for later replacement
        self.renamed_vars = {}
        
        # Remove const, let, var
        code = re.sub(r'\b(const|let|var)\s+', '', code)
        
        # Convert typed variable declarations
        code = re.sub(
            r'(\w+)\s*:\s*([^=\n]+)\s*=',
            lambda m: self._handle_var_declaration(m.group(1), m.group(2), typed=True),
            code
        )
        
        # Handle untyped variable assignments that might conflict with built-ins
        # Don't match inside arrow functions or comparisons
        code = re.sub(
            r'\b(\w+)\s*=\s*(?!=|>)',
            lambda m: self._handle_var_declaration(m.group(1), None, typed=False),
            code
        )
        
        # Replace all usages of renamed variables
        for old_name, new_name in self.renamed_vars.items():
            # Special handling for cases like max = max(...)
            # First, temporarily mark the RHS to protect it
            code = re.sub(
                rf'\b{old_name}_var\s*=\s*{old_name}\(',
                f'{old_name}_var = {old_name}__PROTECTED__(',
                code
            )
            
            # Replace variable usage (not in assignments and not protected)
            code = re.sub(
                rf'\b{old_name}\b(?!\s*=)(?!__PROTECTED__)',
                new_name,
                code
            )
            
            # Restore protected names
            code = code.replace(f'{old_name}__PROTECTED__', old_name)
        
        return code
    
    def _handle_var_declaration(self, name: str, type_str: str, typed: bool) -> str:
        """Handle variable declaration and track renames."""
        safe_name = self._safe_var_name(name)
        if safe_name != name:
            self.renamed_vars[name] = safe_name
        
        if typed and type_str:
            return f"{safe_name}: {self._convert_type(type_str)} ="
        else:
            return f"{safe_name} = "
    
    def _safe_var_name(self, name: str) -> str:
        """Convert variable name to avoid conflicts with Python keywords/built-ins."""
        if name in self.python_keywords:
            return f"{name}_var"
        return name
    
    def _convert_control_structures(self, code: str) -> str:
        """Convert control structures."""
        # Convert for loops
        code = re.sub(
            r'for\s*\(\s*(?:const|let|var)?\s*(\w+)\s+of\s+([^)]+)\)\s*\{',
            r'for \1 in \2:',
            code
        )
        
        # Convert for-in loops
        code = re.sub(
            r'for\s*\(\s*(?:const|let|var)?\s*(\w+)\s+in\s+([^)]+)\)\s*\{',
            r'for \1 in \2:',
            code
        )
        
        # Convert traditional for loops (simplified)
        code = re.sub(
            r'for\s*\(\s*(?:let|var)?\s*(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*([^;]+)\s*;\s*\1\+\+\s*\)\s*\{',
            r'for \1 in range(\2, \3):',
            code
        )
        
        # Convert if statements
        code = re.sub(
            r'if\s*\(([^)]+)\)\s*\{',
            r'if \1:',
            code
        )
        
        # Convert else if
        code = re.sub(
            r'}\s*else\s+if\s*\(([^)]+)\)\s*\{',
            r'elif \1:',
            code
        )
        
        # Convert else
        code = re.sub(
            r'}\s*else\s*\{',
            r'else:',
            code
        )
        
        # Convert while loops
        code = re.sub(
            r'while\s*\(([^)]+)\)\s*\{',
            r'while \1:',
            code
        )
        
        # Convert try-catch
        code = re.sub(
            r'try\s*\{',
            r'try:',
            code
        )
        
        code = re.sub(
            r'}\s*catch\s*\((\w+)\)\s*\{',
            r'except Exception as \1:',
            code
        )
        
        # Convert switch to if-elif
        # This is a simplified version
        code = re.sub(
            r'switch\s*\(([^)]+)\)\s*\{',
            r'_switch_var = \1\nif False:  # switch',
            code
        )
        
        code = re.sub(
            r'case\s+([^:]+):',
            r'elif _switch_var == \1:',
            code
        )
        
        code = re.sub(
            r'default:',
            r'else:',
            code
        )
        
        return code
    
    def _convert_array_methods(self, code: str) -> str:
        """Convert common array methods."""
        # First normalize arrow functions to have consistent spacing
        code = re.sub(r'\s*=>\s*', ' => ', code)
        
        # Also handle cases where the semicolon might be present
        code = code.replace(';', '')
        
        # Handle .reduce() since it's more complex
        code = re.sub(
            r'(\w+)\.reduce\(\((\w+),\s*(\w+)\) => ([^,]+),\s*([^)]+)\)',
            r'functools.reduce(lambda \2, \3: \4, \1, \5)',
            code
        )
        
        # Convert .map() - handle both (x) => and x =>
        code = re.sub(
            r'(\w+)\.map\(\((\w+)\) => ([^)]+)\)',
            r'[\3 for \2 in \1]',
            code, flags=re.MULTILINE | re.DOTALL
        )
        code = re.sub(
            r'(\w+)\.map\((\w+) => ([^)]+)\)',
            r'[\3 for \2 in \1]',
            code, flags=re.MULTILINE | re.DOTALL
        )
        
        # Convert .filter() - handle both (x) => and x =>
        code = re.sub(
            r'(\w+)\.filter\(\((\w+)\) => ([^)]+)\)',
            r'[\2 for \2 in \1 if \3]',
            code, flags=re.MULTILINE | re.DOTALL
        )
        code = re.sub(
            r'(\w+)\.filter\((\w+) => ([^)]+)\)',
            r'[\2 for \2 in \1 if \3]',
            code, flags=re.MULTILINE | re.DOTALL
        )
        
        # Convert .forEach() - handle both (x) => and x =>
        code = re.sub(
            r'(\w+)\.forEach\(\((\w+)\) => \{',
            r'for \2 in \1:',
            code
        )
        code = re.sub(
            r'(\w+)\.forEach\((\w+) => \{',
            r'for \2 in \1:',
            code
        )
        
        # Convert .find() - handle both (x) => and x =>
        code = re.sub(
            r'(\w+)\.find\(\((\w+)\) => ([^)]+)\)',
            r'next((\2 for \2 in \1 if \3), None)',
            code
        )
        code = re.sub(
            r'(\w+)\.find\((\w+) => ([^)]+)\)',
            r'next((\2 for \2 in \1 if \3), None)',
            code
        )
        
        return code
    
    def _convert_objects(self, code: str) -> str:
        """Convert object literals to dictionaries."""
        # Convert return statements with object literals
        code = re.sub(
            r'return\s*\{([^}]+)\}',
            lambda m: f'return {self._convert_object_literal(m.group(1))}',
            code
        )
        
        # Convert object literal assignments
        code = re.sub(
            r'=\s*\{([^}]+)\}',
            lambda m: f'= {self._convert_object_literal(m.group(1))}',
            code
        )
        
        return code
    
    def _convert_object_literal(self, content: str) -> str:
        """Convert object literal content to dictionary."""
        # Split by commas but be careful about nested structures
        lines = content.strip().split('\n')
        pairs = []
        
        # Process each line
        for line in lines:
            line = line.strip()
            if not line or line == ',':
                continue
                
            # Remove trailing comma
            if line.endswith(','):
                line = line[:-1]
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Quote keys if they're not already quoted
                if not (key.startswith('"') or key.startswith("'")):
                    key = f'"{key}"'
                    
                # Use renamed variables if they exist (for values, not keys)
                if hasattr(self, 'renamed_vars') and value in self.renamed_vars:
                    value = self.renamed_vars[value]
                    
                pairs.append(f"{key}: {value}")
        
        return "{" + ", ".join(pairs) + "}"
    
    def _convert_common_methods(self, code: str) -> str:
        """Convert common JS/TS methods to Python equivalents."""
        # Convert spread operator first
        code = re.sub(
            r'\.\.\.(\w+)',
            r'*\1',
            code
        )
        
        # Convert array.length to len(array) BEFORE other replacements
        code = re.sub(
            r'(\w+)\.length\b',
            r'len(\1)',
            code
        )
        
        # Replace methods but be careful not to replace variable names
        for js_method, py_method in self.method_map.items():
            # Skip if it's already been modified (e.g., Math.max_var)
            if not re.search(rf'\b{re.escape(js_method)}_var\b', code):
                code = re.sub(rf'\b{re.escape(js_method)}\b', py_method, code)
        
        # Convert string methods
        code = re.sub(
            r'(\w+)\.toLowerCase\(\)',
            r'\1.lower()',
            code
        )
        
        code = re.sub(
            r'(\w+)\.toUpperCase\(\)',
            r'\1.upper()',
            code
        )
        
        # Convert undefined/null checks
        code = re.sub(
            r'(\w+)\s*===\s*undefined',
            r'\1 is None',
            code
        )
        
        code = re.sub(
            r'(\w+)\s*===\s*null',
            r'\1 is None',
            code
        )
        
        code = re.sub(
            r'(\w+)\s*!==\s*undefined',
            r'\1 is not None',
            code
        )
        
        code = re.sub(
            r'(\w+)\s*!==\s*null',
            r'\1 is not None',
            code
        )
        
        return code
    
    def _convert_operators(self, code: str) -> str:
        """Convert JS/TS operators to Python."""
        # Convert === and !== to == and !=
        code = code.replace('===', '==')
        code = code.replace('!==', '!=')
        
        # Convert && and || to and/or
        code = code.replace('&&', 'and')
        code = code.replace('||', 'or')
        
        # Convert ! to not (when standalone)
        code = re.sub(r'!\s*(\w+)', r'not \1', code)
        
        # Convert ++ and --
        code = re.sub(r'(\w+)\+\+', r'\1 += 1', code)
        code = re.sub(r'(\w+)--', r'\1 -= 1', code)
        
        # Convert template literals (simplified)
        code = re.sub(
            r'`([^`]*)\$\{([^}]+)\}([^`]*)`',
            r'f"\1{\2}\3"',
            code
        )
        
        # Convert remaining template literals
        code = re.sub(r'`([^`]*)`', r'"\1"', code)
        
        return code
    
    def _cleanup_code(self, code: str) -> str:
        """Clean up the converted code."""
        # Convert JS comments that weren't handled
        code = re.sub(r'//\s*(.*)', r'# \1', code)
        
        # Remove remaining braces (but preserve dictionary braces)
        # Only remove standalone braces on their own lines
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            # Don't remove braces from lines that appear to be dictionaries
            if ('return' in line and '{' in line) or (':' in line and '{' in line):
                processed_lines.append(line)
            else:
                # Remove standalone braces
                if line.strip() == '{' or line.strip() == '}':
                    continue
                line = line.replace('{', '')
                line = line.replace('}', '')
                processed_lines.append(line)
        
        code = '\n'.join(processed_lines)
        
        # Remove semicolons
        code = code.replace(';', '')
        
        # Fix missing colons in if/for/while statements
        code = re.sub(r'(if|for|while)\s+(.+)\s*\n', r'\1 \2:\n', code)
        
        # Fix indentation (simplified - assumes 4 spaces)
        lines = code.split('\n')
        cleaned_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append('')
                continue
                
            # Check if we need to decrease indent BEFORE adding the line
            if stripped.startswith(('elif', 'else', 'except', 'finally')):
                indent_level = max(0, indent_level - 1)
                
            # Handle indent placeholder
            if '__INDENT__' in stripped:
                # This is our indent marker, remove it and increase indent
                continue
                
            # Add indented line
            cleaned_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after colons that aren't in strings or comments
            if stripped.endswith(':') and not (stripped.endswith('":') or stripped.endswith("':") or stripped.startswith('#')):
                indent_level += 1
            # Keep proper indentation after returns that aren't the end of a function
                
        return '\n'.join(cleaned_lines)
    
    def _post_process(self, python_code: str) -> str:
        """Additional post-processing steps to fix common conversion issues."""
        # Fix JavaScript-style comments that weren't converted
        python_code = re.sub(r'//\s*(.*)', r'# \1', python_code)
        
        # Fix missing colons in if/for/while statements
        python_code = re.sub(r'(if|for|while)\s+([^:]+)\s*(?<!\:)$', r'\1 \2:', python_code, flags=re.MULTILINE)
        
        # Add missing pass statement to empty blocks
        python_code = re.sub(r'(\w+):\s*\n\s*\n', r'\1:\n    pass\n\n', python_code)
        
        # Fix indentation issues with return statements
        lines = python_code.split('\n')
        for i in range(len(lines)-1):
            if lines[i].strip().startswith('return ') and not lines[i+1].strip().startswith(('elif', 'else', 'except', 'finally')):
                # Make sure there's no indent change after return unless it's followed by control flow
                if i < len(lines)-2 and lines[i+1].strip() and not lines[i+1].startswith(' '):
                    indent_level = len(lines[i]) - len(lines[i].lstrip())
                    lines[i+1] = ' ' * indent_level + lines[i+1].lstrip()
        
        return '\n'.join(lines)
    
    def _generate_imports(self, code: str) -> str:
        """Generate necessary Python imports based on the converted code."""
        imports = []
        
        # Check for type hints
        if any(hint in code for hint in ['List[', 'Dict[', 'Any', 'Union[', 'Optional[', 'Awaitable[']):
            imports.append("from typing import List, Dict, Any, Union, Optional, Awaitable")
            
        # Check for async
        if 'async def' in code or 'await' in code:
            imports.append("import asyncio")
            
        # Check for math functions
        if 'math.' in code:
            imports.append("import math")
            
        # Check for random
        if 'random.' in code:
            imports.append("import random")
            
        # Check for json
        if 'json.' in code:
            imports.append("import json")
            
        # Check for functools (for reduce)
        if 'functools.reduce' in code:
            imports.append("import functools")
            
        return '\n'.join(imports)


# Helper function for easy conversion
def js_to_python(js_code: str) -> str:
    """Convert JavaScript/TypeScript code to Python."""
    converter = JSPythonConverter()
    return converter.convert(js_code)